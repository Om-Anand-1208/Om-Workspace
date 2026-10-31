"""Build the original Om Portfolio cyberpunk studio and export its web model.

Run this file inside Blender's Python environment. It creates a separate scene,
leaving any pre-existing Blender scene data untouched, exports a GLB for Three.js,
and writes a standalone .blend source scene for later edits.
"""

import bpy
import math
import os
from mathutils import Euler, Matrix, Vector


ROOT = "/home/psykr/Projects/Om-Portfolio"
MODEL_DIR = os.path.join(ROOT, "blender")
PUBLIC_ASSETS = os.path.join(ROOT, "public", "assets")
SOURCE_ASSETS = os.path.join(MODEL_DIR, "assets")
SCENE_NAME = "OmPortfolioStudio"
COLLECTION_NAME = "PortfolioStudioModel"
ROOM_SCALE = 0.56

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(PUBLIC_ASSETS, exist_ok=True)

# Replace only a prior scene and collection created by this script. Other open
# scenes and collections remain intact, and repeated runs retain clean object names.
old_scene = bpy.data.scenes.get(SCENE_NAME)
if old_scene and old_scene.get("om_portfolio_generated"):
    for obj in list(old_scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.scenes.remove(old_scene)
for old_collection in list(bpy.data.collections):
    if old_collection.name == COLLECTION_NAME or old_collection.name.startswith(COLLECTION_NAME + "."):
        for obj in list(old_collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(old_collection)

scene = bpy.data.scenes.new(SCENE_NAME)
scene["om_portfolio_generated"] = True
engine_ids = [item.identifier for item in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
preferred_engines = ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES", "BLENDER_WORKBENCH")
scene.render.engine = next((engine for engine in preferred_engines if engine in engine_ids), engine_ids[0])
scene.render.resolution_x = 1440
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.render.resolution_percentage = 80

model_collection = bpy.data.collections.new(COLLECTION_NAME)
model_collection["om_portfolio_generated"] = True
scene.collection.children.link(model_collection)
studio_objects = []
materials = {}

# Blender's glTF importer uses the active scene. Keep the existing authored
# scene data intact while making the generated scene the import destination.
if bpy.context.window:
    bpy.context.window.scene = scene


def material(name, color, roughness=0.65, metallic=0.0, glow=None, strength=0.0):
    if name in materials:
        return materials[name]
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    shader = next(node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED")
    shader.inputs["Base Color"].default_value = (*color, 1.0)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    if glow:
        emission = shader.inputs.get("Emission Color") or shader.inputs.get("Emission")
        if emission:
            emission.default_value = (*glow, 1.0)
        emission_strength = shader.inputs.get("Emission Strength")
        if emission_strength:
            emission_strength.default_value = strength
    materials[name] = mat
    return mat


def mesh_object(name, vertices, faces, mat, location=(0, 0, 0), smooth=False):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    model_collection.objects.link(obj)
    obj.location = location
    if smooth:
        for polygon in mesh.polygons:
            polygon.use_smooth = True
    studio_objects.append(obj)
    return obj


def import_model_asset(
    filename,
    label,
    location,
    scale=(1, 1, 1),
    rotation=(0, 0, 0),
    anchor_mode="ground",
    source="Innerscene Free Parts Library",
    license_name="CC0",
):
    """Import a GLB at a stable target point, preserve materials, and join meshes."""
    filepath = os.path.join(SOURCE_ASSETS, filename)
    if not os.path.isfile(filepath):
        raise FileNotFoundError("Missing source model: " + filepath)

    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=filepath)
    imported = [obj for obj in bpy.data.objects if obj not in before]
    imported_set = set(imported)
    top_level = [obj for obj in imported if obj.parent not in imported_set]
    if not imported:
        raise RuntimeError("The GLB contained no objects: " + filename)

    # Organize imported objects under this model's collection. Several glTF
    # files have one empty root; plant parts are separate top-level meshes.
    for obj in imported:
        for collection in list(obj.users_collection):
            if collection != model_collection:
                collection.objects.unlink(obj)
        if model_collection not in obj.users_collection:
            model_collection.objects.link(obj)

    mesh_objects = [obj for obj in imported if obj.type == "MESH"]
    if not mesh_objects:
        raise RuntimeError("The GLB contained no mesh objects: " + filename)

    # Source GLBs can put the model far from their origin. Measure actual
    # vertices first, then map that bounds anchor to the requested placement.
    source_points = [
        obj.matrix_world @ vertex.co
        for obj in mesh_objects
        for vertex in obj.data.vertices
    ]
    source_min = Vector(tuple(min(point[axis] for point in source_points) for axis in range(3)))
    source_max = Vector(tuple(max(point[axis] for point in source_points) for axis in range(3)))
    if anchor_mode == "center":
        source_anchor = (source_min + source_max) * 0.5
    elif anchor_mode == "ground":
        source_anchor = Vector(((source_min.x + source_max.x) * 0.5,
                                (source_min.y + source_max.y) * 0.5,
                                source_min.z))
    else:
        raise ValueError("anchor_mode must be 'ground' or 'center'")

    root = bpy.data.objects.new(label + " import root", None)
    model_collection.objects.link(root)
    root.matrix_world = Matrix.Identity(4)
    # Keep all original imported transforms in source coordinates beneath this
    # wrapper. The wrapper alone handles anchor, scale, rotation, and placement.
    for obj in top_level:
        source_world = obj.matrix_world.copy()
        obj.parent = root
        obj.matrix_parent_inverse = Matrix.Identity(4)
        obj.matrix_world = source_world

    rotation_matrix = Matrix.Rotation(rotation[2], 4, "Z") @ Matrix.Rotation(rotation[1], 4, "Y") @ Matrix.Rotation(rotation[0], 4, "X")
    scale_matrix = Matrix.Diagonal((scale[0], scale[1], scale[2], 1.0))
    root.matrix_world = (
        Matrix.Translation(Vector(location))
        @ rotation_matrix
        @ scale_matrix
        @ Matrix.Translation(-source_anchor)
    )
    bpy.context.view_layer.update()

    # The plant source carries large close-up maps. 1K keeps the web model
    # crisp at room scale while cutting the download size substantially.
    images = set()
    alpha_images = set()
    for obj in imported:
        if obj.type != "MESH":
            continue
        for mat in obj.data.materials:
            if not mat or not mat.use_nodes:
                continue
            for node in mat.node_tree.nodes:
                if node.type == "TEX_IMAGE" and node.image:
                    images.add(node.image)
                    frontier = [
                        link.to_node
                        for link in mat.node_tree.links
                        if link.from_node == node and link.from_socket.name == "Alpha"
                    ]
                    visited = set()
                    while frontier:
                        target_node = frontier.pop()
                        if target_node in visited:
                            continue
                        visited.add(target_node)
                        if target_node.type == "BSDF_PRINCIPLED" and any(
                            link.to_node == target_node and link.to_socket.name == "Alpha"
                            for link in mat.node_tree.links
                        ):
                            alpha_images.add(node.image)
                            break
                        frontier.extend(
                            link.to_node
                            for link in mat.node_tree.links
                            if link.from_node == target_node
                        )
    for image in images:
        width, height = image.size
        longest = max(width, height)
        if longest > 1024:
            image.scale(max(1, round(width * 1024 / longest)), max(1, round(height * 1024 / longest)))
        # Most prop maps are opaque. JPEG is much smaller for those; keep the
        # plant's cutout leaf map lossless so its alpha survives the export.
        if image not in alpha_images:
            image.file_format = "JPEG"

    # Bake the imported asset's placement into its mesh data before joining.
    # This retains the source UVs and materials without exporting hundreds of
    # tiny objects (the keyboard GLB alone has more than 200 mesh parts).
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in mesh_objects:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        baked_mesh = mesh.copy()
        baked_mesh.transform(evaluated.matrix_world)
        evaluated.to_mesh_clear()
        obj.data = baked_mesh
        obj.parent = None
        obj.matrix_world = Matrix.Identity(4)

    for obj in imported:
        if obj.type != "MESH":
            bpy.data.objects.remove(obj, do_unlink=True)

    bpy.ops.object.select_all(action="DESELECT")
    for obj in mesh_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = mesh_objects[0]
    bpy.ops.object.join()
    asset = bpy.context.view_layer.objects.active
    asset.name = label
    bpy.data.objects.remove(root, do_unlink=True)
    # Keep the object origin at its placement point. This makes it possible to
    # duplicate a prop later (the two plant meshes share the same local origin).
    asset.data.transform(Matrix.Translation(-Vector(location)))
    asset.location = location
    asset["source_asset_file"] = filename
    asset["source_asset_source"] = source
    asset["source_asset_license"] = license_name
    studio_objects.append(asset)
    return asset


def box(name, location, size, mat, bevel=0.0):
    x, y, z = (value / 2 for value in size)
    vertices = [
        (-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
        (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z),
    ]
    faces = [
        (0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
        (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7),
    ]
    obj = mesh_object(name, vertices, faces, mat, location)
    if bevel:
        modifier = obj.modifiers.new("Soft crafted edges", "BEVEL")
        modifier.width = min(bevel, min(size) * 0.24)
        modifier.segments = 3
        modifier.limit_method = "ANGLE"
        modifier.angle_limit = math.radians(25)
    return obj


def quad(name, location, width, height, mat):
    # Faces toward the open front of the room (negative Blender Y).
    vertices = [
        (-width / 2, 0, -height / 2),
        (width / 2, 0, -height / 2),
        (width / 2, 0, height / 2),
        (-width / 2, 0, height / 2),
    ]
    obj = mesh_object(name, vertices, [(0, 1, 2, 3)], mat, location)
    uv = obj.data.uv_layers.new(name="UVMap")
    coords = ((0, 0), (1, 0), (1, 1), (0, 1))
    for loop in obj.data.loops:
        uv.data[loop.index].uv = coords[loop.vertex_index]
    return obj


def cylinder(name, location, radius, depth, mat, vertices=20, radius_top=None):
    top_radius = radius if radius_top is None else radius_top
    points = []
    for z, r in ((-depth / 2, radius), (depth / 2, top_radius)):
        for index in range(vertices):
            angle = 2 * math.pi * index / vertices
            points.append((math.cos(angle) * r, math.sin(angle) * r, z))
    faces = []
    for index in range(vertices):
        nxt = (index + 1) % vertices
        faces.append((index, nxt, vertices + nxt, vertices + index))
    faces.append(tuple(reversed(range(vertices))))
    faces.append(tuple(range(vertices, vertices * 2)))
    return mesh_object(name, points, faces, mat, location, smooth=True)


def ellipsoid(name, location, scale, mat, rings=10, segments=16):
    vertices = []
    for ring in range(rings + 1):
        phi = math.pi * ring / rings
        for segment in range(segments):
            theta = 2 * math.pi * segment / segments
            vertices.append((
                math.sin(phi) * math.cos(theta) * scale[0],
                math.sin(phi) * math.sin(theta) * scale[1],
                math.cos(phi) * scale[2],
            ))
    faces = []
    for ring in range(rings):
        for segment in range(segments):
            a = ring * segments + segment
            b = ring * segments + (segment + 1) % segments
            c = (ring + 1) * segments + (segment + 1) % segments
            d = (ring + 1) * segments + segment
            faces.append((a, b, c, d))
    return mesh_object(name, vertices, faces, mat, location, smooth=True)


def torus(name, location, major, minor, mat, segments=20, sides=8):
    vertices = []
    for i in range(segments):
        u = 2 * math.pi * i / segments
        for j in range(sides):
            v = 2 * math.pi * j / sides
            r = major + minor * math.cos(v)
            vertices.append((r * math.cos(u), minor * math.sin(v), r * math.sin(u)))
    faces = []
    for i in range(segments):
        for j in range(sides):
            a = i * sides + j
            b = i * sides + (j + 1) % sides
            c = ((i + 1) % segments) * sides + (j + 1) % sides
            d = ((i + 1) % segments) * sides + j
            faces.append((a, b, c, d))
    return mesh_object(name, vertices, faces, mat, location, smooth=True)


def plant(prefix, x, y, base_z, scale=1.0):
    box(prefix + " pot", (x, y, base_z + 0.22 * scale), (0.48 * scale, 0.48 * scale, 0.44 * scale), pot, 0.08 * scale)
    cylinder(prefix + " soil", (x, y, base_z + 0.45 * scale), 0.19 * scale, 0.035 * scale, soil)
    leaves = (leaf_a, leaf_b, leaf_c)
    for index in range(8):
        angle = index * 2.399
        reach = (0.25 + (index % 3) * 0.05) * scale
        height = (0.82 + (index % 4) * 0.1) * scale
        leaf = ellipsoid(
            prefix + " leaf " + str(index + 1),
            (x + math.cos(angle) * reach, y + math.sin(angle) * reach, base_z + height),
            (0.10 * scale, 0.055 * scale, 0.31 * scale),
            leaves[index % len(leaves)],
        )
        leaf.rotation_euler[1] = math.cos(angle) * 0.55
        leaf.rotation_euler[0] = -math.sin(angle) * 0.55


# Materials: dark graphite, warm walnut, soft plaster and controlled neon.
plaster = material("Warm slate plaster", (0.115, 0.13, 0.17), 0.92)
plaster_left = material("Blue charcoal plaster", (0.085, 0.11, 0.16), 0.9)
oak = material("Honey walnut", (0.32, 0.16, 0.075), 0.54)
oak_light = material("Desk oak", (0.48, 0.27, 0.12), 0.46)
oak_edge = material("Dark wood edge", (0.19, 0.095, 0.048), 0.62)
floor_mat = material("Warm oak floor", (0.30, 0.17, 0.09), 0.7)
floor_alt = material("Oak board variation", (0.36, 0.21, 0.11), 0.7)
black_metal = material("Graphite metal", (0.025, 0.032, 0.045), 0.28, 0.72)
charcoal = material("Soft charcoal", (0.045, 0.052, 0.065), 0.5, 0.1)
linen = material("Muted rug linen", (0.30, 0.26, 0.23), 0.96)
linen_light = material("Rug weave", (0.42, 0.35, 0.30), 0.97)
cream = material("Ceramic cream", (0.75, 0.69, 0.57), 0.25)
amber_glow = material("Amber lamp glow", (0.9, 0.35, 0.08), 0.25, glow=(1.0, 0.24, 0.035), strength=3.2)
cyan_glow = material("Electric cyan", (0.015, 0.47, 0.75), 0.24, 0.15, (0.015, 0.48, 1.0), 2.3)
pink_glow = material("Neon magenta", (0.65, 0.03, 0.31), 0.25, 0.05, (0.95, 0.015, 0.4), 2.0)
violet_glow = material("Violet accent", (0.24, 0.08, 0.5), 0.28, 0.08, (0.27, 0.04, 0.85), 1.5)
screen_dark = material("Display glass", (0.008, 0.018, 0.035), 0.18, 0.2, (0.015, 0.05, 0.11), 0.3)
screen_code = material("Code display base", (0.015, 0.035, 0.06), 0.22, 0.05, (0.02, 0.07, 0.12), 0.65)
screen_portfolio = material("Portfolio display base", (0.035, 0.055, 0.08), 0.22, 0.04, (0.06, 0.12, 0.2), 0.65)
screen_analytics = material("Analytics display base", (0.015, 0.045, 0.065), 0.22, 0.04, (0.02, 0.13, 0.17), 0.65)
leaf_a = material("Olive leaves", (0.12, 0.30, 0.19), 0.86)
leaf_b = material("Deep green leaves", (0.08, 0.21, 0.16), 0.9)
leaf_c = material("Sage leaves", (0.27, 0.38, 0.23), 0.88)
pot = material("Terracotta pots", (0.34, 0.16, 0.12), 0.8)
soil = material("Plant soil", (0.10, 0.07, 0.045), 1.0)
chair_fabric = material("Chair upholstery", (0.12, 0.16, 0.19), 0.9)
chair_edge = material("Chair piping", (0.29, 0.24, 0.22), 0.84)
paper = material("Paper notes", (0.69, 0.59, 0.43), 0.94)


# Floating room platform and two open-front walls.
box("Floating graphite plinth", (0, 0, -0.23), (11.25, 9.45, 0.46), black_metal, 0.12)
box("Oak platform top", (0, 0, 0.015), (11.05, 9.25, 0.08), oak_light, 0.07)
box("Studio floor", (0, 0, 0.085), (10.78, 8.98, 0.08), floor_mat, 0.035)
for index in range(14):
    y = -4.36 + index * 0.65
    box("Floor board seam " + str(index + 1), (0, y, 0.128), (10.68, 0.014, 0.009), oak_edge, 0.003)
for index in range(12):
    x = -4.9 + index * 0.89
    box("Floor board joint " + str(index + 1), (x, -1.95 if index % 2 else -1.3, 0.13), (0.012, 0.54, 0.008), oak_edge, 0.002)

box("Back wall", (0, 4.55, 2.77), (10.85, 0.20, 5.38), plaster, 0.035)
box("Left wall", (-5.35, 0, 2.77), (0.20, 9.15, 5.38), plaster_left, 0.035)
box("Back wall lower walnut trim", (0, 4.40, 0.28), (10.7, 0.12, 0.20), oak, 0.035)
box("Left wall lower walnut trim", (-5.20, 0, 0.28), (0.12, 9.0, 0.20), oak, 0.03)
box("Back wall top cyan wash", (0, 4.42, 5.38), (10.7, 0.035, 0.045), cyan_glow, 0.015)
box("Left wall magenta wash", (-5.20, 0, 4.95), (0.035, 9.0, 0.04), pink_glow, 0.012)

# Rainy neon skyline window at the left end of the back wall.
box("Window outer frame", (-4.10, 4.39, 3.50), (1.72, 0.14, 2.55), oak_edge, 0.07)
box("Window inner frame", (-4.10, 4.30, 3.50), (1.52, 0.055, 2.35), black_metal, 0.045)
box("Window night glass", (-4.10, 4.265, 3.50), (1.37, 0.025, 2.20), screen_dark, 0.015)
box("Window vertical mullion", (-4.10, 4.23, 3.50), (0.045, 0.04, 2.20), oak_light, 0.01)
box("Window horizontal mullion", (-4.10, 4.23, 3.50), (1.37, 0.04, 0.045), oak_light, 0.01)
for index, (x, width, height, color) in enumerate([
    (-4.65, 0.22, 0.72, violet_glow), (-4.34, 0.18, 1.12, cyan_glow),
    (-3.93, 0.28, 0.88, pink_glow), (-3.60, 0.20, 1.36, cyan_glow),
]):
    box("Window skyline tower " + str(index + 1), (x, 4.21, 2.53 + height / 2), (width, 0.025, height), color, 0.008)
    for row in range(3):
        ellipsoid("Window skyline light " + str(index + 1) + " " + str(row + 1),
                  (x, 4.185, 2.62 + row * 0.16), (0.025, 0.012, 0.022), amber_glow, 6, 8)
box("Window sill", (-4.1, 4.15, 2.22), (1.95, 0.40, 0.12), oak_light, 0.045)

# Broad desk, drawers, legs and a controllable three-screen workbench.
desk_y = 2.36
box("Desk shadow apron", (0, desk_y, 1.02), (6.65, 1.72, 0.33), oak, 0.07)
box("Desk top", (0, desk_y, 1.24), (6.9, 1.86, 0.18), oak_light, 0.09)
box("Desk front cyan edge", (0, desk_y - 0.91, 1.21), (6.72, 0.035, 0.055), cyan_glow, 0.018)
for side in (-1, 1):
    x = side * 2.78
    box("Desk leg " + str(side), (x, desk_y, 0.60), (0.16, 1.58, 1.14), black_metal, 0.035)
    box("Drawer cabinet " + str(side), (side * 2.15, desk_y + 0.12, 0.69), (0.92, 1.35, 0.98), oak, 0.055)
    for row in range(3):
        z = 0.40 + row * 0.28
        box("Drawer face " + str(side) + " " + str(row), (side * 2.15, desk_y - 0.568, z), (0.79, 0.035, 0.20), oak_light, 0.025)
        box("Drawer pull " + str(side) + " " + str(row), (side * 2.15, desk_y - 0.60, z), (0.18, 0.025, 0.024), black_metal, 0.01)

monitor_specs = [
    # The code display is deliberately portrait to break up the two wide panels.
    ("Code", -2.22, 1.34, 2.58, 1.96, screen_code),
    ("Portfolio", 0.00, 2.36, 2.78, 1.42, screen_portfolio),
    ("Analytics", 2.02, 1.62, 2.58, 1.18, screen_analytics),
]
for kind, x, width, center_z, height, display_mat in monitor_specs:
    y = 2.80
    box(kind + " monitor rear shell", (x, y, center_z), (width + 0.15, 0.16, height + 0.15), black_metal, 0.075)
    box(kind + " monitor bezel", (x, y - 0.088, center_z), (width + 0.045, 0.035, height + 0.045), charcoal, 0.035)
    quad("Project" + kind, (x, y - 0.109, center_z), width, height, display_mat)
    box(kind + " monitor chin", (x, y - 0.12, center_z - height / 2 - 0.055), (width + 0.03, 0.045, 0.10), black_metal, 0.02)
    box(kind + " monitor stem", (x, y + 0.02, 1.69), (0.11, 0.13, 0.75), black_metal, 0.035)
    box(kind + " monitor foot", (x, y - 0.01, 1.34), (0.66 if kind != "Code" else 0.45, 0.47, 0.07), black_metal, 0.03)
    box(kind + " indicator", (x + width * 0.38, y - 0.145, center_z - height / 2 - 0.055), (0.035, 0.018, 0.018), cyan_glow, 0.007)

# Wall project cards and pinboard: individually named hit surfaces for later links.
box("Pinboard frame", (-0.20, 4.36, 3.66), (1.75, 0.16, 1.56), oak, 0.045)
box("Pinboard cork", (-0.20, 4.265, 3.66), (1.57, 0.035, 1.37), material("Cork", (0.31, 0.19, 0.11), 0.95), 0.025)
for index, (x, z, color) in enumerate([(-0.68, 3.92, paper), (-0.10, 3.78, cyan_glow), (0.32, 4.08, pink_glow), (-0.15, 3.38, paper)]):
    box("Pinboard note " + str(index + 1), (x, 4.235, z), (0.34, 0.018, 0.42), color, 0.008)
    cylinder("Note pin " + str(index + 1), (x, 4.205, z + 0.14), 0.035, 0.055, amber_glow, 10)

def project_frame(name, x, z, width, height, art_mat):
    y = 4.33
    box(name + " walnut frame", (x, y, z), (width + 0.18, 0.17, height + 0.18), oak_edge, 0.045)
    box(name + " inner mat", (x, y - 0.098, z), (width + 0.06, 0.025, height + 0.06), cream, 0.018)
    quad(name, (x, y - 0.116, z), width, height, art_mat)
    box(name + " picture light", (x, y - 0.03, z + height / 2 + 0.24), (width * 0.7, 0.10, 0.055), amber_glow, 0.018)

project_frame("ProjectArt", 3.38, 3.66, 1.14, 1.55, violet_glow)
project_frame("ProjectMoodboard", 4.68, 3.38, 0.88, 1.08, pink_glow)

# Floating shelves, books and warm/cyan practical lights.
box("Upper studio shelf", (1.85, 4.22, 4.62), (4.65, 0.52, 0.13), oak, 0.04)
box("Shelf neon underglow", (1.85, 3.94, 4.53), (4.20, 0.035, 0.035), pink_glow, 0.012)
book_colors = [paper, cyan_glow, oak_edge, violet_glow, leaf_a, pink_glow]
for index in range(9):
    x = 0.15 + index * 0.27
    height = 0.46 + (index % 4) * 0.09
    box("Shelf book " + str(index + 1), (x, 4.05, 4.69 + height / 2), (0.20, 0.32, height), book_colors[index % len(book_colors)], 0.018)
    box("Book spine band " + str(index + 1), (x, 3.878, 4.80), (0.13, 0.012, 0.018), amber_glow if index % 3 == 0 else oak_light, 0.005)
box("Desk wall cyan lightbar", (0.62, 4.28, 4.12), (3.25, 0.035, 0.055), cyan_glow, 0.018)
box("Desk lamp stem", (-3.06, 2.76, 1.70), (0.075, 0.09, 0.88), oak_edge, 0.025)
box("Desk lamp arm", (-2.77, 2.76, 2.05), (0.60, 0.10, 0.08), oak_edge, 0.025)
cylinder("Desk lamp shade", (-2.50, 2.76, 1.91), 0.28, 0.30, amber_glow, 24, radius_top=0.13)

# Keyboard, keycaps, mouse, notebook, cup and audio gear.
box("Mechanical keyboard base", (0.05, 1.78, 1.36), (1.62, 0.53, 0.08), black_metal, 0.04)
for row in range(4):
    for col in range(13):
        key_mat = cyan_glow if (row == 0 and col in (1, 5, 9, 12)) else (pink_glow if row == 3 and col == 6 else cream)
        box("Keyboard key " + str(row) + " " + str(col), (-0.68 + col * 0.12, 1.64 + row * 0.12, 1.415), (0.085, 0.075, 0.045), key_mat, 0.012)
box("Mouse pad", (1.63, 1.83, 1.30), (0.93, 0.78, 0.035), charcoal, 0.045)
ellipsoid("Wireless mouse", (1.63, 1.80, 1.39), (0.18, 0.25, 0.10), black_metal)
box("Portfolio sketchbook", (-2.0, 1.82, 1.34), (0.72, 0.55, 0.065), paper, 0.025)
for index in range(4):
    box("Sketchbook ink line " + str(index + 1), (-2.0, 1.62 + index * 0.10, 1.378), (0.46 - (index % 2) * 0.08, 0.012, 0.006), oak, 0.003)
cylinder("Coffee cup", (-1.85, 1.80, 1.48), 0.15, 0.25, cream, 24, radius_top=0.13)
cylinder("Coffee surface", (-1.85, 1.80, 1.61), 0.12, 0.012, oak_edge, 24)
torus("Coffee cup handle", (-1.67, 1.80, 1.49), 0.11, 0.025, cream)
box("Audio interface", (2.74, 1.88, 1.36), (0.55, 0.47, 0.12), black_metal, 0.035)
for index in range(3):
    ellipsoid("Audio level light " + str(index + 1), (2.55 + index * 0.17, 1.62, 1.43), (0.035, 0.012, 0.035), cyan_glow if index != 1 else pink_glow, 6, 8)

# Ergonomic chair and simple upholstered details.
box("Chair five-star base hub", (0.0, -0.05, 0.27), (0.25, 0.25, 0.18), black_metal, 0.04)
cylinder("Chair center post", (0.0, -0.05, 0.53), 0.075, 0.43, black_metal, 14)
box("Chair seat shell", (0.0, -0.12, 0.85), (1.08, 0.96, 0.22), black_metal, 0.12)
box("Chair seat cushion", (0.0, -0.12, 0.98), (0.94, 0.82, 0.16), chair_fabric, 0.12)
box("Chair back shell", (0.0, -0.53, 1.52), (0.94, 0.18, 1.16), black_metal, 0.16)
box("Chair back cushion", (0.0, -0.63, 1.54), (0.76, 0.08, 0.95), chair_fabric, 0.13)
for side in (-1, 1):
    box("Chair arm post " + str(side), (side * 0.57, -0.04, 1.12), (0.10, 0.12, 0.53), black_metal, 0.04)
    box("Chair arm pad " + str(side), (side * 0.57, 0.02, 1.40), (0.20, 0.45, 0.10), chair_edge, 0.045)
for index in range(5):
    angle = index * 2 * math.pi / 5
    x = math.cos(angle) * 0.48
    y = -0.05 + math.sin(angle) * 0.48
    wheel = box("Chair base spoke " + str(index + 1), (x / 2, y / 2 - 0.05, 0.24), (0.10, 0.52, 0.075), black_metal, 0.025)
    wheel.rotation_euler[2] = angle
    cylinder("Chair caster " + str(index + 1), (x, y, 0.15), 0.085, 0.15, black_metal, 12)

# Soft rug, side cushion and a couple of leafy accents.
box("Woven rug", (-0.25, -0.82, 0.19), (4.75, 3.30, 0.055), linen, 0.12)
for index in range(9):
    box("Rug woven stripe " + str(index + 1), (-2.25 + index * 0.50, -0.82, 0.222), (0.025, 2.80, 0.008), linen_light, 0.004)
box("Floor cushion", (4.12, -1.90, 0.42), (1.04, 0.90, 0.47), chair_fabric, 0.20)
plant("Desk-side plant", -4.28, -2.98, 0.15, 1.12)
plant("Shelf plant", 3.47, 4.02, 4.70, 0.58)
plant("Corner plant", 4.56, 2.35, 0.15, 0.82)

# A compact desktop tower on the floor, with a restrained luminous side panel.
box("Desktop tower case", (3.76, 2.35, 0.69), (0.64, 0.76, 1.22), black_metal, 0.075)
box("Desktop tower glass", (3.76, 1.955, 0.70), (0.50, 0.025, 0.92), screen_dark, 0.035)
box("Desktop tower cyan strip", (3.54, 1.93, 0.70), (0.025, 0.02, 0.82), cyan_glow, 0.01)
box("Desktop tower pink strip", (3.98, 1.93, 0.70), (0.025, 0.02, 0.42), pink_glow, 0.01)

# Replace the oversized procedural furniture with reusable models while
# keeping the room, desk layout, screen interfaces, and neon accents original.
replaced_prefixes = (
    "Desk shadow apron", "Desk top", "Desk front cyan edge", "Desk leg ",
    "Drawer cabinet ", "Drawer face ", "Drawer pull ",
    "Desk lamp stem", "Desk lamp arm", "Desk lamp shade",
    "Mechanical keyboard base", "Keyboard key ", "Chair ",
    "Desk-side plant", "Shelf plant", "Corner plant",
)
for obj in list(studio_objects):
    if any(obj.name.startswith(prefix) for prefix in replaced_prefixes):
        studio_objects.remove(obj)
        bpy.data.objects.remove(obj, do_unlink=True)

# Bring the room back to believable workstation proportions while leaving the
# imported real-scale models untouched by this global transform.
for obj in studio_objects:
    obj.location *= ROOM_SCALE
    obj.scale *= ROOM_SCALE

# Replace the three procedural screen faces with the repo's screen meshes.
# Their object names remain stable because the website uses them for texture
# painting and pointer interaction. The source room model itself is not used.
for obj in list(studio_objects):
    if obj.name in {"ProjectCode", "ProjectPortfolio", "ProjectAnalytics"}:
        studio_objects.remove(obj)
        bpy.data.objects.remove(obj, do_unlink=True)

repo_source = "Bruno Simon's my-room-in-3d repository"
repo_permission = "Used with explicit permission reported by the user"

# The controls sit on a small original graphite plate; the downloaded asset
# supplies the separate Loupedeck button geometry.
box("Loupedeck custom graphite base", (-0.72, 1.01, 0.81), (0.45, 0.24, 0.055), black_metal, 0.035)
box("Loupedeck cyan edge", (-0.72, 0.887, 0.81), (0.40, 0.012, 0.025), cyan_glow, 0.006)

desk_asset = import_model_asset(
    "corner-computer-desk.glb", "CC0 APEX computer desk",
    (0.0, 1.35, 0.07), scale=(2.35, 1.62, 0.90),
)
chair_asset = import_model_asset(
    "bruno-simon/topChairModel.glb", "Permissioned ergonomic studio chair",
    (0.0, 0.02, 0.07), scale=(0.40, 0.40, 0.40),
    rotation=(0.0, 0.0, math.pi), source=repo_source, license_name=repo_permission,
)
keyboard_asset = import_model_asset(
    "mechanical-keyboard.glb", "CC0 mechanical keyboard",
    (0.0, 1.02, 0.76), scale=(1.18, 1.18, 1.18),
)
lamp_asset = import_model_asset(
    "bruno-simon/elgatoLightModel.glb", "Permissioned Elgato key light",
    (-1.08, 1.28, 0.78), scale=(0.72, 0.72, 0.72),
    source=repo_source, license_name=repo_permission,
)
loupedeck_asset = import_model_asset(
    "bruno-simon/loupedeckButtonsModel.glb", "Permissioned Loupedeck buttons",
    (-0.72, 1.01, 0.84), scale=(1.08, 1.08, 1.08),
    source=repo_source, license_name=repo_permission,
)
if not loupedeck_asset.data.materials:
    loupedeck_asset.data.materials.append(cyan_glow)

# Source model bounds are normalized to screen centers, so each panel keeps its
# own world-space proportions and lines up with the frame built above.
screen_code_asset = import_model_asset(
    "bruno-simon/macScreenModel.glb", "ProjectCode",
    (-2.22 * ROOM_SCALE, (2.80 - 0.109) * ROOM_SCALE, 2.58 * ROOM_SCALE),
    scale=(0.61, 0.80, 1.46), anchor_mode="center",
    source=repo_source, license_name=repo_permission,
)
screen_portfolio_asset = import_model_asset(
    "bruno-simon/pcScreenModel.glb", "ProjectPortfolio",
    (0.0, (2.80 - 0.109) * ROOM_SCALE, 2.78 * ROOM_SCALE),
    scale=(0.55, 0.55, 0.55), anchor_mode="center",
    source=repo_source, license_name=repo_permission,
)
screen_analytics_asset = import_model_asset(
    "bruno-simon/macScreenModel.glb", "ProjectAnalytics",
    (2.02 * ROOM_SCALE, (2.80 - 0.109) * ROOM_SCALE, 2.58 * ROOM_SCALE),
    scale=(1.18, 1.0, 0.88), anchor_mode="center",
    source=repo_source, license_name=repo_permission,
)
plant_asset = import_model_asset(
    "potted-plant.glb", "CC0 studio plant",
    (-2.48, -1.28, 0.085), scale=(0.82, 0.82, 0.82),
)
plant_copy = plant_asset.copy()
plant_copy.data = plant_asset.data
plant_copy.name = "CC0 studio plant duplicate"
plant_copy.location = (2.47, 1.72, 0.085)
plant_copy.scale = (0.68, 0.68, 0.68)
model_collection.objects.link(plant_copy)
plant_copy["source_asset_file"] = "potted-plant.glb"
plant_copy["source_asset_source"] = "Innerscene Free Parts Library"
plant_copy["source_asset_license"] = "CC0"
studio_objects.append(plant_copy)

# Preview camera and soft practical lighting live in this Blender scene only.
world = bpy.data.worlds.new("Om Studio dark world")
world.use_nodes = True
world.node_tree.nodes.get("Background").inputs["Color"].default_value = (0.008, 0.01, 0.018, 1)
world.node_tree.nodes.get("Background").inputs["Strength"].default_value = 0.22
scene.world = world

def area_light(name, location, energy, color, size, target):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.color = color
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
    return obj

warm_light = area_light("Warm key light", (2.5, -6.5, 10), 1250, (1.0, 0.60, 0.34), 7.0, (0, 0, 1.5))
cool_light = area_light("Cool window fill", (-4.4, 2.7, 6.4), 950, (0.12, 0.38, 1.0), 4.5, (0, 0, 1.7))
rim_light = area_light("Magenta rim", (4.5, 3.3, 7.0), 720, (0.75, 0.10, 0.42), 4.0, (0, 1, 2.0))
for light, target in (
    (warm_light, (0, 0, 1.5)),
    (cool_light, (0, 0, 1.7)),
    (rim_light, (0, 1, 2.0)),
):
    light.location *= ROOM_SCALE
    light.data.size *= ROOM_SCALE
    light.rotation_euler = (Vector(target) * ROOM_SCALE - light.location).to_track_quat("-Z", "Y").to_euler()
camera_data = bpy.data.cameras.new("Studio preview camera")
camera = bpy.data.objects.new("Studio preview camera", camera_data)
scene.collection.objects.link(camera)
camera.location = Vector((13, -17, 14)) * ROOM_SCALE
camera.rotation_euler = (Vector((0, 0, 2.15 * ROOM_SCALE)) - camera.location).to_track_quat("-Z", "Y").to_euler()
camera_data.type = "ORTHO"
camera_data.ortho_scale = 17.4 * ROOM_SCALE
scene.camera = camera

# Show the new scene in Blender while preserving the original scene datablocks.
if bpy.context.window:
    bpy.context.window.scene = scene

# Merge non-interactive scenery by material to keep mobile draw calls low. Named
# screen/art planes stay separate so the website can texture and raycast them.
clickable_names = {"ProjectCode", "ProjectPortfolio", "ProjectAnalytics", "ProjectArt", "ProjectMoodboard"}
groups = {}
for obj in list(studio_objects):
    if obj.name in clickable_names or obj.type != "MESH" or obj.get("source_asset_file"):
        continue
    mat = obj.data.materials[0] if obj.data.materials else None
    if mat:
        groups.setdefault(mat, []).append(obj)

depsgraph = bpy.context.evaluated_depsgraph_get()
for mat, objects in groups.items():
    vertices = []
    faces = []
    for obj in objects:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        offset = len(vertices)
        matrix = evaluated.matrix_world
        vertices.extend(tuple(matrix @ vertex.co) for vertex in mesh.vertices)
        faces.extend(tuple(offset + index for index in polygon.vertices) for polygon in mesh.polygons)
        evaluated.to_mesh_clear()
    merged_mesh = bpy.data.meshes.new("Batched " + mat.name + " Mesh")
    merged_mesh.from_pydata(vertices, [], faces)
    merged_mesh.materials.append(mat)
    merged_mesh.update()
    merged = bpy.data.objects.new("Static " + mat.name, merged_mesh)
    model_collection.objects.link(merged)
    studio_objects.append(merged)
    for obj in objects:
        studio_objects.remove(obj)
        bpy.data.objects.remove(obj, do_unlink=True)

# Export only the geometry collection: lights and preview camera stay out of the web model.
bpy.ops.object.select_all(action="DESELECT")
for obj in studio_objects:
    obj.select_set(True)
if studio_objects:
    bpy.context.view_layer.objects.active = studio_objects[0]

glb_path = os.path.join(PUBLIC_ASSETS, "om-cyberpunk-studio.glb")
bpy.ops.export_scene.gltf(
    filepath=glb_path,
    export_format="GLB",
    use_selection=True,
    export_apply=True,
    export_materials="EXPORT",
    export_image_format="AUTO",
    export_image_quality=86,
    export_cameras=False,
    export_lights=False,
    export_yup=True,
)

blend_path = os.path.join(MODEL_DIR, "om-cyberpunk-studio.blend")
bpy.data.libraries.write(blend_path, {scene}, path_remap="RELATIVE", fake_user=True, compress=True)

print("Created Blender scene:", SCENE_NAME)
print("Optimized model meshes:", len(studio_objects))
print("GLB:", glb_path, os.path.getsize(glb_path), "bytes")
print("Editable scene:", blend_path, os.path.getsize(blend_path), "bytes")
print("Interactive nodes:", ["ProjectCode", "ProjectPortfolio", "ProjectAnalytics", "ProjectArt", "ProjectMoodboard"])
