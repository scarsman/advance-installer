# -*- mode: python -*-

block_cipher = None

import os
import platform

def get_binaries(start_dir_path,mode):
  
  results = []
  
  for path, dirs, files in os.walk(start_dir_path):
    
    print ("==================")
    
    print ("DIR : %s" % path)
    
    for f in files:
      
      if (mode == "Windows" and f[-4:] == ".pyd") or (mode == "Linux" and f[-3:] == ".so") :
          
        # construct full file path
        full_file_path = os.path.join(path,f)
        #print full_file_path
            
        print("adding: %s" % full_file_path)
              
        # construct the package structure
          
        tmp_path = path.replace(start_dir_path,"")
        relevant_packages = tmp_path.split(os.path.sep)[1:]
              
        #print(relevant_packages)
            
        if len(relevant_packages) > 0:
            
          package_structure = os.path.sep.join(relevant_packages)
          
          entry = (full_file_path,package_structure)
          
          print(entry)
              
          results.append(entry)
  
  return results

a = Analysis(['SCLExpress.py'],
             pathex=['E:\\advance-installer\\scl_backend'],
             binaries=get_binaries(os.getcwd(),platform.system()),
             datas=[],
             hiddenimports=["-v"],
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
          name='SCLExpress',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False , icon='C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\2\\scl.ico')
