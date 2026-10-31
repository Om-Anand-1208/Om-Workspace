import bpy, os, math
from mathutils import Vector
root=os.path.abspath(os.path.join(os.path.dirname(__file__),'../..'))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=os.path.join(root,'public/assets/original-room-latest.glb'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
coords=[o.matrix_world @ Vector(corner) for o in meshes for corner in o.bound_box]
low=Vector(tuple(min(v[i] for v in coords) for i in range(3))); high=Vector(tuple(max(v[i] for v in coords) for i in range(3))); center=(low+high)*.5
print('BOUNDS',low[:],high[:],center[:])
bpy.ops.object.camera_add(location=center+Vector((-18,-18,13))); camera=bpy.context.object; camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler(); camera.data.type='ORTHO'; camera.data.ortho_scale=18; bpy.context.scene.camera=camera
world=bpy.context.scene.world; world.color=(0.04,0.05,0.05)
bpy.ops.object.light_add(type='AREA', location=center+Vector((-4,-5,12))); light=bpy.context.object; light.data.energy=1800; light.data.shape='DISK'; light.data.size=12
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=24; scene.render.resolution_x=600; scene.render.resolution_y=450; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(root,'public/projects/Om-Portfolio.png'); bpy.ops.render.render(write_still=True)
