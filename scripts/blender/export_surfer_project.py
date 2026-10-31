"""Export the SurferFlow portfolio diorama without the studio backdrop.

Run with: blender -b blender/surferflow_reference_kit/generated_candidate/SurferFlow_Diorama.blend --python scripts/blender/export_surfer_project.py
The original blend remains unchanged; a scaled editable copy is saved alongside exports.
"""
import bpy
import os
from mathutils import Vector

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
output = os.path.join(root, 'public', 'projects')
os.makedirs(output, exist_ok=True)
scene = bpy.context.scene
# The ground is a 200-unit photography backdrop. Including it made the web
# model dwarf its camera and obscured the object. Curves are needed for the
# wave highlight and ripples and are converted by the glTF exporter.
objects = [o for o in scene.objects if o.type in {'MESH', 'CURVE'} and o.name != 'Peach_Studio_Ground' and not o.hide_render]
bpy.ops.object.select_all(action='DESELECT')
scale = 0.4
for o in objects:
    o.location *= scale
    o.scale *= scale
    o.select_set(True)
bpy.context.view_layer.objects.active = objects[0]
bpy.ops.export_scene.gltf(filepath=os.path.join(output, 'SurferFlow.glb'), export_format='GLB', use_selection=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(root, 'blender', 'SurferFlow-portfolio-diorama.blend'))
print('Exported', len(objects), 'objects; excluded studio ground, included wave curves.')
