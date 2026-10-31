"""Replace near-black floor-board side UVs with subtle warm wood samples.

The cleaned top faces remain unchanged. Original side-face UV coordinates are
stored on each object so this seam adjustment can be reversed later.
"""

import json
from pathlib import Path

import bpy


ROOT = Path("/home/psykr/Projects/Om-Portfolio")
MASTER = ROOT / "blender/original-room-editable-master.blend"
BOARD_TOP_UV_BOUNDS = {
    "Shelf_0267": ((0.340071, 0.845183), (0.431910, 0.861261)),
    "Shelf_0268": ((0.215589, 0.748959), (0.231180, 0.868082)),
    "Decor_0028": ((0.771983, 0.741164), (0.787573, 0.860043)),
    "Decor_0029": ((0.711325, 0.664915), (0.727159, 0.784769)),
    "Decor_0030": ((0.517172, 0.692930), (0.532763, 0.812784)),
    "Decor_0031": ((0.356393, 0.713149), (0.372227, 0.828861)),
    "Decor_0032": ((0.850180, 0.641042), (0.866258, 0.757485)),
}
BACKUP_KEY = "om_floor_seam_uv_backup_v8"

if Path(bpy.data.filepath).resolve() != MASTER.resolve():
    raise RuntimeError(f"Expected {MASTER}, opened {bpy.data.filepath}")

missing = [name for name in BOARD_TOP_UV_BOUNDS if bpy.data.objects.get(name) is None]
if missing:
    raise RuntimeError(f"Missing floor boards: {missing}")

total_faces = 0
total_loops = 0
for name, ((u0, v0), (u1, v1)) in BOARD_TOP_UV_BOUNDS.items():
    obj = bpy.data.objects[name]
    uv_layer = obj.data.uv_layers.active
    if uv_layer is None:
        raise RuntimeError(f"No active UV map on {name}")

    side_polygons = []
    for polygon in obj.data.polygons:
        world_normal = (obj.matrix_world.to_3x3() @ polygon.normal).normalized()
        if world_normal.z < 0.9:
            side_polygons.append(polygon)

    if BACKUP_KEY not in obj:
        backup = {
            str(loop_index): [
                float(uv_layer.data[loop_index].uv.x),
                float(uv_layer.data[loop_index].uv.y),
            ]
            for polygon in side_polygons
            for loop_index in polygon.loop_indices
        }
        obj[BACKUP_KEY] = json.dumps(backup, separators=(",", ":"))

    center_u = (u0 + u1) * 0.5
    center_v = (v0 + v1) * 0.5
    epsilon = 0.00035
    offsets = (
        (-epsilon, -epsilon),
        (epsilon, -epsilon),
        (epsilon, epsilon),
        (-epsilon, epsilon),
    )
    for polygon in side_polygons:
        for index, loop_index in enumerate(polygon.loop_indices):
            du, dv = offsets[index % len(offsets)]
            uv_layer.data[loop_index].uv = (center_u + du, center_v + dv)
            total_loops += 1
        total_faces += 1

    obj["om_floor_seams_softened"] = True

bpy.ops.wm.save_as_mainfile(
    filepath=str(MASTER),
    check_existing=False,
    compress=True,
)

print(f"SOFTENED_BOARDS={len(BOARD_TOP_UV_BOUNDS)}")
print(f"REMAPPED_SIDE_FACES={total_faces}")
print(f"REMAPPED_UV_LOOPS={total_loops}")
