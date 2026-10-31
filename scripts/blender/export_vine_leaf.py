"""Extract one textured leaf from the CC0 plant model for the room garland."""
import bpy, bmesh, numpy as np
from pathlib import Path
root=Path(__file__).resolve().parents[2]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(root/'public/assets/potted-plant-web.glb'))
leaf=next(o for o in bpy.context.scene.objects if o.type=='MESH' and 'leaves' in o.name.lower())
bm=bmesh.new();bm.from_mesh(leaf.data);bm.verts.ensure_lookup_table();bm.verts.index_update()
seen=set(); groups=[]
for v in bm.verts:
 if v.index in seen:continue
 stack=[v];seen.add(v.index);group=[]
 while stack:
  current=stack.pop();group.append(current)
  for edge in current.link_edges:
   other=edge.other_vert(current)
   if other.index not in seen:seen.add(other.index);stack.append(other)
 if len(group)>100:groups.append(group)
# A large leaf, selected by its surface extent, with the original UV coordinates.
group=max(groups,key=lambda g: np.linalg.norm(np.ptp(np.array([v.co[:] for v in g]),axis=0)))
keep=set(group); bmesh.ops.delete(bm,geom=[v for v in bm.verts if v not in keep],context='VERTS')
coords=np.array([v.co[:] for v in bm.verts]); center=coords.mean(axis=0); vals,vecs=np.linalg.eigh(np.cov((coords-center).T)); order=np.argsort(vals)[::-1]; long,wide,normal=vecs[:,order].T
length=np.ptp((coords-center)@long); scale=.27/length
for v in bm.verts:
 p=np.array(v.co[:])-center; v.co=(float(p@wide*scale),float(p@long*scale),float(p@normal*scale))
bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(leaf.data);bm.free();leaf.data.update()
leaf.parent=None;leaf.location=(0,0,0);leaf.rotation_euler=(0,0,0);leaf.scale=(1,1,1)
bpy.ops.object.select_all(action='DESELECT');leaf.select_set(True);bpy.context.view_layer.objects.active=leaf
bpy.ops.export_scene.gltf(filepath=str(root/'public/assets/vine-leaf.glb'),export_format='GLB',use_selection=True,export_yup=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
print('EXTRACTED',len(leaf.data.vertices),'vertices')
