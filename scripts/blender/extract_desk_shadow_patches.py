"""Extract the two desktop UV islands containing removed-object shadows."""

from pathlib import Path

from PIL import Image


ROOT = Path("/home/psykr/Projects/Om-Portfolio")
SOURCE = ROOT / "blender/textures/bakedDay-shadow-clean-v5.png"
OUTPUT = ROOT / "blender/texture-patches/shadow-cleanup"
PADDING = 32

PATCHES = {
    "desk_main_top": ((0.001217, 0.252980), (0.069913, 0.514368)),
    "desk_monitor_shelf": ((0.602434, 0.455659), (0.731544, 0.489763)),
}

atlas = Image.open(SOURCE).convert("RGB")
width, height = atlas.size
OUTPUT.mkdir(parents=True, exist_ok=True)

for name, ((u0, v0), (u1, v1)) in PATCHES.items():
    x0 = max(0, int(u0 * width) - PADDING)
    x1 = min(width, int(u1 * width) + PADDING)
    y0 = max(0, int((1.0 - v1) * height) - PADDING)
    y1 = min(height, int((1.0 - v0) * height) + PADDING)
    destination = OUTPUT / f"{name}-source.png"
    atlas.crop((x0, y0, x1, y1)).save(destination, optimize=True)
    print(name, destination, (x0, y0, x1, y1), destination.stat().st_size)
