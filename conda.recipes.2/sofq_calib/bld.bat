set MENU_DIR=%PREFIX%\Menu
if not exist (%MENU_DIR%) mkdir %MENU_DIR%

copy %RECIPE_DIR%\icon.ico %MENU_DIR%
if errorlevel 1 exit 1

copy %RECIPE_DIR%\menu-windows.json %MENU_DIR%\sofq_calib.json
if errorlevel 1 exit 1

%PYTHON% setup.py install
if errorlevel 1 exit 1
