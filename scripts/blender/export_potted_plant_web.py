"""Resize the existing CC0 plant for the room; retain the original source file."""
import bpy
from pathlib import Path
root=Path(__file__).resolve().parents[2]
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(root/'blender/assets/potted-plant.glb'))
for image in bpy.data.images:
    if image.size[0] > 512 and image.size[1] > 512:
        image.scale(512,512)
        image.pack()
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(root/'public/assets/potted-plant-web.glb'),export_format='GLB',use_selection=True,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
