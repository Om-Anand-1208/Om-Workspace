"""Replace the packed bakedDay atlas with the approved cleaned sofa atlas."""

from pathlib import Path

import bpy


texture_path = Path(
    "/home/psykr/Projects/Om-Portfolio/blender/textures/bakedDay-no-octopus.png"
)
if not texture_path.is_file():
    raise FileNotFoundError(texture_path)

previous_baked_images = [
    image for image in bpy.data.images if image.name.startswith("bakedDay")
]
cleaned = bpy.data.images.load(str(texture_path), check_existing=False)
cleaned.name = "bakedDay-no-octopus-v2.png"

replaced = 0
for material in bpy.data.materials:
    if not material.use_nodes or material.node_tree is None:
        continue
    for node in material.node_tree.nodes:
        if node.type != "TEX_IMAGE" or node.image is None:
            continue
        if node.image.name.startswith("bakedDay"):
            node.image = cleaned
            replaced += 1

if replaced == 0:
    raise RuntimeError("No bakedDay.jpg material nodes were found")

cleaned.pack()
for image in previous_baked_images:
    if image.users == 0:
        bpy.data.images.remove(image)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath, check_existing=False, compress=True)
print(f"REPLACED_BAKED_TEXTURE_NODES={replaced}")
print(f"PACKED_TEXTURE={cleaned.name}")
