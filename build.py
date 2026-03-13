#!/usr/bin/env python3
"""
imgui-lwjgl2-jni build script
-------------------------------
1. Checks / clones imgui and dear_bindings if missing
2. Creates a venv and installs dear_bindings requirements
3. Runs dear_bindings to generate dcimgui.h / dcimgui.cpp + opengl2 backend
4. Compiles imgui_jni.dll (Windows) / .so (Linux) / .dylib (macOS)
5. Compiles ImGui.java + Input.java into imgui-lwjgl2-jni.jar

Requirements:
  - Python 3.10+
  - git
  - g++ with 64-bit support (w64devkit on Windows, system gcc on Linux/macOS)
  - JAVA_HOME set to a JDK (not JRE) with javac + jar tools

Usage:
  python build.py
  python build.py --skip-bindings   # skip dear_bindings generation
  python build.py --skip-compile    # skip DLL compilation
  python build.py --skip-jar        # skip JAR compilation
"""

import argparse
import os
import platform
import subprocess
import sys
import venv
import re
import shutil
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

ROOT         = Path(__file__).parent.resolve()
SRC          = ROOT / "src"
IMGUI_DIR    = SRC / "imgui"
DB_DIR       = SRC / "dear_bindings"
DB_GENERATED = DB_DIR / "generated"
JAVA_SRC_DIR = SRC / "java"
OUT_DIR      = ROOT / "out"
VENV_DIR     = ROOT / ".venv"

# Default git URLs — user can override if they have forks
DEFAULT_IMGUI_URL = "https://github.com/ocornut/imgui.git"
DEFAULT_DB_URL    = "https://github.com/dearimgui/dear_bindings.git"

# Only opengl2 backend needed for LWJGL 2
BACKENDS = ["opengl2"]

# ── Platform detection ────────────────────────────────────────────────────────

SYSTEM = platform.system()  # 'Windows', 'Linux', 'Darwin'

if SYSTEM == "Windows":
    DLL_NAME         = "imgui_jni.dll"
    JNI_PLATFORM_INC = "win32"
    PLATFORM_FLAGS   = ["-m64"]
    LINK_FLAGS       = ["-lopengl32"]
    VENV_PYTHON      = VENV_DIR / "Scripts" / "python.exe"
    VENV_PIP         = VENV_DIR / "Scripts" / "pip.exe"
elif SYSTEM == "Linux":
    DLL_NAME         = "libimgui_jni.so"
    JNI_PLATFORM_INC = "linux"
    PLATFORM_FLAGS   = ["-fPIC"]
    LINK_FLAGS       = ["-lGL"]
    VENV_PYTHON      = VENV_DIR / "bin" / "python"
    VENV_PIP         = VENV_DIR / "bin" / "pip"
elif SYSTEM == "Darwin":
    DLL_NAME         = "libimgui_jni.dylib"
    JNI_PLATFORM_INC = "darwin"
    PLATFORM_FLAGS   = ["-fPIC"]
    LINK_FLAGS       = ["-framework", "OpenGL"]
    VENV_PYTHON      = VENV_DIR / "bin" / "python"
    VENV_PIP         = VENV_DIR / "bin" / "pip"
else:
    print(f"Unsupported platform: {SYSTEM}")
    sys.exit(1)

# ── Helpers ───────────────────────────────────────────────────────────────────

def run(cmd, cwd=None):
    """Run a command, print it, exit on failure."""
    print(f"\n>>> {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        print(f"\nBuild failed (exit code {result.returncode})")
        sys.exit(result.returncode)

def is_empty_or_missing(path):
    """Return True if path doesn't exist or is an empty directory."""
    if not path.exists():
        return True
    if path.is_dir() and not any(path.iterdir()):
        return True
    return False

def prompt_clone(name, target_dir, default_url):
    """Ask user for a git URL and clone it."""
    print(f"\n  '{target_dir.relative_to(ROOT)}' is missing or empty.")
    print(f"  Default URL: {default_url}")
    url = input(f"  Enter git URL to clone {name} (or press Enter to use default): ").strip()
    if not url:
        url = default_url
    print(f"  Cloning {name} from {url} ...")
    target_dir.parent.mkdir(parents=True, exist_ok=True)
    run(["git", "clone", url, str(target_dir)])

def check_git():
    """Make sure git is available."""
    result = subprocess.run(["git", "--version"], capture_output=True)
    if result.returncode != 0:
        print("ERROR: git is not installed or not on PATH.")
        sys.exit(1)

def check_java_home():
    """Validate JAVA_HOME and return it as a Path."""
    java_home = os.environ.get("JAVA_HOME")
    if not java_home:
        print("ERROR: JAVA_HOME is not set.")
        print("  Set it to your JDK directory, e.g.:")
        print('  Windows:  $env:JAVA_HOME = "C:\\Program Files\\Java\\jdk1.6.0_45"')
        print('  Linux:    export JAVA_HOME=/usr/lib/jvm/java-6-openjdk-amd64')
        sys.exit(1)

    java_home = Path(java_home)

    jni_h = java_home / "include" / "jni.h"
    if not jni_h.exists():
        print(f"ERROR: jni.h not found at {jni_h}")
        print("  Make sure JAVA_HOME points to a JDK, not a JRE.")
        sys.exit(1)

    javac = java_home / "bin" / ("javac.exe" if SYSTEM == "Windows" else "javac")
    if not javac.exists():
        print(f"ERROR: javac not found at {javac}")
        print("  Make sure JAVA_HOME points to a JDK, not a JRE.")
        sys.exit(1)

    result = subprocess.run(
        [str(javac), "-version"],
        capture_output=True, text=True
    )
    version_str = result.stderr.strip() or result.stdout.strip()
    print(f"  javac: {version_str}")

    match = re.search(r'javac (\d+)\.(\d+)', version_str)
    if match:
        major = int(match.group(1))
        if major > 8:
            print(f"ERROR: JDK {major} cannot target Java 6.")
            print("  Set JAVA_HOME to JDK 6 or JDK 8 to build this project.")
            print("  JDK 8 download: https://adoptium.net/temurin/releases/?version=8")
            sys.exit(1)

    return java_home

def find_64bit_gxx():
    """Find first g++ on PATH that supports 64-bit, or use GXX env override."""
    gxx = os.environ.get("GXX")
    if gxx:
        print(f"  Using GXX override: {gxx}")
        return gxx

    paths = os.environ.get("PATH", "").split(os.pathsep)
    for directory in paths:
        candidate = Path(directory) / ("g++.exe" if SYSTEM == "Windows" else "g++")
        if candidate.exists():
            result = subprocess.run(
                [str(candidate), "-dumpmachine"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and "x86_64" in result.stdout:
                print(f"  Found 64-bit g++ at: {candidate}")
                return str(candidate)
            else:
                print(f"  Skipping {candidate} ({result.stdout.strip()})")

    print("ERROR: No 64-bit g++ found on PATH.")
    print("  Install w64devkit: https://github.com/skeeto/w64devkit/releases")
    print("  Or set GXX to point directly at one:")
    print('  Windows: $env:GXX = "C:\\Program Files\\w64devkit\\bin\\g++.exe"')
    sys.exit(1)

# ── Steps ─────────────────────────────────────────────────────────────────────

def step_check_sources():
    """Check imgui and dear_bindings exist, offer to clone if missing."""
    print("\n[0/5] Checking source dependencies")
    check_git()

    if is_empty_or_missing(IMGUI_DIR) or not (IMGUI_DIR / "imgui.h").exists():
        prompt_clone("imgui", IMGUI_DIR, DEFAULT_IMGUI_URL)

    if is_empty_or_missing(DB_DIR) or not (DB_DIR / "dear_bindings.py").exists():
        prompt_clone("dear_bindings", DB_DIR, DEFAULT_DB_URL)

    # Final check after clone attempts
    if not (IMGUI_DIR / "imgui.h").exists():
        print(f"ERROR: imgui.h still not found at {IMGUI_DIR / 'imgui.h'}")
        print("  The clone may have failed or the URL was wrong.")
        sys.exit(1)
    if not (DB_DIR / "dear_bindings.py").exists():
        print(f"ERROR: dear_bindings.py still not found at {DB_DIR / 'dear_bindings.py'}")
        print("  The clone may have failed or the URL was wrong.")
        sys.exit(1)

    print("  imgui         OK")
    print("  dear_bindings OK")

def step_venv():
    """Create venv and install dear_bindings requirements."""
    if not VENV_DIR.exists():
        print(f"\n[1/5] Creating venv at {VENV_DIR}")
        venv.create(str(VENV_DIR), with_pip=True)
    else:
        print(f"\n[1/5] Venv already exists, skipping creation")

    requirements = DB_DIR / "requirements.txt"
    if requirements.exists():
        run([str(VENV_PIP), "install", "-r", str(requirements), "-q"])
    else:
        print("  No requirements.txt found in dear_bindings, skipping pip install")

def step_generate_bindings():
    """Run dear_bindings to generate dcimgui + opengl2 backend."""
    print("\n[2/5] Generating C bindings with dear_bindings")
    DB_GENERATED.mkdir(parents=True, exist_ok=True)
    (DB_GENERATED / "backends").mkdir(parents=True, exist_ok=True)

    imgui_h  = IMGUI_DIR / "imgui.h"
    imconfig = IMGUI_DIR / "imconfig.h"
    if not imconfig.exists():
        print(f"ERROR: imconfig.h not found at {imconfig}")
        print("  This file should be part of the imgui source.")
        sys.exit(1)

    # Main imgui.h
    run([str(VENV_PYTHON), str(DB_DIR / "dear_bindings.py"),
         "-o", str(DB_GENERATED / "dcimgui"),
         str(imgui_h)], cwd=DB_DIR)

    # imgui_internal.h (optional)
    internal_h = IMGUI_DIR / "imgui_internal.h"
    if internal_h.exists():
        run([str(VENV_PYTHON), str(DB_DIR / "dear_bindings.py"),
             "-o", str(DB_GENERATED / "dcimgui_internal"),
             "--include", str(imgui_h),
             str(internal_h)], cwd=DB_DIR)

    # opengl2 backend only
    for backend in BACKENDS:
        backend_h = IMGUI_DIR / "backends" / f"imgui_impl_{backend}.h"
        if not backend_h.exists():
            print(f"  ERROR: Backend header not found: {backend_h}")
            sys.exit(1)
        print(f"\n  Processing backend: {backend}")
        run([str(VENV_PYTHON), str(DB_DIR / "dear_bindings.py"),
             "--backend",
             "--include",       str(imgui_h),
             "--imconfig-path", str(imconfig),
             "-o", str(DB_GENERATED / "backends" / f"dcimgui_impl_{backend}"),
             str(backend_h)], cwd=DB_DIR)

def step_compile(java_home):
    """Compile the JNI DLL/so/dylib."""
    print(f"\n[3/5] Compiling {DLL_NAME}")

    CXX          = find_64bit_gxx()
    backends_src = IMGUI_DIR / "backends"
    db_backends  = DB_GENERATED / "backends"

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    sources = [
        str(IMGUI_DIR / "imgui.cpp"),
        str(IMGUI_DIR / "imgui_draw.cpp"),
        str(IMGUI_DIR / "imgui_widgets.cpp"),
        str(IMGUI_DIR / "imgui_tables.cpp"),
        str(IMGUI_DIR / "imgui_demo.cpp"),
        str(backends_src / "imgui_impl_opengl2.cpp"),
        str(DB_GENERATED / "dcimgui.cpp"),
        str(SRC / "dcimgui_impl.cpp"),
        str(db_backends / "dcimgui_impl_opengl2.cpp"),
        str(SRC / "imgui_jni.cpp"),
    ]

    missing = [s for s in sources if not Path(s).exists()]
    if missing:
        print("ERROR: Missing source files:")
        for m in missing:
            print(f"  {m}")
        print("\nTip: run without --skip-bindings to generate missing files.")
        sys.exit(1)

    includes = [
        f"-I{IMGUI_DIR}",
        f"-I{backends_src}",
        f"-I{DB_GENERATED}",
        f"-I{db_backends}",
        f"-I{java_home / 'include'}",
        f"-I{java_home / 'include' / JNI_PLATFORM_INC}",
    ]

    cmd = (
        [CXX, "-shared"]
        + PLATFORM_FLAGS
        + ["-o", str(OUT_DIR / DLL_NAME)]
        + sources
        + includes
        + LINK_FLAGS
    )

    run(cmd)
    print(f"\n  Native output: {OUT_DIR / DLL_NAME}")

def step_build_jar(java_home):
    """Compile ImGui.java + Input.java into imgui-lwjgl2-jni.jar."""
    print("\n[4/5] Building imgui-lwjgl2-jni.jar")

    out_classes = OUT_DIR / "classes"
    out_classes.mkdir(parents=True, exist_ok=True)

    java_files = list(JAVA_SRC_DIR.rglob("*.java"))
    if not java_files:
        print(f"ERROR: No .java files found in {JAVA_SRC_DIR}")
        print("  Expected ImGui.java and Input.java in src/java/imgui/")
        sys.exit(1)

    print(f"  Found {len(java_files)} Java source file(s):")
    for f in java_files:
        print(f"    {f.relative_to(ROOT)}")

    # Find LWJGL jar for compilation classpath
    lwjgl_jar = ROOT / "lib" / "lwjgl.jar"
    if not lwjgl_jar.exists():
        # Try to find it anywhere under lib/
        candidates = list((ROOT / "lib").rglob("lwjgl*.jar")) if (ROOT / "lib").exists() else []
        if candidates:
            lwjgl_jar = candidates[0]
            print(f"  Using LWJGL jar: {lwjgl_jar.relative_to(ROOT)}")
        else:
            print("ERROR: lwjgl.jar not found in lib/")
            print("  Place your LWJGL 2.9.3 jar at lib/lwjgl.jar")
            sys.exit(1)

    javac = java_home / "bin" / ("javac.exe" if SYSTEM == "Windows" else "javac")
    jar   = java_home / "bin" / ("jar.exe"   if SYSTEM == "Windows" else "jar")

    # Compile
    run([
        str(javac),
        "-source", "1.6",
        "-target", "1.6",
        "-cp", str(lwjgl_jar),
        "-d", str(out_classes),
    ] + [str(f) for f in java_files])

    # Package
    jar_out = OUT_DIR / "imgui-lwjgl2-jni.jar"
    run([
        str(jar), "cf", str(jar_out),
        "-C", str(out_classes), "."
    ])

    shutil.rmtree(out_classes)

    print(f"\n  JAR output: {jar_out}")

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Build imgui-lwjgl2-jni")
    parser.add_argument("--skip-bindings", action="store_true",
                        help="Skip dear_bindings generation (use existing generated files)")
    parser.add_argument("--skip-compile",  action="store_true",
                        help="Skip native DLL/so/dylib compilation")
    parser.add_argument("--skip-jar",      action="store_true",
                        help="Skip JAR compilation")
    args = parser.parse_args()

    print("imgui-lwjgl2-jni build script")
    print(f"Platform : {SYSTEM}")
    print(f"Output   : {DLL_NAME}")

    # Always check sources first — offer to clone if missing
    step_check_sources()

    java_home = check_java_home()

    if not args.skip_bindings:
        step_venv()
        step_generate_bindings()
    else:
        print("\n[1-2/5] Skipping venv + binding generation")

    if not args.skip_compile:
        step_compile(java_home)
    else:
        print(f"\n[3/5] Skipping {DLL_NAME} compilation")

    if not args.skip_jar:
        step_build_jar(java_home)
    else:
        print("\n[4/5] Skipping JAR compilation")

    print("\n── Build complete ──")
    print(f"  {OUT_DIR / DLL_NAME}")
    print(f"  {OUT_DIR / 'imgui-lwjgl2-jni.jar'}")

if __name__ == "__main__":
    main()