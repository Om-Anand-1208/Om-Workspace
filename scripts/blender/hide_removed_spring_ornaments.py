"""Hide the three shelf spring ornaments while keeping them recoverable.

The web exporter only includes visible, render-enabled meshes. Keeping the
source pieces hidden instead of deleting them makes this edit reversible.
"""

from pathlib import Path

import bpy


ROOT = Path("/home/psykr/Projects/Om-Portfolio")
MASTER = ROOT / "blender/original-room-editable-master.blend"
ORNAMENT_OBJECTS = (
    "Shelf_0179",
    "Shelf_0180",
    "Shelf_0182",
    "Shelf_0183",
    "Shelf_0184",
    "Shelf_0185",
    "Shelf_0186",
    "Shelf_0187",
    "Shelf_0188",
    "Shelf_0189",
    "Shelf_0190",
    "Shelf_0191",
    "Shelf_0192",
    "Shelf_0193",
    "Shelf_0194",
)

if Path(bpy.data.filepath).resolve() != MASTER.resolve():
    raise RuntimeError(f"Expected {MASTER}, opened {bpy.data.filepath}")

missing = [name for name in ORNAMENT_OBJECTS if bpy.data.objects.get(name) is None]
if missing:
    raise RuntimeError(f"Missing spring ornament pieces: {missing}")

for name in ORNAMENT_OBJECTS:
    obj = bpy.data.objects[name]
    obj.hide_render = True
    obj.hide_viewport = True
    obj.hide_set(True)
    obj["om_removed_reason"] = "Removed shelf spring ornament"

bpy.ops.wm.save_as_mainfile(
    filepath=str(MASTER),
    check_existing=False,
    compress=True,
)

hidden = [
    name
    for name in ORNAMENT_OBJECTS
    if bpy.data.objects[name].hide_render and bpy.data.objects[name].hide_viewport
]
print(f"SPRING_ORNAMENT_PIECES={len(ORNAMENT_OBJECTS)}")
print(f"HIDDEN_PIECES={len(hidden)}")
print("HIDDEN_NAMES=" + ",".join(hidden))
