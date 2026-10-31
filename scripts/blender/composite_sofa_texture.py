"""Composite approved shadow-cleaned UV patches into a new baked atlas."""

from pathlib import Path

from PIL import Image, ImageFilter


ROOT = Path("/home/psykr/Projects/Om-Portfolio")
SOURCE = Path("/home/psykr/Projects/my-room-in-3d/static/assets/bakedDay.jpg")
OUTPUT = ROOT / "blender/textures/bakedDay-no-octopus.png"
PADDING = 20

PATCHES = {
    "0009": {
        "uv": ((0.001217, 0.517778), (0.094274, 0.599142)),
        "path": ROOT / "blender/texture-patches/sofa_uv_0009_clean.png",
    },
    "0013": {
        "uv": ((0.467233, 0.581846), (0.515710, 0.614002)),
        "path": ROOT / "blender/texture-patches/sofa_uv_0013_clean.png",
    },
    "0014": {
        "uv": ((0.491837, 0.021311), (0.536904, 0.032517)),
        "path": ROOT / "blender/texture-patches/sofa_uv_0014_clean.png",
    },
    "0016": {
        "uv": ((0.701581, 0.407669), (0.707915, 0.430568)),
        "path": ROOT / "blender/texture-patches/sofa_uv_0016_clean.png",
    },
    "0017": {
        "uv": ((0.529109, 0.601822), (0.562726, 0.690981)),
        "path": ROOT / "blender/texture-patches/sofa_uv_0017_clean.png",
    },
    "0018": {
        "uv": ((0.516198, 0.587936), (0.521800, 0.613028)),
        "path": ROOT / "blender/texture-patches/sofa_uv_0018_clean.png",
    },
    "0019": {
        "uv": ((0.217294, 0.638119), (0.231423, 0.728740)),
        "path": ROOT / "blender/texture-patches/sofa_uv_0019_clean.png",
    },
    "0031": {
        "uv": ((0.236052, 0.405720), (0.365163, 0.483917)),
        "path": ROOT / "blender/texture-patches/sofa_uv_0031_clean.png",
    },
}


atlas = Image.open(SOURCE).convert("RGB")
width, height = atlas.size

for name, spec in PATCHES.items():
    (u0, v0), (u1, v1) = spec["uv"]
    uv_x0 = int(u0 * width)
    uv_x1 = int(u1 * width)
    uv_y0 = int((1.0 - v1) * height)
    uv_y1 = int((1.0 - v0) * height)

    crop_x0 = max(0, uv_x0 - PADDING)
    crop_x1 = min(width, uv_x1 + PADDING)
    crop_y0 = max(0, uv_y0 - PADDING)
    crop_y1 = min(height, uv_y1 + PADDING)
    crop_size = (crop_x1 - crop_x0, crop_y1 - crop_y0)

    generated = Image.open(spec["path"]).convert("RGB")
    generated = generated.resize(crop_size, Image.Resampling.LANCZOS)

    source_box = (
        uv_x0 - crop_x0,
        uv_y0 - crop_y0,
        uv_x1 - crop_x0,
        uv_y1 - crop_y0,
    )
    replacement = generated.crop(source_box)

    # A small feather keeps the retouched island continuous with its original
    # baked border without modifying neighbouring atlas islands.
    mask = Image.new("L", replacement.size, 255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=1.5))
    atlas.paste(replacement, (uv_x0, uv_y0), mask)
    print(f"composited {name}: {(uv_x0, uv_y0, uv_x1, uv_y1)}")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
atlas.save(OUTPUT, format="PNG", optimize=True)
print(OUTPUT)
