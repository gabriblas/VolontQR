import re
import shutil
import sys
from pathlib import Path

from nicegui.scripts.pack import main

ROOT = Path(__file__).parent.resolve()
BUILD = ROOT / "build"
DIST = ROOT / "dist"

if BUILD.exists() and input(f"Remove {BUILD}? [y/N] ") == "y":
    shutil.rmtree(BUILD)
if DIST.exists() and input(f"Remove {DIST}? [y/N] ") == "y":
    shutil.rmtree(DIST)

sys.argv += ["--onefile"]  # slower to load, but only one file
sys.argv += ["--windowed"]  # do not show terminal

if (ROOT / "logos").exists():
    sys.argv += ["--icon=logos/logo.ico"]

sys.argv += ["--name", "VolontQR"]
sys.argv += ["main.py"]

if __name__ == "__main__":
    sys.argv[0] = re.sub(r"(-script\.pyw|\.exe)?$", "", sys.argv[0])
    sys.exit(main())
