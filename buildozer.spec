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
android.archs = arm64-v8a
android.ndk = 25b
android.api = 33
android.minapi = 21
android.accept_sdk_license = True
p4a.branch = release-2024.01.21
