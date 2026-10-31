"""Export the latest editable room master as a compact website GLB.

Run with Blender in background mode against original-room-editable-master.blend.
The source file is never saved: visible baked pieces are duplicated into a
temporary scene, joined for web performance, and exported with Draco.
"""

from pathlib import Path

import bpy


ROOT = Path("/home/psykr/Projects/Om-Portfolio")
SOURCE = ROOT / "blender/original-room-editable-master.blend"
OUTPUT = ROOT / "public/assets/room-sofa-shifted.glb"


def flat_screen_material(name: str, color: tuple[float, float, float, float]):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    principled = next(
        node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED"
    )
    principled.inputs["Base Color"].default_value = color
    principled.inputs["Roughness"].default_value = 0.55
    if "Emission Color" in principled.inputs:
        principled.inputs["Emission Color"].default_value = color
        principled.inputs["Emission Strength"].default_value = 0.35
    return material


source_path = Path(bpy.data.filepath).resolve()
if source_path != SOURCE.resolve():
    raise RuntimeError(f"Expected {SOURCE}, opened {source_path}")

source_scene = bpy.context.scene
source_view_layer = bpy.context.view_layer
source_meshes = [
    obj
    for obj in source_scene.objects
    if obj.type == "MESH"
    and obj.visible_get(view_layer=source_view_layer)
    and not obj.hide_render
]
if not source_meshes:
    raise RuntimeError("No visible room meshes found")

export_scene = bpy.data.scenes.new("WEB_EXPORT_SCENE")
bpy.context.window.scene = export_scene
export_collection = bpy.data.collections.new("WEB_EXPORT")
export_scene.collection.children.link(export_collection)

duplicates: list[bpy.types.Object] = []
for source in source_meshes:
    duplicate = source.copy()
    duplicate.data = source.data.copy()
    duplicate.animation_data_clear()
    duplicate.parent = None
    duplicate.matrix_world = source.matrix_world.copy()
    # Shift the sofa toward the workstation while leaving floorboards in place.
    if source.name in {'Architecture_0007', 'Architecture_0008'}:
        duplicate.matrix_world.translation.y += 0.38
    if source.name.startswith('LivingSeating_'):
        try:
            number = int(source.name.rsplit('_', 1)[1])
        except ValueError:
            number = -1
        if 9 <= number <= 32:
            duplicate.matrix_world.translation.y += 0.38
    export_collection.objects.link(duplicate)
    duplicates.append(duplicate)

monitor_material = flat_screen_material(
    "WEB_Monitor_Screen", (0.018, 0.035, 0.055, 1.0)
)
laptop_material = flat_screen_material(
    "WEB_Laptop_Screen", (0.055, 0.035, 0.075, 1.0)
)

for duplicate in duplicates:
    if duplicate.name == "Monitor_Screen_Dynamic":
        duplicate.data.materials.clear()
        duplicate.data.materials.append(monitor_material)
    elif duplicate.name == "Laptop_Screen_Dynamic":
        duplicate.data.materials.clear()
        duplicate.data.materials.append(laptop_material)

baked = [
    obj
    for obj in duplicates
    if len(obj.data.materials) == 1
    and obj.data.materials[0]
    and obj.data.materials[0].name == "SRC_Baked_Day"
]
if len(baked) < 500:
    raise RuntimeError(f"Expected the baked room pieces, found only {len(baked)}")

bpy.ops.object.select_all(action="DESELECT")
for obj in baked:
    obj.select_set(True)
bpy.context.view_layer.objects.active = baked[0]
bpy.ops.object.join()
room = bpy.context.view_layer.objects.active
room.name = "Room_Baked"
room.data.name = "Room_Baked_Mesh"

export_objects = [obj for obj in export_scene.objects if obj.type == "MESH"]
bpy.ops.object.select_all(action="DESELECT")
for obj in export_objects:
    obj.select_set(True)
bpy.context.view_layer.objects.active = room

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.export_scene.gltf(
    filepath=str(OUTPUT),
    export_format="GLB",
    use_selection=True,
    export_apply=True,
    export_texcoords=True,
    export_normals=True,
    export_tangents=False,
    export_materials="EXPORT",
    export_image_format="AUTO",
    export_unused_images=False,
    export_cameras=False,
    export_lights=False,
    export_animations=False,
    export_morph=False,
    export_skins=False,
    export_extras=False,
    export_yup=True,
    export_draco_mesh_compression_enable=True,
    export_draco_mesh_compression_level=6,
)

print(f"SOURCE_VISIBLE_MESHES={len(source_meshes)}")
print(f"JOINED_BAKED_MESHES={len(baked)}")
print(f"EXPORTED_MESH_OBJECTS={len(export_objects)}")
print(f"OUTPUT={OUTPUT}")
print(f"OUTPUT_BYTES={OUTPUT.stat().st_size}")
