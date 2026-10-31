"""Extract the two UV receivers containing the removed guitar's baked shadow."""

from pathlib import Path

from PIL import Image


ROOT = Path("/home/psykr/Projects/Om-Portfolio")
SOURCE = ROOT / "blender/textures/bakedDay-shadow-clean-v3.png"
OUTPUT = ROOT / "blender/texture-patches/shadow-cleanup"
PADDING = 36

PATCHES = {
    "guitar_cabinet_side": ((0.531545, 0.323625), (0.597318, 0.392565)),
    "guitar_floor": ((0.660168, 0.730932), (0.675759, 0.851030)),
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
