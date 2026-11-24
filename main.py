import io
import os
import random
from PIL import Image as PILImage, ImageDraw, ImageFont

from kivy.app import App
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.core.window import Window
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView

# Color de fondo global (#1E293B)
Window.clearcolor = (0.118, 0.161, 0.231, 1)


def hex_to_rgba(hex_color, alpha=1.0):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return (r, g, b, alpha)


class TarjetaNivel(ButtonBehavior, BoxLayout):
    """Tarjeta táctil con borde redondeado para el menú principal."""

    def __init__(self, bg_hex, border_hex, **kwargs):
        super().__init__(orientation="vertical", padding=dp(8), spacing=dp(4), **kwargs)
        self.bg_rgba = hex_to_rgba(bg_hex)
        self.border_rgba = hex_to_rgba(border_hex)
        with self.canvas.before:
            Color(*self.bg_rgba)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
            Color(*self.border_rgba)
            self.line = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, dp(10)),
                width=dp(1.5),
            )
        self.bind(pos=self._actualizar_canvas, size=self._actualizar_canvas)

    def _actualizar_canvas(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.line.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(10))


class PantallaMenu(Screen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.app = app_ref

    def on_pre_enter(self, *args):
        self.clear_widgets()
        raiz = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))

        # Cabecera con cabecera.png
        ruta_cab = self.app.buscar_imagen(self.app.ruta_ppal, "cabecera")
        if ruta_cab:
            img_cab = Image(
                source=ruta_cab,
                size_hint_y=0.20,
                allow_stretch=True,
                keep_ratio=True,
            )
            raiz.add_widget(img_cab)
        else:
            lbl_titulo = Label(
                text="[b]APRENDE ALGORITMOS JUGANDO[/b]\n[size=14sp]Toca un nivel disponible para comenzar[/size]",
                markup=True,
                font_size=dp(20),
                color=hex_to_rgba("#38BDF8"),
                halign="center",
                size_hint_y=0.18,
            )
            raiz.add_widget(lbl_titulo)

        # Cuadrícula de 5 niveles (responsive: 2 o 3 columnas según orientación)
        cols = 3 if Window.width >= Window.height else 2
        grid = GridLayout(cols=cols, spacing=dp(10), size_hint_y=0.80)

        niveles = [
            {
                "num": 1,
                "titulo": "NIVEL 1\nHacer Limonada",
                "estado": "DISPONIBLE",
                "img": "limonadappal",
                "disponible": True,
                "borde": "#22C55E",
                "color_est": "#4ADE80",
            },
            {
                "num": 2,
                "titulo": "NIVEL 2\nPreparar Sándwich",
                "estado": "DISPONIBLE",
                "img": "sandwichppal",
                "disponible": True,
                "borde": "#22C55E",
                "color_est": "#4ADE80",
            },
            {
                "num": 3,
                "titulo": "NIVEL 3\nReto Intermedio",
                "estado": "EN CONSTRUCCIÓN",
                "img": "robotppal",
                "disponible": False,
                "borde": "#F59E0B",
                "color_est": "#FACC15",
            },
            {
                "num": 4,
                "titulo": "NIVEL 4\nReto Avanzado",
                "estado": "EN CONSTRUCCIÓN",
                "img": "susi1ppal",
                "disponible": False,
                "borde": "#64748B",
                "color_est": "#FACC15",
            },
            {
                "num": 5,
                "titulo": "NIVEL 5\nDesafío Maestro",
                "estado": "EN CONSTRUCCIÓN",
                "img": "personaje_rojoppal",
                "disponible": False,
                "borde": "#64748B",
                "color_est": "#FACC15",
            },
        ]

        for info in niveles:
            bg = "#0F172A" if info["disponible"] else "#162032"
            tarjeta = TarjetaNivel(bg_hex=bg, border_hex=info["borde"])

            lbl_t = Label(
                text=info["titulo"],
                font_size=dp(13),
                bold=True,
                halign="center",
                color=(1, 1, 1, 1) if info["disponible"] else hex_to_rgba("#CBD5E1"),
                size_hint_y=0.28,
            )
            lbl_t.bind(size=lbl_t.setter("text_size"))
            tarjeta.add_widget(lbl_t)

            ruta_img = self.app.buscar_imagen(self.app.ruta_ppal, info["img"])
            if ruta_img:
                tarjeta.add_widget(
                    Image(
                        source=ruta_img,
                        allow_stretch=True,
                        keep_ratio=True,
                        size_hint_y=0.52,
                    )
                )
            else:
                tarjeta.add_widget(
                    Label(
                        text=f"[{info['img']}.png]",
                        font_size=dp(11),
                        color=hex_to_rgba("#F87171"),
                        size_hint_y=0.52,
                    )
                )

            lbl_e = Label(
                text=info["estado"],
                font_size=dp(11),
                bold=True,
                color=hex_to_rgba(info["color_est"]),
                size_hint_y=0.20,
            )
            tarjeta.add_widget(lbl_e)

            if info["disponible"]:
                tarjeta.bind(
                    on_release=lambda btn, n=info["num"]: self.app.abrir_nivel(n)
                )
            else:
                tarjeta.bind(
                    on_release=lambda btn, n=info["num"]: self.app.mostrar_popup(
                        f"Nivel {n} - En construcción",
                        f"El Nivel {n} aún está en construcción.\nPor ahora puedes jugar el Nivel 1 y el Nivel 2.",
                    )
                )

            grid.add_widget(tarjeta)

        raiz.add_widget(grid)
        self.add_widget(raiz)


class PantallaNivel(Screen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.app = app_ref
        self.nivel_actual = 1
        self.algoritmo_usuario = []
        self.pasos_simulacion = []
        self.indice_sim = 0
        self.puntaje_final = 0
        self.ejecutando = False
        self.evento_sim = None
        self.max_intentos = 3
        self.intentos_usados = 0
        self.penalizacion_acumulada = 0
        self.nivel_finalizado = False
        self.indice_seleccionado = None

    def cargar_nivel(self, num_nivel):
        if self.evento_sim:
            self.evento_sim.cancel()
            self.evento_sim = None

        self.nivel_actual = num_nivel
        self.algoritmo_usuario = []
        self.pasos_simulacion = []
        self.indice_sim = 0
        self.puntaje_final = 0
        self.ejecutando = False
        self.intentos_usados = 0
        self.penalizacion_acumulada = 0
        self.nivel_finalizado = False
        self.indice_seleccionado = None

        if num_nivel == 1:
            self.titulo_nivel = "Nivel 1: Hacer Limonada"
            self.carpeta_nivel = self.app.ruta_limonada
            self.imagen_portada = "limonada"
            self.respaldo_portada = None
            self.instrucciones_disponibles = [
                "Tomar un vaso vacío y limpio",
                "Cortar un limón por la mitad",
                "Exprimir el jugo del limón dentro del vaso",
                "Agregar agua al vaso",
                "Añadir azúcar al gusto",
                "Revolver la mezcla con una cuchara",
                "Beber la limonada",
                "Agregar sal",
                "Lavar el vaso",
            ]
        else:
            self.titulo_nivel = "Nivel 2: Preparar un Sándwich"
            self.carpeta_nivel = self.app.ruta_sandwich
            self.imagen_portada = "sandwich_listo"
            self.respaldo_portada = "sandwich_cerrado"
            self.instrucciones_disponibles = [
                "Tomar un plato limpio y colocarlo en la mesa",
                "Tomar dos rebanadas de pan y ponerlas en el plato",
                "Abrir el frasco de mantequilla",
                "Untar mantequilla en el pan con un cuchillo",
                "Colocar una rebanada de jamón sobre el pan",
                "Colocar una rebanada de queso sobre el jamón",
                "Cerrar el sándwich con la otra rebanada de pan",
                "Tostar el sándwich en la sandwichera",
                "Comer el sándwich tostado",
                "Poner cáscara de plátano en el pan",
                "Meter el plato de metal en el microondas",
                "Guardar el pan en la nevera",
            ]

        self.construir_ui()
        self.cargar_instrucciones_disponibles()
        self.actualizar_estadisticas()
        self.mostrar_imagen(
            self.imagen_portada,
            f"¡Bienvenido al {self.titulo_nivel}! Tienes 3 oportunidades. Arma tu algoritmo y toca EJECUTAR.",
            respaldo=self.respaldo_portada,
        )

    def construir_ui(self):
        self.clear_widgets()
        raiz = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(6))

        # --- BARRA SUPERIOR DE ESTADO ---
        barra_top = BoxLayout(size_hint_y=0.07, spacing=dp(6))
        self.lbl_titulo_top = Label(
            text=self.titulo_nivel,
            bold=True,
            font_size=dp(14),
            color=hex_to_rgba("#FACC15"),
            halign="left",
        )
        self.lbl_titulo_top.bind(size=self.lbl_titulo_top.setter("text_size"))

        self.lbl_stats_top = Label(
            text="Intentos: 0/3 | Puntos: --/20",
            bold=True,
            font_size=dp(12),
            color=hex_to_rgba("#38BDF8"),
            halign="right",
        )
        self.lbl_stats_top.bind(size=self.lbl_stats_top.setter("text_size"))

        btn_salir = Button(
            text="Salir",
            size_hint_x=0.22,
            background_normal="",
            background_color=hex_to_rgba("#B91C1C"),
            bold=True,
            font_size=dp(12),
            on_release=lambda *a: self.salir_al_menu(),
        )
        barra_top.add_widget(self.lbl_titulo_top)
        barra_top.add_widget(self.lbl_stats_top)
        barra_top.add_widget(btn_salir)
        raiz.add_widget(barra_top)

        # --- ÁREA DE SIMULACIÓN VISUAL ---
        box_sim = BoxLayout(orientation="vertical", size_hint_y=0.34, spacing=dp(4))
        self.img_sim = Image(allow_stretch=True, keep_ratio=True, size_hint_y=0.78)
        self.lbl_estado = Label(
            text="",
            font_size=dp(12),
            bold=True,
            halign="center",
            valign="middle",
            color=(1, 1, 1, 1),
            size_hint_y=0.22,
        )
        self.lbl_estado.bind(size=self.lbl_estado.setter("text_size"))
        box_sim.add_widget(self.img_sim)
        box_sim.add_widget(self.lbl_estado)
        raiz.add_widget(box_sim)

        # --- ZONA MEDIA: INSTRUCCIONES (IZQ) Y TU ALGORITMO (DER) ---
        zona_media = BoxLayout(orientation="horizontal", size_hint_y=0.49, spacing=dp(8))

        # Columna Izquierda: Instrucciones disponibles
        col_izq = BoxLayout(orientation="vertical", spacing=dp(4))
        header_izq = BoxLayout(size_hint_y=0.14, spacing=dp(4))
        header_izq.add_widget(
            Label(
                text="INSTRUCCIONES",
                bold=True,
                font_size=dp(12),
                color=hex_to_rgba("#38BDF8"),
            )
        )
        header_izq.add_widget(
            Button(
                text="Mezclar",
                size_hint_x=0.45,
                background_normal="",
                background_color=hex_to_rgba("#334155"),
                font_size=dp(11),
                bold=True,
                on_release=lambda *a: self.cargar_instrucciones_disponibles(),
            )
        )
        col_izq.add_widget(header_izq)

        scroll_izq = ScrollView(size_hint_y=0.86)
        self.lista_disponibles = GridLayout(cols=1, spacing=dp(4), size_hint_y=None)
        self.lista_disponibles.bind(
            minimum_height=self.lista_disponibles.setter("height")
        )
        scroll_izq.add_widget(self.lista_disponibles)
        col_izq.add_widget(scroll_izq)

        # Columna Derecha: Algoritmo armado
        col_der = BoxLayout(orientation="vertical", spacing=dp(4))
        col_der.add_widget(
            Label(
                text="TU ALGORITMO (Toca un paso)",
                bold=True,
                font_size=dp(12),
                color=hex_to_rgba("#4ADE80"),
                size_hint_y=0.14,
            )
        )
        scroll_der = ScrollView(size_hint_y=0.86)
        self.lista_algoritmo_ui = GridLayout(cols=1, spacing=dp(4), size_hint_y=None)
        self.lista_algoritmo_ui.bind(
            minimum_height=self.lista_algoritmo_ui.setter("height")
        )
        scroll_der.add_widget(self.lista_algoritmo_ui)
        col_der.add_widget(scroll_der)

        zona_media.add_widget(col_izq)
        zona_media.add_widget(col_der)
        raiz.add_widget(zona_media)

        # --- BARRA INFERIOR DE CONTROLES TÁCTILES ---
        barra_bot = BoxLayout(size_hint_y=0.10, spacing=dp(5))
        botones_ctrl = [
            ("Subir", "#334155", self.subir_paso),
            ("Bajar", "#334155", self.bajar_paso),
            ("Quitar", "#991B1B", self.quitar_paso),
            ("Limpiar", "#475569", self.limpiar_algoritmo),
            ("Reiniciar", "#0284C7", lambda: self.cargar_nivel(self.nivel_actual)),
        ]
        for texto, color_hex, accion in botones_ctrl:
            barra_bot.add_widget(
                Button(
                    text=texto,
                    background_normal="",
                    background_color=hex_to_rgba(color_hex),
                    font_size=dp(11),
                    bold=True,
                    on_release=lambda btn, fn=accion: fn(),
                )
            )

        self.btn_ejecutar = Button(
            text="EJECUTAR",
            size_hint_x=1.4,
            background_normal="",
            background_color=hex_to_rgba("#16A34A"),
            font_size=dp(13),
            bold=True,
            on_release=lambda *a: self.iniciar_evaluacion(),
        )
        barra_bot.add_widget(self.btn_ejecutar)
        raiz.add_widget(barra_bot)

        self.add_widget(raiz)

    def actualizar_estadisticas(self, puntos_mostrados=None):
        restantes = max(0, self.max_intentos - self.intentos_usados)
        pts_txt = f"{puntos_mostrados}/20" if puntos_mostrados is not None else "--/20"
        self.lbl_stats_top.text = (
            f"Ejecuciones: {self.intentos_usados}/{self.max_intentos} "
            f"(Restan: {restantes}) | Pts: {pts_txt}"
        )

    def cargar_instrucciones_disponibles(self):
        self.lista_disponibles.clear_widgets()
        mezcladas = self.instrucciones_disponibles.copy()
        random.shuffle(mezcladas)

        for texto in mezcladas:
            btn = Button(
                text=f"+ {texto}",
                size_hint_y=None,
                height=dp(42),
                background_normal="",
                background_color=hex_to_rgba("#0F172A"),
                color=hex_to_rgba("#E2E8F0"),
                font_size=dp(11),
                halign="left",
                valign="middle",
                padding=(dp(8), dp(4)),
            )
            btn.bind(size=btn.setter("text_size"))
            btn.bind(on_release=lambda b, t=texto: self.agregar_paso(t))
            self.lista_disponibles.add_widget(btn)

    def refrescar_lista_algoritmo(self, indice_activo=None):
        self.lista_algoritmo_ui.clear_widgets()
        for idx, paso in enumerate(self.algoritmo_usuario):
            es_sel = idx == self.indice_seleccionado or idx == indice_activo
            bg = "#2563EB" if es_sel else "#1E293B"
            btn = Button(
                text=f"{idx + 1}. {paso}",
                size_hint_y=None,
                height=dp(42),
                background_normal="",
                background_color=hex_to_rgba(bg),
                color=(1, 1, 1, 1),
                font_size=dp(11),
                halign="left",
                valign="middle",
                padding=(dp(8), dp(4)),
            )
            btn.bind(size=btn.setter("text_size"))
            btn.bind(on_release=lambda b, i=idx: self.seleccionar_paso(i))
            self.lista_algoritmo_ui.add_widget(btn)

    def seleccionar_paso(self, idx):
        if self.ejecutando:
            return
        self.indice_seleccionado = idx
        self.refrescar_lista_algoritmo()

    def agregar_paso(self, texto):
        if self.ejecutando or self.nivel_finalizado:
            return
        self.algoritmo_usuario.append(texto)
        self.indice_seleccionado = len(self.algoritmo_usuario) - 1
        self.refrescar_lista_algoritmo()

    def subir_paso(self):
        idx = self.indice_seleccionado
        if idx is None or idx <= 0 or self.ejecutando or self.nivel_finalizado:
            return
        self.algoritmo_usuario[idx], self.algoritmo_usuario[idx - 1] = (
            self.algoritmo_usuario[idx - 1],
            self.algoritmo_usuario[idx],
        )
        self.indice_seleccionado = idx - 1
        self.refrescar_lista_algoritmo()

    def bajar_paso(self):
        idx = self.indice_seleccionado
        if (
            idx is None
            or idx >= len(self.algoritmo_usuario) - 1
            or self.ejecutando
            or self.nivel_finalizado
        ):
            return
        self.algoritmo_usuario[idx], self.algoritmo_usuario[idx + 1] = (
            self.algoritmo_usuario[idx + 1],
            self.algoritmo_usuario[idx],
        )
        self.indice_seleccionado = idx + 1
        self.refrescar_lista_algoritmo()

    def quitar_paso(self):
        idx = self.indice_seleccionado
        if idx is None or self.ejecutando or self.nivel_finalizado:
            return
        self.algoritmo_usuario.pop(idx)
        self.indice_seleccionado = None
        self.refrescar_lista_algoritmo()

    def limpiar_algoritmo(self):
        if self.ejecutando or self.nivel_finalizado:
            return
        self.algoritmo_usuario.clear()
        self.indice_seleccionado = None
        self.refrescar_lista_algoritmo()
        self.mostrar_imagen(
            self.imagen_portada,
            "Lista limpiada. Ajusta tu algoritmo y vuelve a ejecutar.",
            respaldo=self.respaldo_portada,
        )

    def salir_al_menu(self):
        if self.evento_sim:
            self.evento_sim.cancel()
            self.evento_sim = None
        self.ejecutando = False
        self.app.sm.current = "menu"

    # --- RENDERIZADO DE IMÁGENES Y PUNTAJE CON PILLOW ---
    def _cargar_fuente_pil(self, tamano):
        rutas_fuentes = [
            "/system/fonts/Roboto-Bold.ttf",
            "/system/fonts/DroidSans-Bold.ttf",
            "arialbd.ttf",
            "DejaVuSans-Bold.ttf",
        ]
        for f in rutas_fuentes:
            try:
                return ImageFont.truetype(f, tamano)
            except OSError:
                continue
        return ImageFont.load_default()

    def mostrar_imagen(
        self, nombre_base, texto_estado, respaldo=None, puntaje_superpuesto=None
    ):
        self.lbl_estado.text = texto_estado
        ruta = self.app.buscar_imagen(self.carpeta_nivel, nombre_base)
        if not ruta and respaldo:
            ruta = self.app.buscar_imagen(self.carpeta_nivel, respaldo)

        if not ruta:
            return

        if puntaje_superpuesto is None:
            self.img_sim.texture = None
            self.img_sim.source = ruta
            self.img_sim.reload()
        else:
            img = PILImage.open(ruta).convert("RGBA")
            draw = ImageDraw.Draw(img)
            w, h = img.size
            texto_pts = f"{puntaje_superpuesto} PTS"
            subtexto = "TOTAL ACUMULADO"

            if nombre_base == "completada":
                cx, cy = int(w * 0.50), int(h * 0.62)
                color_principal = (22, 163, 74, 255)
            else:
                cx, cy = int(w * 0.50), int(h * 0.43)
                color_principal = (220, 38, 38, 255)

            fuente_g = self._cargar_fuente_pil(max(22, int(h * 0.13)))
            fuente_p = self._cargar_fuente_pil(max(12, int(h * 0.05)))

            bbox_g = draw.textbbox((0, 0), texto_pts, font=fuente_g)
            tw_g, th_g = bbox_g[2] - bbox_g[0], bbox_g[3] - bbox_g[1]
            bbox_p = draw.textbbox((0, 0), subtexto, font=fuente_p)
            tw_p = bbox_p[2] - bbox_p[0]

            for dx in (-2, -1, 0, 1, 2):
                for dy in (-2, -1, 0, 1, 2):
                    draw.text(
                        (cx - tw_g // 2 + dx, cy - th_g // 2 + dy),
                        texto_pts,
                        font=fuente_g,
                        fill=(255, 255, 255, 255),
                    )
                    draw.text(
                        (cx - tw_p // 2 + dx, cy + th_g // 2 + 4 + dy),
                        subtexto,
                        font=fuente_p,
                        fill=(255, 255, 255, 255),
                    )

            draw.text(
                (cx - tw_g // 2, cy - th_g // 2),
                texto_pts,
                font=fuente_g,
                fill=color_principal,
            )
            draw.text(
                (cx - tw_p // 2, cy + th_g // 2 + 4),
                subtexto,
                font=fuente_p,
                fill=(30, 41, 59, 255),
            )

            buffer = io.BytesIO()
            img.save(buffer, format="png")
            buffer.seek(0)
            self.img_sim.texture = CoreImage(buffer, ext="png").texture

    # --- EVALUACIÓN DE ALGORITMOS ---
    def iniciar_evaluacion(self):
        if self.ejecutando:
            return

        if self.nivel_finalizado or self.intentos_usados >= self.max_intentos:
            self.app.mostrar_popup(
                "Sin oportunidades",
                "Alcanzaste el límite de 3 ejecuciones o finalizaste el nivel.\nToca 'Reiniciar' o 'Salir'.",
            )
            return

        if not self.algoritmo_usuario:
            self.app.mostrar_popup(
                "Algoritmo vacío",
                "Agrega al menos una instrucción antes de ejecutar.",
            )
            return

        self.intentos_usados += 1
        self.penalizacion_acumulada = max(0, (self.intentos_usados - 1) * 5)
        self.actualizar_estadisticas()

        self.ejecutando = True
        self.btn_ejecutar.disabled = True
        self.btn_ejecutar.background_color = hex_to_rgba("#475569")
        self.pasos_simulacion = []

        if self.nivel_actual == 1:
            puntos_brutos, ok = self.evaluar_nivel_1()
        else:
            puntos_brutos, ok = self.evaluar_nivel_2()

        self.puntaje_final = max(0, min(20, puntos_brutos - self.penalizacion_acumulada))
        self.algoritmo_completado_ok = ok
        self.indice_sim = 0
        self.reproducir_paso()

    def evaluar_nivel_1(self):
        tiene_vaso = limon_cortado = tiene_jugo = tiene_agua = False
        tiene_azucar = mezclado = bebido = error_fatal = False
        puntos = 0

        for idx, instruccion in enumerate(self.algoritmo_usuario):
            if instruccion == "Tomar un vaso vacío y limpio":
                if not tiene_vaso:
                    tiene_vaso = True
                    puntos += 3
                    self.pasos_simulacion.append((idx, "vaso_vacio", "Paso válido: Vaso vacío y limpio listo (+3 pts)", None))
                else:
                    self.pasos_simulacion.append((idx, "vaso_vacio", "Ya tienes un vaso limpio en la mesa.", None))
            elif instruccion == "Cortar un limón por la mitad":
                if not limon_cortado:
                    limon_cortado = True
                    puntos += 2
                    self.pasos_simulacion.append((idx, "limon_cortado", "Paso válido: Limón cortado por la mitad (+2 pts)", None))
                else:
                    self.pasos_simulacion.append((idx, "limon_cortado", "El limón ya estaba cortado.", None))
            elif instruccion == "Exprimir el jugo del limón dentro del vaso":
                if not tiene_vaso:
                    self.pasos_simulacion.append((idx, "error_sin_vaso", "ERROR: Exprimiste el limón en la mesa sin vaso.", None))
                    error_fatal = True
                    break
                elif not limon_cortado:
                    self.pasos_simulacion.append((idx, "error_mezcla", "ERROR: No puedes exprimir un limón sin cortarlo.", None))
                    error_fatal = True
                    break
                else:
                    if not tiene_jugo:
                        tiene_jugo = True
                        puntos += 3
                    self.pasos_simulacion.append((idx, "jugo_en_vaso", "Paso válido: Jugo de limón en el vaso (+3 pts)", None))
            elif instruccion == "Agregar agua al vaso":
                if not tiene_vaso:
                    self.pasos_simulacion.append((idx, "error_sin_vaso", "ERROR: Derramaste el agua en la mesa sin vaso.", None))
                    error_fatal = True
                    break
                else:
                    if not tiene_agua:
                        tiene_agua = True
                        puntos += 3
                    self.pasos_simulacion.append((idx, "agua_anadida", "Paso válido: Agua añadida al vaso (+3 pts)", None))
            elif instruccion == "Añadir azúcar al gusto":
                if not tiene_vaso:
                    self.pasos_simulacion.append((idx, "error_sin_vaso", "ERROR: Tiraste el azúcar sobre la mesa sin vaso.", None))
                    error_fatal = True
                    break
                else:
                    if not tiene_azucar:
                        tiene_azucar = True
                        puntos += 3
                    self.pasos_simulacion.append((idx, "azucar_anadida", "Paso válido: Azúcar añadida al vaso (+3 pts)", None))
            elif instruccion == "Revolver la mezcla con una cuchara":
                if not tiene_vaso:
                    self.pasos_simulacion.append((idx, "error_sin_vaso", "ERROR: No hay vaso donde revolver.", None))
                    error_fatal = True
                    break
                elif not (tiene_jugo and tiene_agua and tiene_azucar):
                    self.pasos_simulacion.append((idx, "error_mezcla", "ERROR: Faltan ingredientes antes de revolver.", None))
                    error_fatal = True
                    break
                else:
                    if not mezclado:
                        mezclado = True
                        puntos += 3
                    self.pasos_simulacion.append((idx, "revolviendo", "Paso válido: Mezclando ingredientes (+3 pts)", None))
            elif instruccion == "Beber la limonada":
                if not tiene_vaso:
                    self.pasos_simulacion.append((idx, "error_sin_vaso", "ERROR: No tienes vaso para beber.", None))
                    error_fatal = True
                    break
                elif not mezclado:
                    self.pasos_simulacion.append((idx, "error_mezcla", "ERROR: La limonada no está mezclada.", None))
                    error_fatal = True
                    break
                elif idx != len(self.algoritmo_usuario) - 1:
                    self.pasos_simulacion.append((idx, "error_mezcla", "ERROR: Bebiste antes de terminar el algoritmo.", None))
                    error_fatal = True
                    break
                else:
                    bebido = True
                    puntos += 3
                    self.pasos_simulacion.append((idx, "bebiendo", "Paso válido: Bebiendo la limonada (+3 pts)", None))
            elif instruccion == "Agregar sal":
                puntos = max(0, puntos - 5)
                self.pasos_simulacion.append((idx, "error_sal", "ERROR GRAVE: Le pusiste sal a la limonada (-5 pts)", None))
                error_fatal = True
                break
            elif instruccion == "Lavar el vaso":
                if tiene_jugo or tiene_agua or tiene_azucar:
                    puntos = max(0, puntos - 4)
                    self.pasos_simulacion.append((idx, "error_mezcla", "ERROR: Lavaste el vaso y botaste los ingredientes (-4 pts)", None))
                    error_fatal = True
                    break
                else:
                    puntos = max(0, puntos - 2)
                    self.pasos_simulacion.append((idx, "vaso_vacio", "Paso innecesario: El vaso ya estaba limpio (-2 pts)", None))

        return puntos, (not error_fatal and bebido)

    def evaluar_nivel_2(self):
        tiene_plato = tiene_pan = frasco_abierto = tiene_mantequilla = False
        tiene_jamon = tiene_queso = sandwich_cerrado = tostado = False
        comido = error_fatal = False
        puntos = 0

        for idx, instruccion in enumerate(self.algoritmo_usuario):
            if instruccion == "Tomar un plato limpio y colocarlo en la mesa":
                if not tiene_plato:
                    tiene_plato = True
                    puntos += 2
                    self.pasos_simulacion.append((idx, "plato_vacio", "Paso válido: Plato limpio sobre la mesa (+2 pts)", None))
                else:
                    self.pasos_simulacion.append((idx, "plato_vacio", "Ya tienes un plato limpio en la mesa.", None))
            elif instruccion == "Tomar dos rebanadas de pan y ponerlas en el plato":
                if not tiene_plato:
                    self.pasos_simulacion.append((idx, "error_sin_plato", "ERROR: Pusiste el pan sin plato.", None))
                    error_fatal = True
                    break
                else:
                    if not tiene_pan:
                        tiene_pan = True
                        puntos += 2
                    self.pasos_simulacion.append((idx, "pan_en_plato", "Paso válido: Rebanadas de pan en el plato (+2 pts)", None))
            elif instruccion == "Abrir el frasco de mantequilla":
                if not frasco_abierto:
                    frasco_abierto = True
                    puntos += 2
                    self.pasos_simulacion.append((idx, "frasco_abierto", "Paso válido: Frasco destapado (+2 pts)", None))
                else:
                    self.pasos_simulacion.append((idx, "frasco_abierto", "El frasco ya estaba abierto.", None))
            elif instruccion == "Untar mantequilla en el pan con un cuchillo":
                if not tiene_pan:
                    self.pasos_simulacion.append((idx, "error_sin_plato", "ERROR: No hay pan donde untar.", None))
                    error_fatal = True
                    break
                elif not frasco_abierto:
                    self.pasos_simulacion.append((idx, "error_frasco_cerrado", "ERROR: El frasco de mantequilla está cerrado.", None))
                    error_fatal = True
                    break
                elif sandwich_cerrado:
                    self.pasos_simulacion.append((idx, "sandwich_cerrado", "ERROR: El sándwich ya está cerrado.", None))
                    error_fatal = True
                    break
                else:
                    if not tiene_mantequilla:
                        tiene_mantequilla = True
                        puntos += 2
                    self.pasos_simulacion.append((idx, "pan_con_mantequilla", "Paso válido: Mantequilla untada (+2 pts)", None))
            elif instruccion == "Colocar una rebanada de jamón sobre el pan":
                if not tiene_pan:
                    self.pasos_simulacion.append((idx, "error_sin_plato", "ERROR: No hay pan para poner el jamón.", None))
                    error_fatal = True
                    break
                elif sandwich_cerrado:
                    self.pasos_simulacion.append((idx, "sandwich_cerrado", "ERROR: El sándwich ya está cerrado.", None))
                    error_fatal = True
                    break
                else:
                    if not tiene_jamon:
                        tiene_jamon = True
                        puntos += 2
                    self.pasos_simulacion.append((idx, "sandwich_jamon", "Paso válido: Jamón colocado (+2 pts)", None))
            elif instruccion == "Colocar una rebanada de queso sobre el jamón":
                if not tiene_pan:
                    self.pasos_simulacion.append((idx, "error_sin_plato", "ERROR: No hay pan para poner el queso.", None))
                    error_fatal = True
                    break
                elif not tiene_jamon:
                    self.pasos_simulacion.append((idx, "sandwich_queso", "ERROR: Coloca el jamón antes del queso.", None))
                    error_fatal = True
                    break
                elif sandwich_cerrado:
                    self.pasos_simulacion.append((idx, "sandwich_cerrado", "ERROR: El sándwich ya está cerrado.", None))
                    error_fatal = True
                    break
                else:
                    if not tiene_queso:
                        tiene_queso = True
                        puntos += 2
                    self.pasos_simulacion.append((idx, "sandwich_queso", "Paso válido: Queso añadido (+2 pts)", None))
            elif instruccion == "Cerrar el sándwich con la otra rebanada de pan":
                if not tiene_pan:
                    self.pasos_simulacion.append((idx, "error_sin_plato", "ERROR: No tienes pan en el plato.", None))
                    error_fatal = True
                    break
                elif not (tiene_mantequilla and tiene_jamon and tiene_queso):
                    self.pasos_simulacion.append((idx, "pan_en_plato", "ERROR: Faltan ingredientes antes de cerrar.", None))
                    error_fatal = True
                    break
                else:
                    if not sandwich_cerrado:
                        sandwich_cerrado = True
                        puntos += 2
                    self.pasos_simulacion.append((idx, "sandwich_cerrado", "Paso válido: Sándwich cerrado (+2 pts)", None))
            elif instruccion == "Tostar el sándwich en la sandwichera":
                if not sandwich_cerrado:
                    self.pasos_simulacion.append((idx, "pan_en_plato", "ERROR: Cierra el sándwich antes de tostarlo.", None))
                    error_fatal = True
                    break
                else:
                    if not tostado:
                        tostado = True
                        puntos += 3
                    self.pasos_simulacion.append((idx, "tostando", "Paso válido: Tostando el sándwich (+3 pts)", None))
            elif instruccion == "Comer el sándwich tostado":
                if not sandwich_cerrado:
                    self.pasos_simulacion.append((idx, "pan_en_plato", "ERROR: El sándwich no está armado.", None))
                    error_fatal = True
                    break
                elif not tostado:
                    self.pasos_simulacion.append((idx, "sandwich_cerrado", "ERROR: Comiste el sándwich frío sin tostar.", None))
                    error_fatal = True
                    break
                elif idx != len(self.algoritmo_usuario) - 1:
                    self.pasos_simulacion.append((idx, "comiendo_sandwich", "ERROR: Comiste antes de terminar el algoritmo.", None))
                    error_fatal = True
                    break
                else:
                    comido = True
                    puntos += 3
                    self.pasos_simulacion.append((idx, "comiendo_sandwich", "Paso válido: Disfrutando el sándwich (+3 pts)", None))
            elif instruccion == "Poner cáscara de plátano en el pan":
                puntos = max(0, puntos - 5)
                self.pasos_simulacion.append((idx, "trampa_platano", "ERROR GRAVE: Cáscara de plátano en el sándwich (-5 pts)", None))
                error_fatal = True
                break
            elif instruccion == "Meter el plato de metal en el microondas":
                puntos = max(0, puntos - 5)
                self.pasos_simulacion.append((idx, "trampa_microondas", "PELIGRO: Metal en el microondas (-5 pts)", None))
                error_fatal = True
                break
            elif instruccion == "Guardar el pan en la nevera":
                puntos = max(0, puntos - 2)
                self.pasos_simulacion.append((idx, "trampa_nevera", "Paso innecesario: Pan en la nevera (-2 pts)", None))
                error_fatal = True
                break

        return puntos, (not error_fatal and comido)

    def reproducir_paso(self, dt=0):
        if self.indice_sim < len(self.pasos_simulacion):
            idx_lista, img_nombre, descripcion, respaldo = self.pasos_simulacion[
                self.indice_sim
            ]
            self.refrescar_lista_algoritmo(indice_activo=idx_lista)
            self.mostrar_imagen(img_nombre, descripcion, respaldo)
            self.indice_sim += 1
            self.evento_sim = Clock.schedule_once(self.reproducir_paso, 1.2)
        else:
            self.evento_sim = None
            self.ejecutando = False
            self.refrescar_lista_algoritmo()
            self.actualizar_estadisticas(self.puntaje_final)

            if 10 <= self.puntaje_final <= 20 and self.algoritmo_completado_ok:
                self.nivel_finalizado = True
                self.mostrar_imagen(
                    "completada",
                    f"¡{self.titulo_nivel.upper()} COMPLETADO! Puntos: {self.puntaje_final}/20",
                    puntaje_superpuesto=self.puntaje_final,
                )
            elif self.puntaje_final < 10 or self.intentos_usados >= self.max_intentos:
                if self.intentos_usados >= self.max_intentos:
                    self.nivel_finalizado = True
                    msg = f"NIVEL NO COMPLETADO (3/3 intentos). Puntos: {self.puntaje_final}/20"
                else:
                    restantes = self.max_intentos - self.intentos_usados
                    msg = f"Puntuación menor a 10 ({self.puntaje_final} pts). Quedan {restantes} oportunidad(es)."
                    self.btn_ejecutar.disabled = False
                    self.btn_ejecutar.background_color = hex_to_rgba("#16A34A")

                self.mostrar_imagen(
                    "no_completada", msg, puntaje_superpuesto=self.puntaje_final
                )
            else:
                restantes = self.max_intentos - self.intentos_usados
                self.mostrar_imagen(
                    "no_completada",
                    f"Algoritmo incompleto ({self.puntaje_final} pts). Quedan {restantes} oportunidad(es).",
                    puntaje_superpuesto=self.puntaje_final,
                )
                self.btn_ejecutar.disabled = False
                self.btn_ejecutar.background_color = hex_to_rgba("#16A34A")


class AprendeAlgoritmosApp(App):
    def build(self):
        self.title = "Aprende Algoritmos"
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.ruta_ppal = os.path.join(self.base_dir, "ppal")
        self.ruta_limonada = os.path.join(self.base_dir, "imageneslimonada")
        self.ruta_sandwich = os.path.join(self.base_dir, "sandwich")

        self.sm = ScreenManager()
        self.pantalla_menu = PantallaMenu(self, name="menu")
        self.pantalla_nivel = PantallaNivel(self, name="nivel")
        self.sm.add_widget(self.pantalla_menu)
        self.sm.add_widget(self.pantalla_nivel)
        return self.sm

    def buscar_imagen(self, carpeta, nombre_base):
        objetivo = nombre_base.strip().lower()
        extensiones_validas = (".png", ".jpg", ".jpeg", ".webp", ".bmp")
        if os.path.exists(carpeta):
            for archivo in os.listdir(carpeta):
                nombre, ext = os.path.splitext(archivo)
                nombre_limpio = nombre.strip().lower()
                if nombre_limpio.endswith(".png"):
                    nombre_limpio = nombre_limpio[:-4]
                if nombre_limpio == objetivo and ext.lower() in extensiones_validas:
                    return os.path.join(carpeta, archivo)
        return None

    def abrir_nivel(self, num_nivel):
        self.pantalla_nivel.cargar_nivel(num_nivel)
        self.sm.current = "nivel"

    def mostrar_popup(self, titulo, mensaje):
        box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        lbl = Label(text=mensaje, halign="center", valign="middle")
        lbl.bind(size=lbl.setter("text_size"))
        btn = Button(
            text="Entendido",
            size_hint_y=0.35,
            background_normal="",
            background_color=hex_to_rgba("#2563EB"),
        )
        box.add_widget(lbl)
        box.add_widget(btn)
        popup = Popup(title=titulo, content=box, size_hint=(0.8, 0.4))
        btn.bind(on_release=popup.dismiss)
        popup.open()


if __name__ == "__main__":
    AprendeAlgoritmosApp().run()