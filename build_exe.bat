@echo off
setlocal
title Build DialogueForge.exe

REM Run from this script's folder whatever the console's current directory is.
cd /d "%~dp0"

echo.
echo  DialogueForge build
echo  ===================
echo.
echo  Working folder: %CD%
echo.

if not exist "src\DialogueForge.py" (
    echo  [X] src\DialogueForge.py is missing.
    echo.
    echo      Run this from the root of the repo, with src\ next to it.
    echo      If you downloaded single files rather than the whole repo,
    echo      grab the full source zip instead.
    echo.
    dir /b
    echo.
    pause
    exit /b 1
)
echo  [OK] found src\DialogueForge.py

python --version >nul 2>&1
if errorlevel 1 (
    echo  [X] Python not found on PATH.
    echo      Install from https://www.python.org/downloads/ and tick
    echo      "Add python.exe to PATH".
    pause
    exit /b 1
)
for /f "delims=" %%v in ('python --version') do echo  [OK] %%v

python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo  [X] This Python has no tkinter.
    echo      Re-run the Python installer, choose Modify, tick "tcl/tk and IDLE".
    pause
    exit /b 1
)
echo  [OK] tkinter available

echo  [..] Installing / updating PyInstaller
python -m pip install --upgrade --quiet pyinstaller
if errorlevel 1 (
    echo  [X] PyInstaller could not be installed. Check your connection.
    pause
    exit /b 1
)
echo  [OK] PyInstaller ready

echo  [..] Installing / updating pyspellchecker (powers spellcheck)
python -m pip install --upgrade --quiet pyspellchecker
set SPELLOPT=
python -c "import spellchecker" >nul 2>&1
if errorlevel 1 (
    echo  [!] pyspellchecker not available - the build will still work, but
    echo      spellcheck will be switched off in the .exe.
) else (
    echo  [OK] pyspellchecker ready - its dictionary will be bundled
    set SPELLOPT=--collect-data spellchecker
)
echo.

echo  Which build?
echo.
echo    [1] Single .exe   - one file, easiest to hand out. Slower to start
echo                        and more likely to trip antivirus.
echo    [2] Folder        - zip and upload. Starts instantly, far less
echo                        likely to be flagged. Recommended for release.
echo    [3] Both
echo.
set /p CHOICE=  Enter 1, 2 or 3 (default 3): 
if "%CHOICE%"=="" set CHOICE=3

REM --noupx matters: UPX-compressed exes are a known antivirus trigger and
REM the size saving is not worth the support load.
set COMMON=--windowed --clean --noconfirm --noupx --name DialogueForge
set COMMON=%COMMON% --icon src\logo.ico --version-file src\version_info.txt
REM SPELLOPT bundles pyspellchecker's dictionary; empty when it isn't installed.
set COMMON=%COMMON% %SPELLOPT%

if "%CHOICE%"=="2" goto onedir

:onefile
echo.
echo  [..] Building single-file exe
python -m PyInstaller %COMMON% --onefile src\DialogueForge.py
if errorlevel 1 goto failed
echo  [OK] dist\DialogueForge.exe
if "%CHOICE%"=="1" goto done

:onedir
echo.
echo  [..] Building folder distribution
python -m PyInstaller %COMMON% --onedir --distpath dist_folder src\DialogueForge.py
if errorlevel 1 goto failed
echo  [OK] dist_folder\DialogueForge\DialogueForge.exe
goto done

:failed
echo.
echo  [X] Build failed. Scroll up for the error.
pause
exit /b 1

:done
echo.
echo  ===================================================================
echo   Done.
echo.
echo   Single file : dist\DialogueForge.exe
echo   Folder      : dist_folder\DialogueForge\   (zip this to release)
echo.
echo   Neither needs Python on the target PC.
echo   Read docs\RELEASING.md before publishing.
echo  ===================================================================
echo.
pause
