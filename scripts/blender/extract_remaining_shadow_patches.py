"""Extract the marked floor-shadow and coffee-table UV receivers."""

from pathlib import Path

from PIL import Image


ROOT = Path("/home/psykr/Projects/Om-Portfolio")
SOURCE = ROOT / "blender/textures/bakedDay-shadow-clean-v4.png"
OUTPUT = ROOT / "blender/texture-patches/shadow-cleanup"
PADDING = 24

PATCHES = {
    "floor_0108": ((0.367842, 0.408643), (0.383676, 0.467352)),
    "floor_0109": ((0.828499, 0.641042), (0.845064, 0.754318)),
    "floor_0120": ((0.917171, 0.001336), (0.932762, 0.072225)),
    "floor_0121": ((0.279170, 0.893417), (0.358585, 0.908764)),
    "floor_0122": ((0.469182, 0.977460), (0.480388, 0.994513)),
    "floor_0128": ((0.449450, 0.623015), (0.466502, 0.742625)),
    "coffee_table_circle": ((0.375881, 0.603283), (0.403408, 0.709982)),
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
