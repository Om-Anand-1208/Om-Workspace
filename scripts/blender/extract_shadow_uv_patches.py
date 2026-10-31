"""Extract audited UV islands that still contain removed-prop shadows."""

from pathlib import Path

from PIL import Image


ROOT = Path("/home/psykr/Projects/Om-Portfolio")
SOURCE = ROOT / "blender/textures/bakedDay-no-octopus.png"
OUTPUT = ROOT / "blender/texture-patches/shadow-cleanup"
PADDING = 36

PATCHES = {
    "office_wall": ((0.6002412438, 0.0013356805), (0.8455513716, 0.3794104457)),
    "shelf_top": ((0.2267949432, 0.4878146052), (0.3179031610, 0.5733199120)),
    "sofa_base": ((0.3739323020, 0.5058413744), (0.4555399418, 0.5988984704)),
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
