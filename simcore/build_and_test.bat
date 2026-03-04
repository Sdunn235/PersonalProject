@echo off
REM ============================================================
REM  SimCore Build + Test Script
REM  Works with: MinGW (MSYS2), MSVC, or Ninja
REM  IDE: IntelliJ IDEA / CLion / standalone
REM ============================================================
setlocal EnableDelayedExpansion

set SIMCORE_DIR=%~dp0
set BUILD_DIR=%SIMCORE_DIR%build
set CMAKE_EXE=
set GENERATOR=
set FOUND_COMPILER=0

echo.
echo ====================================================
echo  SimCore Build ^& Test
echo ====================================================
echo.

REM ── 1. Find cmake ────────────────────────────────────────────
where cmake >nul 2>&1
if %ERRORLEVEL% equ 0 ( set CMAKE_EXE=cmake & goto :find_compiler )

REM MSYS2 MinGW64 (most common on IntelliJ/Windows without VS)
if exist "C:\msys64\mingw64\bin\cmake.exe" (
    set CMAKE_EXE=C:\msys64\mingw64\bin\cmake.exe
    set PATH=C:\msys64\mingw64\bin;%PATH%
    echo Found MSYS2 MinGW64 cmake.
    goto :find_compiler
)
if exist "C:\msys64\ucrt64\bin\cmake.exe" (
    set CMAKE_EXE=C:\msys64\ucrt64\bin\cmake.exe
    set PATH=C:\msys64\ucrt64\bin;%PATH%
    echo Found MSYS2 UCRT64 cmake.
    goto :find_compiler
)

REM JetBrains CLion bundled cmake
for /d %%D in ("C:\Program Files\JetBrains\CLion*") do (
    if exist "%%D\bin\cmake\win\x64\bin\cmake.exe" (
        set CMAKE_EXE=%%D\bin\cmake\win\x64\bin\cmake.exe
        echo Found CLion-bundled cmake: %%D
        goto :find_compiler
    )
)

REM VS 2022 bundled cmake (if C++ workload installed)
set VS_CMAKE="C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe"
if exist %VS_CMAKE% ( set CMAKE_EXE=%VS_CMAKE% & goto :find_compiler )

echo ERROR: cmake not found.
echo.
echo ── QUICK FIX (run ONE of these in a terminal, then re-run this script) ──
echo.
echo   Option A - MSYS2 + MinGW ^(recommended for IntelliJ^):
echo     1. Download and install MSYS2 from https://www.msys2.org/
echo        OR run:  winget install MSYS2.MSYS2
echo     2. Open "MSYS2 MinGW64" from Start Menu and run:
echo          pacman -S --noconfirm mingw-w64-x86_64-cmake mingw-w64-x86_64-gcc mingw-w64-x86_64-ninja
echo     3. Re-run this script.
echo.
echo   Option B - VS 2022 C++ workload:
echo     Open Visual Studio Installer ^> Modify VS 2022 ^> add
echo     "Desktop development with C++" ^> Install
echo.
goto :eof

:find_compiler
REM ── 2. Find compiler and pick generator ──────────────────────

REM Check MinGW/GCC
where g++ >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set GENERATOR=MinGW Makefiles
    set FOUND_COMPILER=1
    echo Compiler: g++ ^(MinGW^)
    goto :configure
)
if exist "C:\msys64\mingw64\bin\g++.exe" (
    set PATH=C:\msys64\mingw64\bin;%PATH%
    set GENERATOR=MinGW Makefiles
    set FOUND_COMPILER=1
    echo Compiler: MSYS2 MinGW64 g++
    goto :configure
)
if exist "C:\msys64\ucrt64\bin\g++.exe" (
    set PATH=C:\msys64\ucrt64\bin;%PATH%
    set GENERATOR=MinGW Makefiles
    set FOUND_COMPILER=1
    echo Compiler: MSYS2 UCRT64 g++
    goto :configure
)

REM Check Ninja (CLion often installs this)
where ninja >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set GENERATOR=Ninja
    set FOUND_COMPILER=1
    echo Compiler: Ninja
    goto :configure
)

REM Check MSVC
where cl >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set GENERATOR=NMake Makefiles
    set FOUND_COMPILER=1
    echo Compiler: MSVC cl
    goto :configure
)

echo ERROR: No C++ compiler found ^(g++, clang++, or cl^).
echo.
echo ── QUICK FIX ──────────────────────────────────────────────────
echo   Run in MSYS2 MinGW64 shell:
echo     pacman -S --noconfirm mingw-w64-x86_64-gcc mingw-w64-x86_64-cmake mingw-w64-x86_64-ninja
echo   Then add C:\msys64\mingw64\bin to your Windows PATH.
echo ────────────────────────────────────────────────────────────────
goto :eof

:configure
echo.
echo [1/3] Configuring...  generator: %GENERATOR%
"%CMAKE_EXE%" -B "%BUILD_DIR%" -G "%GENERATOR%" -DCMAKE_BUILD_TYPE=Release "%SIMCORE_DIR%"
if %ERRORLEVEL% neq 0 ( echo Configuration FAILED. & pause & exit /b 1 )

echo.
echo [2/3] Building...
"%CMAKE_EXE%" --build "%BUILD_DIR%" --config Release --parallel
if %ERRORLEVEL% neq 0 ( echo Build FAILED. & pause & exit /b 1 )

echo.
echo [3/3] Running tests...
cd /d "%BUILD_DIR%"
ctest -C Release --output-on-failure -V
if %ERRORLEVEL% neq 0 ( echo. & echo Some tests FAILED. & pause & exit /b 1 )

echo.
echo ====================================================
echo  ALL TESTS PASSED
echo ====================================================
echo.
pause

