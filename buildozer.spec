[app]
title = Aprende Algoritmos
package.name = aprendealgoritmos
package.domain = org.educacion
source.dir = .
source.include_exts = py,png,jpg,jpeg,webp,ttf
version = 0.1
requirements = python3==3.11.6,hostpython3==3.11.6,kivy==2.3.0,pillow,charset-normalizer==3.3.2
icon.filename = %(source.dir)s/ppal/projo.png
orientation = landscape
fullscreen = 1

[buildozer]
log_level = 2
warn_on_root = 1
android.archs = arm64-v8a
android.accept_sdk_license = True
