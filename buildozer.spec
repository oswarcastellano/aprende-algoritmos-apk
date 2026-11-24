[app]
title = Aprende Algoritmos
package.name = aprendealgoritmos
package.domain = org.educacion
source.dir = .
source.include_exts = py,png,jpg,jpeg,webp,ttf
version = 0.1
requirements = python3,kivy,pillow
icon.filename = %(source.dir)s/ppal/projo.png
orientation = landscape
fullscreen = 1

[buildozer]
log_level = 2
warn_on_root = 1
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
