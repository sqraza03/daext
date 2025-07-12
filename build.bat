@echo off

title /output
echo building...

pyinstaller --onefile --console --uac-admin --optimize=2 --i="NONE" --hidden-import=mysql.connector --hidden-import=mysql.connector.cursor --hidden-import=mysql.connector.errors --hidden-import=core.auth --hidden-import=core.enhanced_overlay --hidden-import=core.security --hidden-import=core.config_manager --hidden-import=ui.auth_window --hidden-import=tkinter --hidden-import=tkinter.ttk --hidden-import=tkinter.messagebox --hidden-import=threading --hidden-import=json --hidden-import=os --hidden-import=sys --hidden-import=time --hidden-import=datetime --hidden-import=hashlib --hidden-import=platform --hidden-import=subprocess --hidden-import=uuid --hidden-import=requests --hidden-import=websocket --hidden-import=psutil --add-data "assets/fonts/arial.ttf;fonts" --add-data "assets/fonts/icons.ttf;fonts" --add-data "assets/fonts/weapon.ttf;fonts" --add-data "assets/textures/colorpicker.png;textures" --paths=src src/main.py > nul 2>&1

timeout /t 1 > nul

if exist build rd /s /q build
if exist main.spec del main.spec
if exist dist ren dist output
