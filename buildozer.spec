[app]
title = Convertidor de Temperatura
package.name = convertidor
package.domain = org.conversor.temp
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 0.3
requirements = python3,kivy==2.3.1,pillow,pyjnius,android
orientation = portrait
fullscreen = 0
android.permissions = VIBRATE
android.api = 34
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a,x86_64
android.accept_sdk_license = True
android.allow_backup = True
android.presplash_color = #10131A
p4a.branch = v2024.01.21

[buildozer]
log_level = 2
warn_on_root = 1
