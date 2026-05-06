@echo off
REM The Maze Game - Quick Run Script
REM This script compiles and runs the game with or without GUI

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                 THE MAZE - GAME LAUNCHER                      ║
echo ║              Dark Fantasy Dungeon Crawler                      ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Check if src folder exists
if not exist "src" (
    echo ❌ Error: src folder not found!
    echo Please make sure you're in the project directory.
    pause
    exit /b 1
)

REM Menu
echo Choose which version to run:
echo.
echo [1] Launch GUI Version (Graphical with Colors & Buttons) ⭐ RECOMMENDED
echo [2] Launch Console Version (Text-based)
echo [3] Compile Project Only
echo [4] Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Starting The Maze GUI...
    echo Compiling project...
    javac -d . src/edu/wctc/*.java
    if errorlevel 1 (
        echo ❌ Compilation failed!
        pause
        exit /b 1
    )
    echo ✅ Compilation complete!
    echo.
    echo Launching GUI window...
    echo.
    java edu.wctc.GameGUI
) else if "%choice%"=="2" (
    echo.
    echo Starting The Maze Console Version...
    echo Compiling project...
    javac -d . src/edu/wctc/*.java
    if errorlevel 1 (
        echo ❌ Compilation failed!
        pause
        exit /b 1
    )
    echo ✅ Compilation complete!
    echo.
    echo Running game...
    echo.
    java edu.wctc.Main
) else if "%choice%"=="3" (
    echo.
    echo Compiling project...
    javac -d . src/edu/wctc/*.java
    if errorlevel 1 (
        echo ❌ Compilation failed!
        pause
        exit /b 1
    )
    echo ✅ Compilation complete!
    pause
) else if "%choice%"=="4" (
    echo Exiting...
    exit /b 0
) else (
    echo Invalid choice. Exiting.
    exit /b 1
)

pause

