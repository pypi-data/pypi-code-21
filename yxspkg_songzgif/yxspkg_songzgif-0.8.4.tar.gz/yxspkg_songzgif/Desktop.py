import  os,sys
from os import path
from urllib import request

def main():
    for i,v in enumerate(sys.argv):
        if v=='--python':
            default_python=sys.argv[i+1]
            break 
    else:
        default_python = 'python3'

    if sys.platform.startswith('win'):
        print('Downloading file')
        p=os.environ['HOMEPATH']
        desk=path.join('C:',p,'Desktop')
        exe_name=path.join(desk,'SongZ GIF.exe')
        if path.isdir(desk) and not path.isfile(exe_name):
            exe_file_url='https://raw.githubusercontent.com/blacksong/fragment/master/SongZ%20GIF.exe'
            exe_file = request.urlopen(exe_file_url).read()
            fp=open(exe_name,'wb')
            fp.write(exe_file)
            fp.close()
    elif sys.platform.startswith('darwin'):
        print('Downloading file')
        
        info_file = b'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key>
  <string>run.sh</string>
  <key>CFBundleName</key>
  <string>Gif Maker</string>
  <key>CFBundleIconFile</key>
  <string>main.icns</string>
</dict>
</plist>
'''
        run_file=b'''#!/bin/sh
python3 -m yxspkg_songzgif.gif'''
        if default_python!='python3':
            run_file=run_file.replace(b'python3',default_python.encode())
        p=os.environ['HOMEPATH']
        desk=path.join(p,'Desktop')
        app_name=path.join(desk,'SongZ GIF.app')
        if path.isdir(desk) and not path.isdir(app_name):
            app_file_url='https://raw.githubusercontent.com/blacksong/fragment/master/SongZ_GIF.icns'
            app_file = request.urlopen(app_file_url).read()
            os.makedirs(path.join(app_name,'Contents','MacOS'))
            os.makedirs(path.join(app_name,'Contents','Resources'))
            open(path.join(app_name,'Contents','Resources','main.icns'),'wb').write(app_file)
            open(path.join(app_name,'Contents','Info.plist'),'wb').write(info_file)
            open(path.join(app_name,'Contents','MacOS','run.sh'),'wb').write(run_file)
    elif sys.platform.startswith('linux'):
        
        desktop_file='''[Desktop Entry]
Name=SongZ GIF
Name[zh_CN]=SongZ GIF
Comment=Edit gif and video

Comment[zh_CN]=编辑gif动图和视频
Exec={py} -m yxspkg_songzgif.gif
Terminal=false
Type=Application
StartupNotify=true
MimeType=video/image;
Icon={png}
Categories=GNOME;GTK;Utility;TextEditor;

[Desktop Action new-window]
Name=New Window
Exec={py} -m yxspkg_songzgif.gif
''' 
        p=os.environ['HOME']
        applications=path.join(p,'.local','share','applications')
        if not path.isdir(applications):
            os.makedirs(applications)
        icon=path.join(p,'.local','share','icons','SongZ_GIF')
        if not path.isdir(icon):
            os.makedirs(icon)
        icon_name=path.join(icon,'SongZ_GIF.png')
        if not path.isfile(icon_name):
            print('Downloading file')
            png_file_url='https://raw.githubusercontent.com/blacksong/fragment/master/SongZ_GIF.png'
            png_file = request.urlopen(png_file_url).read()
            open(icon_name,'wb').write(png_file)
        desktop_file=desktop_file.format(py=default_python,png=icon_name)
        if not path.isfile(path.join(applications,'SongZ GIF.desktop')):
            open(path.join(applications,'SongZ GIF.desktop'),'w').write(desktop_file)

if __name__=='__main__':
    main()