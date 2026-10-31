"""Composite verified removed-prop shadow repairs into a versioned atlas."""

from pathlib import Path

from PIL import Image, ImageFilter


ROOT = Path("/home/psykr/Projects/Om-Portfolio")
SOURCE = ROOT / "blender/textures/bakedDay-shadow-clean-v7.png"
OUTPUT = ROOT / "blender/textures/bakedDay-shadow-clean-v8.png"
PATCHES = {
    "floor_shelf_0267": {
        "uv": ((0.340071, 0.845183), (0.431910, 0.861261)),
        "path": ROOT / "blender/texture-patches/shadow-cleanup/floor_Shelf_0267-clean.png",
        "generated_crop": (0.018, 0.207, 0.940, 0.690),
    },
    "floor_shelf_0268": {
        "uv": ((0.215589, 0.748959), (0.231180, 0.868082)),
        "path": ROOT / "blender/texture-patches/shadow-cleanup/floor_Shelf_0268-clean.png",
        "generated_crop": (0.283, 0.025, 0.655, 0.974),
    },
    "floor_decor_0028": {
        "uv": ((0.771983, 0.741164), (0.787573, 0.860043)),
        "path": ROOT / "blender/texture-patches/shadow-cleanup/floor_Decor_0028-clean.png",
        "generated_crop": (0.276, 0.025, 0.655, 0.974),
    },
    "floor_decor_0029": {
        "uv": ((0.711325, 0.664915), (0.727159, 0.784769)),
        "path": ROOT / "blender/texture-patches/shadow-cleanup/floor_Decor_0029-clean.png",
        "generated_crop": (0.276, 0.025, 0.658, 0.972),
    },
    "floor_decor_0030": {
        "uv": ((0.517172, 0.692930), (0.532763, 0.812784)),
        "path": ROOT / "blender/texture-patches/shadow-cleanup/floor_Decor_0030-clean.png",
        "generated_crop": (0.283, 0.025, 0.658, 0.972),
    },
    "floor_decor_0031": {
        "uv": ((0.356393, 0.713149), (0.372227, 0.828861)),
        "path": ROOT / "blender/texture-patches/shadow-cleanup/floor_Decor_0031-clean.png",
        "generated_crop": (0.262, 0.025, 0.655, 0.968),
    },
    "floor_decor_0032": {
        "uv": ((0.850180, 0.641042), (0.866258, 0.757485)),
        "path": ROOT / "blender/texture-patches/shadow-cleanup/floor_Decor_0032-clean.png",
        "generated_crop": (0.262, 0.025, 0.654, 0.971),
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

    generated = Image.open(spec["path"]).convert("RGB")
    gx0, gy0, gx1, gy1 = spec["generated_crop"]
    generated_box = (
        int(gx0 * generated.width),
        int(gy0 * generated.height),
        int(gx1 * generated.width),
        int(gy1 * generated.height),
    )
    replacement = generated.crop(generated_box).resize(
        (uv_x1 - uv_x0, uv_y1 - uv_y0), Image.Resampling.LANCZOS
    )

    mask = Image.new("L", replacement.size, 255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=1.5))
    atlas.paste(replacement, (uv_x0, uv_y0), mask)
    print(f"composited {name}: {(uv_x0, uv_y0, uv_x1, uv_y1)}")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
atlas.save(OUTPUT, format="PNG", optimize=True)
print(OUTPUT)

