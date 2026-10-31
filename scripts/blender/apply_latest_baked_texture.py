"""Pack the latest shadow-cleaned baked atlas into the editable room master."""

from pathlib import Path

import bpy


ROOT = Path("/home/psykr/Projects/Om-Portfolio")
TEXTURE = ROOT / "blender/textures/bakedDay-shadow-clean-v8.png"
MATERIAL = "SRC_Baked_Day"

if not TEXTURE.exists():
    raise FileNotFoundError(TEXTURE)

cleaned = bpy.data.images.load(str(TEXTURE), check_existing=False)
cleaned.name = "bakedDay-shadow-clean-v8.png"
cleaned.pack()

material = bpy.data.materials.get(MATERIAL)
if material is None or not material.use_nodes or material.node_tree is None:
    raise RuntimeError(f"Missing node material: {MATERIAL}")

replaced = 0
for node in material.node_tree.nodes:
    if node.type == "TEX_IMAGE":
        node.image = cleaned
        node.interpolation = "Linear"
        replaced += 1

if replaced == 0:
    raise RuntimeError(f"No image nodes found in {MATERIAL}")

bpy.ops.wm.save_as_mainfile(
    filepath=bpy.data.filepath,
    check_existing=False,
    compress=True,
)
print(f"REPLACED_TEXTURE_NODES={replaced}")
print(f"PACKED_TEXTURE={cleaned.name}")
