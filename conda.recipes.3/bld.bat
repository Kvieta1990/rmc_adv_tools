:: %PYTHON% -m easy_install --no-deps .
:: if errorlevel 1 exit 1
%PYTHON% setup.py install
if errorlevel 1 exit 1

set MENU_DIR=%PREFIX%\Menu
if not exist (%MENU_DIR%) mkdir %MENU_DIR%

copy %RECIPE_DIR%\tr_icon.ico %MENU_DIR%
if errorlevel 1 exit 1

%PYTHON% %RECIPE_DIR%\expandpath.py %RECIPE_DIR%\menu-windows.json > %MENU_DIR%\menu-windows.json
if errorlevel 1 exit 1

:: copy %RECIPE_DIR%\menu-windows.json %MENU_DIR%\topas4rmc.json
:: if errorlevel 1 exit 1

