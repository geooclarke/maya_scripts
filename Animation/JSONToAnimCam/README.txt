JSONToAnimCam bundled Windows build
====================================

For end users
-------------
Run JSONToAnimCam.exe from the built JSONToAnimCam folder.
No separate Python or Alembic installation is required on the end user's PC.
Keep the full folder together; do not copy only the EXE.

For the developer building the app
----------------------------------
1. Install a supported 64-bit CPython version on Windows.
2. Double-click build_windows.bat.
3. The distributable application is created at:
   dist\JSONToAnimCam\JSONToAnimCam.exe
4. Distribute the entire dist\JSONToAnimCam folder.

The build script creates a private .venv and installs:
- alembic3d 1.8.12.1
- PyInstaller 6.22.3

The PyInstaller spec explicitly collects alembic3d and Imath binaries, data,
and hidden imports. A one-folder build is used because it is simpler to inspect
and more reliable for native libraries than extracting them from a one-file EXE.

Important
---------
The package is named alembic3d. Do not replace it with `pip install alembic`,
which is an unrelated database migration package.

Run JSONToAnimCam.py during development.
Run JSONToAnimCam.exe for the bundled application.
