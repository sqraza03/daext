@echo off

title Building Fury
echo Building Fury executable...

REM Clean previous builds
if exist build rd /s /q build
if exist dist rd /s /q dist
if exist output rd /s /q output
if exist main.spec del main.spec

REM Create the PyInstaller spec file for better control
echo Creating PyInstaller spec file...

pyinstaller --onefile ^
--console ^
--uac-admin ^
--optimize=2 ^
--icon=NONE ^
--name=main ^
--distpath=output ^
--workpath=build ^
--specpath=. ^
--hidden-import=ui.config ^
--hidden-import=ui.menu ^
--hidden-import=ui.materials.draw ^
--hidden-import=ui.materials.components ^
--hidden-import=ui.controllers.control ^
--hidden-import=ui.resources.fonts ^
--hidden-import=ui.resources.textures ^
--hidden-import=ui.auth_window ^
--hidden-import=core.utils ^
--hidden-import=core.offsets ^
--hidden-import=core.overlay ^
--hidden-import=core.security ^
--hidden-import=core.config_manager ^
--hidden-import=core.auth ^
--hidden-import=core.enhanced_overlay ^
--hidden-import=features.esp ^
--hidden-import=features.aimbot ^
--hidden-import=features.trigger ^
--hidden-import=features.entity ^
--hidden-import=mysql.connector ^
--hidden-import=mysql.connector.cursor ^
--hidden-import=mysql.connector.errors ^
--hidden-import=mysql.connector.connection ^
--hidden-import=mysql.connector.pooling ^
--hidden-import=websocket ^
--hidden-import=websocket._app ^
--hidden-import=websocket._core ^
--hidden-import=websocket._exceptions ^
--hidden-import=websocket._http ^
--hidden-import=websocket._logging ^
--hidden-import=websocket._socket ^
--hidden-import=websocket._ssl_compat ^
--hidden-import=websocket._url ^
--hidden-import=websocket._utils ^
--hidden-import=tkinter ^
--hidden-import=tkinter.ttk ^
--hidden-import=tkinter.messagebox ^
--hidden-import=tkinter.font ^
--hidden-import=tkinter.filedialog ^
--hidden-import=threading ^
--hidden-import=json ^
--hidden-import=os ^
--hidden-import=sys ^
--hidden-import=time ^
--hidden-import=datetime ^
--hidden-import=hashlib ^
--hidden-import=platform ^
--hidden-import=subprocess ^
--hidden-import=uuid ^
--hidden-import=requests ^
--hidden-import=requests.adapters ^
--hidden-import=requests.auth ^
--hidden-import=requests.cookies ^
--hidden-import=requests.exceptions ^
--hidden-import=requests.models ^
--hidden-import=requests.sessions ^
--hidden-import=requests.utils ^
--hidden-import=psutil ^
--hidden-import=psutil._common ^
--hidden-import=psutil._compat ^
--hidden-import=psutil._psutil_windows ^
--hidden-import=ctypes ^
--hidden-import=ctypes.wintypes ^
--hidden-import=winreg ^
--hidden-import=io ^
--hidden-import=traceback ^
--hidden-import=random ^
--hidden-import=string ^
--hidden-import=unicodedata ^
--hidden-import=math ^
--add-data "assets/fonts/arial.ttf;fonts" ^
--add-data "assets/fonts/icons.ttf;fonts" ^
--add-data "assets/fonts/weapon.ttf;fonts" ^
--add-data "assets/textures/colorpicker.png;textures" ^
--paths=src ^
--paths=src/ui ^
--paths=src/core ^
--paths=src/features ^
src/main.py

timeout /t 2 > nul

REM Clean up build artifacts
if exist build rd /s /q build
if exist main.spec del main.spec

echo.
echo Build completed! Check the 'output' folder for main.exe
echo.
pause