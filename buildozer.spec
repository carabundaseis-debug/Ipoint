[app]
title = Ipoint
package.name = ipoint
package.domain = org.ipoint

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

requirements = python3==3.11.8,hostpython3==3.11.8,kivy==2.3.0

orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/icon.png

android.permissions =
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
