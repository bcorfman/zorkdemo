# -*- mode: python ; coding: utf-8 -*-
import glob
import os
import platform
import sys

# modify sys.path so it can find version.py in the current working dir.
sys.path.insert(0, '.')
try:
    print "VERSION found"
    from version import VERSION
except ImportError:
    print "VERSION import error"
    VERSION='refs/tags/0.3.0.0'

block_cipher = None
os_name = platform.system()


a = Analysis(['main.py'],
             binaries=[],
             datas=[('data','data')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Mimetyx-ZorkDemo-{}'.format(VERSION),
          debug=False,
          strip=False,
          upx=False,
          console=True )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='zorkdemo')

if os_name == 'Darwin':
    VERSION_NUM = VERSION.rsplit('/', 1)[1]
    ver = [int(i) for i in VERSION_NUM.split('.')]
    info_plist = {
        'CFBundleName': 'ZorkDemo',
        'CFBundleDisplayName': 'Mimetyx ZorkDemo',
        'CFBundleIdentifier': 'org.mimetyx.zorkdemo',
        'CFBundleVersion': '%d.%d.%d.%d' % (ver[0], ver[1], ver[2], ver[3]),
        'CFBundleShortVersionString': str(ver[0]) + '.' + str(ver[1]),
        'LSApplicationCategoryType': 'public.app-category.adventure-games',
        'LSMinimumSystemVersion': os.environ.get('MACOSX_DEPLOYMENT_TARGET', '10.15'),
        'NSHighResolutionCapable': 'True',
        'NSPrincipalClass': 'NSApplication'
    }


    app = BUNDLE(coll,
                 name='zorkdemo.app',
                 bundle_identifier=None,
                 info_plist=info_plist
                 )
