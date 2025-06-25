[app]
title = Таймер сна TV
package.name = sleeptimer_tv
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,ttf
version = 1.0
requirements = python3,kivy>=2.0.0,plyer
android.permissions = FOREGROUND_SERVICE
android.api = 30
android.minapi = 21
android.ndk = 23b
android.meta_data = android.software.leanback
android.features = android.software.leanback
orientation = landscape
fullscreen = 1
log_level = 2

[buildozer]
log_level = 2