@echo off
setlocal
cd /d "%~dp0"

if not exist .venv (
    py -3 -m venv .venv
    if errorlevel 1 goto :error
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
if errorlevel 1 goto :error
python -m pip install -r requirements-build.txt
if errorlevel 1 goto :error

python -c "import alembic3d, imath; print('Alembic bindings OK')"
if errorlevel 1 goto :error

python -m PyInstaller --noconfirm --clean JSONToAnimCam.spec
if errorlevel 1 goto :error

echo.
echo Build complete:
echo %CD%\dist\JSONToAnimCam\JSONToAnimCam.exe
echo.
echo Distribute the whole dist\JSONToAnimCam folder.
pause
exit /b 0

:error
echo.
echo Build failed. Review the error above.
pause
exit /b 1
