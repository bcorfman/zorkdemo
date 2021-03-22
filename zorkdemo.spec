# -*- mode: python ; coding: utf-8 -*-
import glob
import os
import platform
import sys

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
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='zorkdemo',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )

os_name = platform.system()
if os_name == 'Darwin':
    info_plist = {
        'CFBundleName': 'ZorkDemo',
        'CFBundleDisplayName': 'ZorkDemo',
        'CFBundleIdentifier': 'org.mimetyx.zorkdemo',
        'CFBundleVersion': '%d.%d.%d.%d' % VERSION.split('.')[:4],
        'CFBundleShortVersionString': VERSION.split('.')[:3],
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
