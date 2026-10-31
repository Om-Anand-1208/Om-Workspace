"""Remove the annotated props from the exact room GLB used by the website.

Blender imports the Draco-compressed GLB as a single mesh. The prop islands
are identified by their contiguous vertex spans in that mesh, so this script
removes their faces directly without splitting thousands of duplicate vertices.
The camera can fragment into many tiny islands after Draco export, so a second
pass removes the connected components in its known local-space cluster.
"""

import bpy
import bmesh
from mathutils import Vector

ROOM_GLB = "/home/psykr/Projects/Om-Portfolio/public/assets/roomModel-simplified.glb"
ROOM_BLEND = "/home/psykr/Projects/Om-Portfolio/blender/om-portfolio-room-cleaned.blend"
SOURCE_VERTEX_COUNT = 258596
PRE_CAMERA_CLEANED_VERTEX_COUNT = 190001
FINAL_CLEANED_VERTEX_COUNT = 184371
KNOWN_VERTEX_COUNTS = {
    SOURCE_VERTEX_COUNT,
    PRE_CAMERA_CLEANED_VERTEX_COUNT,
    FINAL_CLEANED_VERTEX_COUNT,
}

# Draco splits both assemblies into disconnected islands. Bounds are in
# mesh-local coordinates before applying the imported object's root transform.
TARGET_COMPONENT_CLUSTERS = {
    "wall camera and bracket": ((3.55, 1.80, -0.60), (4.50, 3.30, 1.00)),
    "desk microphone and supports": ((3.51, 3.20, -1.28), (4.03, 4.03, -0.96)),
}
MICROPHONE_WORLD_BOUNDS = ((0.9044, 4.0564, 1.9561), (1.5996, 4.4697, 2.1137))

# These two loose islands are the laptop's original screen frame and keyboard
# deck. They were removed in an earlier pass; restore them from the matching
# source room asset, whose baked texture and world transform match the website.
SOURCE_ROOM_GLB = "/home/psykr/Projects/my-room-in-3d/static/assets/roomModel.glb"
LAPTOP_PART_POLYGON_RANGES = {
    "laptop screen frame": (55800, 55915),
    "laptop keyboard deck": (55916, 56025),
}

# Inclusive vertex ranges from the exact website GLB, checked against their
# world-space bounds in the imported Blender mesh.
PROP_SPANS = {
    "shelf figures": [
        (204573, 207044), (207045, 209516), (209517, 211982),
        (211983, 214454), (214455, 216924), (216925, 219386),
        (219387, 221856), (221857, 224326), (224327, 226798),
        (226799, 229270), (229271, 231742), (231743, 234210),
    ],
    "oval wall panel": [(144551, 145126)],
    "desk microphone and nearby support": [
        (138328, 138853), (140026, 140509), (140510, 140703),
        (141232, 141267), (150873, 155018),
    ],
    "wall camera and bracket": [
        (159189, 159816), (160445, 161068), (162943, 163562),
        (170749, 171164),
        (171165, 173318), (173319, 175474),
        (175475, 177630), (177631, 179788),
        (179789, 181944), (181945, 184100),
        (184101, 186260), (186261, 188418),
        (188419, 190578), (190579, 192738),
        (192739, 194898), (194899, 197058),
        (197059, 199216), (199217, 201368),
        (201369, 202738),
    ],
}

def merge_spans(spans):
    merged = []
    for low, high in sorted(spans):
        if merged and low <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], high))
        else:
            merged.append((low, high))
    return merged

PROP_SPANS = {label: merge_spans(spans) for label, spans in PROP_SPANS.items()}
ALL_SPANS = merge_spans([span for spans in PROP_SPANS.values() for span in spans])

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ROOM_GLB)
room = next(obj for obj in bpy.context.scene.objects if obj.type == "MESH")
source_vertex_count = len(room.data.vertices)
if source_vertex_count not in KNOWN_VERTEX_COUNTS:
    raise RuntimeError(
        f"Unexpected website room mesh size: {source_vertex_count} vertices; "
        "the known cleanup data no longer applies."
    )

bm = bmesh.new()
bm.from_mesh(room.data)
bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()

def prop_span_for_face(face):
    indices = [vertex.index for vertex in face.verts]
    for low, high in ALL_SPANS:
        if all(low <= index <= high for index in indices):
            return low, high
    return None

removed_by_span = {}
if source_vertex_count == SOURCE_VERTEX_COUNT:
    doomed_faces = []
    for face in bm.faces:
        span = prop_span_for_face(face)
        if span is not None:
            doomed_faces.append(face)
            removed_by_span[span] = removed_by_span.get(span, 0) + 1

    if not doomed_faces:
        bm.free()
        raise RuntimeError("No target geometry matched the known GLB vertex spans")

    target_vertex_ids = {
        index
        for low, high in ALL_SPANS
        for index in range(low, high + 1)
    }
    bmesh.ops.delete(bm, geom=doomed_faces, context="FACES")
    orphaned_target_vertices = [
        vertex for vertex in bm.verts
        if vertex.index in target_vertex_ids and not vertex.link_faces
    ]
    if orphaned_target_vertices:
        bmesh.ops.delete(bm, geom=orphaned_target_vertices, context="VERTS")

# Collect connected face components by quantized vertex positions. Draco can
# duplicate vertices between triangles, so index-only connectivity misses
# these islands. Components are measured before deleting to keep adjacent wall
# faces intact.
face_count = len(bm.faces)
parent = list(range(face_count))
rank = [0] * face_count

def find_root(item):
    while parent[item] != item:
        parent[item] = parent[parent[item]]
        item = parent[item]
    return item

def union(a, b):
    root_a, root_b = find_root(a), find_root(b)
    if root_a == root_b:
        return
    if rank[root_a] < rank[root_b]:
        root_a, root_b = root_b, root_a
    parent[root_b] = root_a
    if rank[root_a] == rank[root_b]:
        rank[root_a] += 1

first_face_for_position = {}
for face_id, face in enumerate(bm.faces):
    for vertex in face.verts:
        key = tuple(round(float(axis) * 100000) for axis in vertex.co)
        previous = first_face_for_position.get(key)
        if previous is None:
            first_face_for_position[key] = face_id
        else:
            union(face_id, previous)

component_faces = {}
for face_id, face in enumerate(bm.faces):
    root = find_root(face_id)
    stats = component_faces.setdefault(root, [[], [float("inf")] * 3, [float("-inf")] * 3])
    stats[0].append(face)
    for vertex in face.verts:
        for axis, value in enumerate(vertex.co):
            stats[1][axis] = min(stats[1][axis], float(value))
            stats[2][axis] = max(stats[2][axis], float(value))

target_faces = []
removed_components = {}
for component_id, (faces, low, high) in component_faces.items():
    if len(faces) < 15:
        continue
    for label, (cluster_min, cluster_max) in TARGET_COMPONENT_CLUSTERS.items():
        enclosed = all(low[i] >= cluster_min[i] and high[i] <= cluster_max[i] for i in range(3))
        if enclosed:
            target_faces.extend(faces)
            removed_components.setdefault(label, []).append(
                (len(faces), tuple(round(v, 3) for v in low), tuple(round(v, 3) for v in high))
            )
            break

if target_faces:
    bmesh.ops.delete(bm, geom=target_faces, context="FACES")
for label, components in removed_components.items():
    print("REMOVED", label, "components", components)

# Some microphone triangles are welded into a larger room island, so loose
# component deletion cannot catch them. Remove only face centers inside the
# audited mic bounds; the laptop key grid starts outside this volume.
mic_low, mic_high = MICROPHONE_WORLD_BOUNDS
mic_faces = []
for face in bm.faces:
    center = room.matrix_world @ face.calc_center_median()
    if all(mic_low[i] <= float(center[i]) <= mic_high[i] for i in range(3)):
        mic_faces.append(face)
if mic_faces:
    bmesh.ops.delete(bm, geom=mic_faces, context="FACES")
print("REMOVED microphone residual faces", len(mic_faces))

loose = [vertex for vertex in bm.verts if not vertex.link_faces]
if loose:
    bmesh.ops.delete(bm, geom=loose, context="VERTS")

# Copy the original laptop frame and deck faces, retaining their UVs. The source
# model and simplified website asset share the same root transform and atlas.
existing_objects = set(bpy.context.scene.objects)
bpy.ops.import_scene.gltf(filepath=SOURCE_ROOM_GLB)
source_room = next(obj for obj in bpy.context.scene.objects if obj not in existing_objects and obj.type == "MESH")
source_bm = bmesh.new()
source_bm.from_mesh(source_room.data)
source_bm.faces.ensure_lookup_table()
source_uv_layer = source_bm.loops.layers.uv.get("UVMap")
if source_uv_layer is None:
    source_bm.free()
    bm.free()
    raise RuntimeError("Source room is missing the UVMap required by the baked texture")
target_uv_layer = bm.loops.layers.uv.get("UVMap")
if target_uv_layer is None:
    target_uv_layer = bm.loops.layers.uv.new("UVMap")
source_to_target = {}
room_world_to_local = room.matrix_world.inverted_safe()
added_parts = {}
for label, (first_polygon, last_polygon) in LAPTOP_PART_POLYGON_RANGES.items():
    added_faces = 0
    for polygon_index in range(first_polygon, last_polygon + 1):
        source_face = source_bm.faces[polygon_index]
        target_verts = []
        for source_vertex in source_face.verts:
            target_vertex = source_to_target.get(source_vertex.index)
            if target_vertex is None:
                world_position = source_room.matrix_world @ source_vertex.co
                local_position = room_world_to_local @ world_position
                target_vertex = bm.verts.new(local_position)
                source_to_target[source_vertex.index] = target_vertex
            target_verts.append(target_vertex)
        target_face = bm.faces.new(target_verts)
        target_face.material_index = 0
        target_face.smooth = source_face.smooth
        for target_loop, source_loop in zip(target_face.loops, source_face.loops):
            target_loop[target_uv_layer].uv = source_loop[source_uv_layer].uv
        added_faces += 1
    added_parts[label] = added_faces
source_bm.free()
bpy.data.objects.remove(source_room, do_unlink=True)
print("RESTORED laptop parts from source", added_parts)

bm.normal_update()
bm.to_mesh(room.data)
bm.free()
room.data.update()

for label, spans in PROP_SPANS.items():
    print(
        "REMOVED", label,
        "faces", sum(removed_by_span.get(span, 0) for span in spans),
        "spans", len(spans),
    )
print("CLEAN_ROOM", room.name, "vertices", len(room.data.vertices), "faces", len(room.data.polygons))

# Preserve the website's compact Draco mesh and its separate bakedDay texture.
export_properties = bpy.ops.export_scene.gltf.get_rna_type().properties
export_options = {"filepath": ROOM_GLB, "export_format": "GLB", "export_apply": True}
if "export_draco_mesh_compression_enable" in export_properties:
    export_options["export_draco_mesh_compression_enable"] = True
if "export_draco_mesh_compression_level" in export_properties:
    export_options["export_draco_mesh_compression_level"] = 6
bpy.ops.export_scene.gltf(**export_options)
print("EXPORTED_ROOM", ROOM_GLB)

# Save a separate, editable Blender source with the baked material for future edits.
image = bpy.data.images.load(
    "/home/psykr/Projects/Om-Portfolio/public/assets/bakedDay.jpg",
    check_existing=True,
)
image.pack()
material = bpy.data.materials.new("Room Baked Day")
material.use_nodes = True
nodes = material.node_tree.nodes
principled = next(node for node in nodes if node.type == "BSDF_PRINCIPLED")
texture = nodes.new("ShaderNodeTexImage")
texture.image = image
material.node_tree.links.new(texture.outputs["Color"], principled.inputs["Base Color"])
principled.inputs["Roughness"].default_value = 0.82
room.data.materials.clear()
room.data.materials.append(material)

camera_data = bpy.data.cameras.new("Room Preview Camera")
camera = bpy.data.objects.new("Room Preview Camera", camera_data)
bpy.context.scene.collection.objects.link(camera)
camera.location = (-15.2, 10.8, 15.2)
direction = Vector((0.29, 0.42, 2.96)) - camera.location
camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
camera.data.lens = 52
bpy.context.scene.camera = camera
bpy.context.scene.render.resolution_x = 1200
bpy.context.scene.render.resolution_y = 900
bpy.context.view_layer.objects.active = room
room.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=ROOM_BLEND)
print("BLEND_SOURCE", ROOM_BLEND)
