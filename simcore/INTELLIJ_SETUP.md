# SimCore — IntelliJ IDEA Setup Guide

## What You Need (One-Time Setup)

You need a C++ compiler + cmake. The fastest path on Windows with IntelliJ is **MSYS2**.

### Step 1 — Install MSYS2

Open a **normal Windows terminal** (not the IDE terminal) and run:

```
winget install MSYS2.MSYS2
```

If winget isn't found, download the installer directly from: https://www.msys2.org/

### Step 2 — Install GCC + CMake + Ninja inside MSYS2

After MSYS2 installs, open **"MSYS2 MinGW64"** from the Start Menu (the one labeled MinGW64, not MSYS2 or UCRT64) and run:

```bash
pacman -S --noconfirm mingw-w64-x86_64-gcc mingw-w64-x86_64-cmake mingw-w64-x86_64-ninja
```

### Step 3 — Add MinGW to Windows PATH

1. Search "Environment Variables" in Start Menu
2. Edit **System** → Path → New → add: `C:\msys64\mingw64\bin`
3. Click OK, **restart IntelliJ IDEA**

---

## Opening SimCore in IntelliJ IDEA

IntelliJ IDEA 2025+ has native CMake support via the **C/C++ plugin**.

### Option A — Open as CMake Project (Recommended)

1. In IntelliJ: **File → Open**
2. Navigate to: `C:\Users\Shawn\Documents\Personal Project\simcore`
3. Select the **`CMakeLists.txt`** file
4. Choose **"Open as Project"**
5. IntelliJ will detect it as a CMake project automatically

### Option B — If IntelliJ asks about the toolchain

Go to **File → Settings → Build, Execution, Deployment → CMake**:
- Generator: `MinGW Makefiles` (or `Ninja` if you prefer)
- CMake options: `-DCMAKE_BUILD_TYPE=Release`

Go to **File → Settings → Build, Execution, Deployment → Toolchains**:
- Add a new **MinGW** toolchain
- C compiler: `C:\msys64\mingw64\bin\gcc.exe`
- C++ compiler: `C:\msys64\mingw64\bin\g++.exe`
- CMake: `C:\msys64\mingw64\bin\cmake.exe`

---

## Running Tests in IntelliJ

Once the project loads:

1. In the **CMake** tool window (View → Tool Windows → CMake), click **Reload CMake Project**
2. The `simcore_tests` target will appear in the Run configurations dropdown
3. Click **Run** → select `simcore_tests`
4. All 60+ tests will run in the built-in test runner with pass/fail per test

---

## Alternative: Run build_and_test.bat directly

After installing MSYS2 and adding `C:\msys64\mingw64\bin` to PATH:

1. Double-click `simcore\build_and_test.bat`
2. It auto-detects the MinGW toolchain and runs all tests
3. All tests should pass

---

## What Gets Built

```
simcore/build/
  libsimcore.a        ← static library (link this into your Unreal adapter)
  simcore_tests.exe   ← test runner
```

The `libsimcore.a` (or `.lib` on MSVC) is what the Unreal `SimCoreAdapter` module
will link against in Phase 3.

