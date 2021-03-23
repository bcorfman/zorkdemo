# -*- mode: python ; coding: utf-8 -*-
import glob
import os
import platform
import sys

# modify sys.path so it can find version.py in the current working dir.
sys.path.insert(0, '.')
from version import VERSION

block_cipher = None


a = Analysis(['zorkdemo.py'],
             binaries=[],
             datas=[('data','data')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

os_name = platform.system()

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          # Avoid name clash between picard executable and picard module folder
          name='zorkdemo' if os_name == 'Windows' else 'zorkdemo-run',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
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
        'CFBundleDisplayName': 'ZorkDemo',
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
