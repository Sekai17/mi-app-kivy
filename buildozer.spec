[app]
title = AI tycoon
package.name = femboy
package.domain = org.sekai17

source.dir =.
source.include_exts = py,png,jpg,kv,atlas,json

version = 0.1

requirements = python3,kivy

orientation = portrait
fullscreen = 0

# Android
android.permissions = INTERNET
android.api = 33
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a

# usa p4a develop (soporta NDK 25)
p4a.branch = develop

[buildozer]
log_level = 2
warn_on_root = 1
