"""SurferFlow pastel isometric diorama builder for Blender.

Uses only Blender's built-in bpy API. No add-ons or external assets required.
Run:
  blender --background --python surferflow_diorama.py -- --output-dir ./surferflow_output

The script saves a .blend and six consistent orthographic renders.
Designed as a clean, editable first pass, not a fluid simulation.
"""

import argparse
import math
import os
import sys
from mathutils import Vector
import bpy


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------
def get_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description="Build the SurferFlow diorama")
    parser.add_argument("--output-dir", default="./surferflow_output")
    parser.add_argument("--blend-name", default="SurferFlow_Diorama.blend")
    parser.add_argument("--resolution", type=int, default=1024)
    parser.add_argument("--no-render", action="store_true", help="Build and save only")
    return parser.parse_known_args(argv)[0]


ARGS = get_args()
OUT_DIR = os.path.abspath(os.path.expanduser(ARGS.output_dir))
os.makedirs(OUT_DIR, exist_ok=True)


# -----------------------------------------------------------------------------
# Scene, collections, and materials
# -----------------------------------------------------------------------------
def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)
    for coll in list(bpy.data.collections):
        if coll.name != "Collection" and coll.users == 0:
            bpy.data.collections.remove(coll)


def get_collection(name):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    return coll


def organize(obj, collection_name):
    target = get_collection(collection_name)
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    target.objects.link(obj)
    return obj


def make_mat(name, color, roughness=0.72, metallic=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
    return mat


PALETTE = {
    "peach": (0.91, 0.67, 0.62),
    "peach_light": (1.00, 0.79, 0.70),
    "sea_deep": (0.055, 0.30, 0.34),
    "sea": (0.10, 0.52, 0.51),
    "sea_light": (0.25, 0.72, 0.66),
    "sea_mint": (0.43, 0.82, 0.74),
    "foam": (1.00, 0.91, 0.79),
    "sand": (0.94, 0.76, 0.56),
    "rock": (0.43, 0.36, 0.33),
    "rock_light": (0.59, 0.49, 0.43),
    "leaf": (0.31, 0.53, 0.34),
    "leaf_light": (0.50, 0.68, 0.40),
    "skin": (0.75, 0.43, 0.29),
    "shirt": (1.00, 0.88, 0.73),
    "shorts": (0.15, 0.43, 0.39),
    "hair": (0.20, 0.105, 0.075),
    "board": (1.00, 0.91, 0.78),
    "coral": (0.94, 0.38, 0.30),
    "dark": (0.075, 0.13, 0.15),
}
MATS = {key: make_mat("SF_MAT_" + key, value) for key, value in PALETTE.items()}


def use_mat(obj, mat):
    if mat:
        obj.data.materials.clear()
        obj.data.materials.append(mat)
    return obj


# -----------------------------------------------------------------------------
# Geometry helpers. All names intentionally remain readable for Codex edits.
# -----------------------------------------------------------------------------
def add_cube(name, location, dimensions, mat, bevel=0.0, collection="01_Ocean_Base"):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel > 0:
        mod = obj.modifiers.new("Soft_Rounded_Edges", "BEVEL")
        mod.width = bevel
        mod.segments = 4
        obj.modifiers.new("Weighted_Corner_Normals", "WEIGHTED_NORMAL")
    use_mat(obj, mat)
    return organize(obj, collection)


def add_uv(name, location, scale, mat, collection="04_Surfer", segments=24, rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    use_mat(obj, mat)
    return organize(obj, collection)


def add_ico(name, location, scale, mat, collection="03_Coastal_Details", subdivisions=2, smooth=True):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if smooth:
        for poly in obj.data.polygons:
            poly.use_smooth = True
    use_mat(obj, mat)
    return organize(obj, collection)


def add_cylinder_between(name, start, end, radius, mat, collection="04_Surfer", vertices=16, radius_end=None):
    a, b = Vector(start), Vector(end)
    delta = b - a
    if delta.length < 0.0001:
        return None
    bpy.ops.mesh.primitive_cone_add(
        vertices=vertices,
        radius1=radius if radius_end is None else radius_end,
        radius2=radius,
        depth=delta.length,
        location=(a + b) / 2,
    )
    obj = bpy.context.object
    obj.name = name
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = delta.to_track_quat("Z", "Y")
    for poly in obj.data.polygons:
        poly.use_smooth = True
    use_mat(obj, mat)
    return organize(obj, collection)


def add_curve(name, points, mat, bevel_depth=0.025, collection="02_Wave_and_Foam", cyclic=False):
    data = bpy.data.curves.new(name + "_Curve", type="CURVE")
    data.dimensions = "3D"
    data.resolution_u = 12
    data.bevel_depth = bevel_depth
    data.bevel_resolution = 3
    spline = data.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for p, co in zip(spline.points, points):
        p.co = (co[0], co[1], co[2], 1.0)
    spline.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, data)
    get_collection(collection).objects.link(obj)
    use_mat(obj, mat)
    return obj


def add_plane_mesh(name, xmin, xmax, ymin, ymax, z, mat, collection="01_Ocean_Base"):
    verts = [(xmin, ymin, z), (xmax, ymin, z), (xmax, ymax, z), (xmin, ymax, z)]
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(verts, [], [(0, 1, 2, 3)])
    mesh.materials.append(mat)
    obj = bpy.data.objects.new(name, mesh)
    get_collection(collection).objects.link(obj)
    return obj


# -----------------------------------------------------------------------------
# Model parts
# -----------------------------------------------------------------------------
def build_ocean_base():
    # Rounded tile and simple flat upper ocean surface: intentionally no fluid sim.
    add_cube("Ocean_Tile_Beveled_Base", (0, 0, 0.42), (10.0, 8.4, 0.84), MATS["sea_deep"], 0.22)
    add_plane_mesh("Ocean_Surface", -4.84, 4.84, -4.04, 4.04, 0.845, MATS["sea"])
    # A thin darker trim beneath the main tile gives the diorama a finished edge.
    add_cube("Ocean_Tile_Lower_Trim", (0, 0, 0.055), (10.08, 8.48, 0.15), MATS["sea_deep"], 0.06)


def build_wave():
    # A single extruded sculptural ribbon. Edit WAVE_PROFILE to change the silhouette.
    water_z = 0.86
    profile = [
        (-4.30, 0.89), (-3.70, 0.98), (-3.12, 1.18), (-2.65, 1.52),
        (-2.22, 2.02), (-1.80, 2.65), (-1.37, 3.24), (-0.88, 3.70),
        (-0.30, 3.98), (0.28, 4.02), (0.70, 3.82), (0.81, 3.52),
        (0.62, 3.25), (0.30, 3.04), (0.08, 2.87),
    ]
    width_steps = 22
    y_min, y_max = -1.10, 3.10
    verts, faces = [], []
    for j in range(width_steps + 1):
        t = j / width_steps
        y = y_min + (y_max - y_min) * t
        width_fade = 1.0 - 0.10 * ((t - 0.5) * 2.0) ** 2
        for x, z in profile:
            # Slight x drift and crest taper give the slab a soft, flowing shape.
            edge = abs((t - 0.5) * 2.0)
            verts.append((x + 0.13 * edge * edge, y, water_z + (z - water_z) * width_fade))
    n = len(profile)
    for j in range(width_steps):
        for i in range(n - 1):
            a = j * n + i
            faces.append((a, a + 1, a + n + 1, a + n))
    mesh = bpy.data.meshes.new("Wave_Ribbon_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    wave = bpy.data.objects.new("Wave_Main_Curled_Ribbon", mesh)
    get_collection("02_Wave_and_Foam").objects.link(wave)
    use_mat(wave, MATS["sea_light"])
    for poly in mesh.polygons:
        poly.use_smooth = True
    solid = wave.modifiers.new("Wave_Thickness", "SOLIDIFY")
    solid.thickness = 0.14
    solid.offset = 0.0
    bevel = wave.modifiers.new("Soft_Wave_Edges", "BEVEL")
    bevel.width = 0.045
    bevel.segments = 3

    # Narrow inner highlight adds a layered clay look without complex water shaders.
    highlight_points = [
        (-3.65, -0.70, 1.02), (-2.85, -0.70, 1.44),
        (-2.20, -0.70, 2.04), (-1.60, -0.70, 2.88),
        (-0.92, -0.70, 3.56), (-0.25, -0.70, 3.82),
    ]
    add_curve("Wave_Flow_Highlight", highlight_points, MATS["sea_mint"], 0.035)

    # Foam pearls along the crest. Low object count, easy to move or remove.
    for i in range(19):
        t = i / 18.0
        y = -1.02 + t * 4.00
        x = 0.16 + 0.18 * math.sin(t * math.pi)
        z = 3.87 - 0.22 * abs(t - 0.5) * 2.0
        size = 0.12 + 0.045 * (0.5 + 0.5 * math.sin(i * 2.31))
        add_uv("Foam_Crest_%02d" % i, (x, y, z), (size * 1.18, size, size * 0.92), MATS["foam"], "02_Wave_and_Foam", 16, 10)

    # Large, rounded foam clusters at the wave foot.
    for row in range(2):
        for i in range(9):
            x = -1.6 + i * 0.34
            y = -0.72 + row * 0.48 + 0.08 * math.sin(i * 1.4)
            z = 0.98 + 0.06 * math.sin(i * 1.8 + row)
            r = 0.11 + 0.04 * (0.5 + 0.5 * math.cos(i * 2.2 + row))
            add_uv("Foam_Foot_%d_%02d" % (row, i), (x, y, z), (r * 1.4, r, r * 0.62), MATS["foam"], "02_Wave_and_Foam", 16, 10)

    # Foreground ripple ribbons, intentionally sparse.
    for idx, y in enumerate((-3.38, -2.92, -3.72, -2.52)):
        pts = []
        for k in range(13):
            x = -3.8 + k * 0.48
            zz = 0.88 + 0.02 * math.sin(k * 0.85 + idx)
            yy = y + 0.10 * math.sin(k * 0.62 + idx * 0.7)
            pts.append((x, yy, zz))
        add_curve("Ocean_Ripple_%02d" % idx, pts, MATS["sea_mint"] if idx % 2 == 0 else MATS["foam"], 0.018, "02_Wave_and_Foam")


def build_coastal_details():
    # Tiny sandy rock outcrop at the far corner; ocean remains the dominant shape.
    add_uv("Small_Sand_Patch", (-3.75, 3.25, 0.96), (0.95, 0.72, 0.20), MATS["sand"], "03_Coastal_Details", 24, 12)
    rocks = [
        ((-4.22, 3.17, 1.20), (0.38, 0.35, 0.39), "rock"),
        ((-3.70, 3.48, 1.30), (0.44, 0.38, 0.49), "rock_light"),
        ((-3.23, 3.16, 1.16), (0.33, 0.30, 0.30), "rock"),
    ]
    for idx, (loc, scale, matkey) in enumerate(rocks):
        add_ico("Rounded_Coastal_Rock_%02d" % idx, loc, scale, MATS[matkey], subdivisions=2, smooth=True)

    # A few broad succulent-like leaves, instead of a complicated palm tree.
    leaf_center = (-3.78, 3.18, 1.34)
    for i, angle in enumerate((0, 55, 110, 165, 220, 275)):
        a = math.radians(angle)
        loc = (leaf_center[0] + 0.23 * math.cos(a), leaf_center[1] + 0.20 * math.sin(a), leaf_center[2] + (0.12 if i % 2 else 0.02))
        leaf = add_uv("Succulent_Leaf_%02d" % i, loc, (0.14, 0.09, 0.22), MATS["leaf_light"] if i % 2 == 0 else MATS["leaf"], "03_Coastal_Details", 16, 10)
        leaf.rotation_euler[1] = math.radians(28 * math.cos(a))
        leaf.rotation_euler[0] = math.radians(24 * math.sin(a))

    # Two tiny foam beads around the rocks tie the coast back into the sea.
    for i, loc in enumerate(((-4.45, 2.72, 0.99), (-3.05, 2.84, 0.99), (-4.2, 3.75, 0.99))):
        add_uv("Coastal_Foam_%02d" % i, loc, (0.16, 0.10, 0.07), MATS["foam"], "03_Coastal_Details", 16, 10)


def build_surfboard():
    # Rounded bevel-cube works as a stylized board and is trivial to edit.
    board = add_cube("Surfboard_Main", (-1.62, -2.02, 1.055), (2.25, 0.56, 0.13), MATS["board"], 0.22, "04_Surfer")
    board.rotation_euler[2] = math.radians(-8)
    stripe = add_cube("Surfboard_Coral_Stripe", (-1.62, -2.02, 1.126), (1.55, 0.075, 0.012), MATS["coral"], 0.035, "04_Surfer")
    stripe.rotation_euler[2] = math.radians(-8)
    # A small rear fin signals surfboard construction without over-detail.
    fin = add_cube("Surfboard_Fin", (-2.45, -2.02, 1.01), (0.20, 0.12, 0.12), MATS["sea_deep"], 0.04, "04_Surfer")
    fin.rotation_euler[1] = math.radians(14)
    return board


def build_surfer():
    # Simplified toy-like human, deliberately constructed from editable primitives.
    skin, shirt, shorts, hair, dark = MATS["skin"], MATS["shirt"], MATS["shorts"], MATS["hair"], MATS["dark"]
    y = -2.02
    # Feet and legs, in a wide low surfing stance.
    left_foot = (-2.03, y - 0.03, 1.16)
    right_foot = (-1.24, y + 0.04, 1.16)
    add_uv("Surfer_Foot_Back", left_foot, (0.22, 0.12, 0.075), skin, "04_Surfer")
    add_uv("Surfer_Foot_Front", right_foot, (0.22, 0.12, 0.075), skin, "04_Surfer")

    hip_l = (-1.93, y, 1.75)
    knee_l = (-2.02, y - 0.01, 1.43)
    ankle_l = (-2.03, y - 0.02, 1.22)
    hip_r = (-1.48, y, 1.77)
    knee_r = (-1.32, y + 0.04, 1.45)
    ankle_r = (-1.24, y + 0.04, 1.22)
    add_uv("Surfer_Shorts_Hips", (-1.72, y, 1.79), (0.32, 0.20, 0.22), shorts, "04_Surfer")
    add_cylinder_between("Surfer_Leg_Back_Thigh", hip_l, knee_l, 0.105, skin)
    add_cylinder_between("Surfer_Leg_Back_Shin", knee_l, ankle_l, 0.085, skin)
    add_cylinder_between("Surfer_Leg_Front_Thigh", hip_r, knee_r, 0.105, skin)
    add_cylinder_between("Surfer_Leg_Front_Shin", knee_r, ankle_r, 0.085, skin)
    for idx, loc in enumerate((knee_l, knee_r)):
        add_uv("Surfer_Knee_%d" % idx, loc, (0.105, 0.10, 0.105), skin, "04_Surfer", 16, 10)

    # Shirt torso and neck.
    torso = add_uv("Surfer_Cream_Top", (-1.72, y, 2.11), (0.31, 0.22, 0.42), shirt, "04_Surfer")
    torso.rotation_euler[1] = math.radians(-8)
    add_uv("Surfer_Neck", (-1.69, y, 2.47), (0.105, 0.11, 0.12), skin, "04_Surfer", 16, 10)

    # Arms stretch outward for balance.
    shoulder_l = (-1.94, y, 2.30)
    elbow_l = (-2.24, y - 0.03, 2.47)
    hand_l = (-2.48, y - 0.08, 2.56)
    shoulder_r = (-1.50, y, 2.31)
    elbow_r = (-1.19, y - 0.04, 2.43)
    hand_r = (-0.91, y - 0.08, 2.48)
    for label, a, b, c in (("Back", shoulder_l, elbow_l, hand_l), ("Front", shoulder_r, elbow_r, hand_r)):
        add_cylinder_between("Surfer_Arm_%s_Upper" % label, a, b, 0.075, skin)
        add_cylinder_between("Surfer_Arm_%s_Forearm" % label, b, c, 0.063, skin)
        add_uv("Surfer_Hand_%s" % label, c, (0.09, 0.075, 0.075), skin, "04_Surfer", 16, 10)
        add_uv("Surfer_Elbow_%s" % label, b, (0.075, 0.075, 0.075), skin, "04_Surfer", 16, 10)

    # Head, swept hair cap and simple hair locks. No facial texture needed.
    add_uv("Surfer_Head", (-1.67, y - 0.01, 2.69), (0.23, 0.22, 0.27), skin, "04_Surfer")
    add_uv("Surfer_Hair_Cap", (-1.69, y + 0.005, 2.86), (0.245, 0.225, 0.16), hair, "04_Surfer")
    for i, loc in enumerate(((-1.82, y - 0.05, 2.91), (-1.70, y - 0.09, 2.96), (-1.57, y - 0.03, 2.91))):
        add_uv("Surfer_Hair_Lock_%d" % i, loc, (0.105, 0.10, 0.10), hair, "04_Surfer", 16, 10)

    # Minimal dark sunglasses on the forward-facing (-Y) side of the face.
    add_cube("Surfer_Sunglasses_Left", (-1.77, y - 0.209, 2.70), (0.105, 0.035, 0.055), dark, 0.018, "04_Surfer")
    add_cube("Surfer_Sunglasses_Right", (-1.63, y - 0.209, 2.70), (0.105, 0.035, 0.055), dark, 0.018, "04_Surfer")
    add_cube("Surfer_Sunglasses_Bridge", (-1.70, y - 0.23, 2.70), (0.045, 0.025, 0.025), dark, 0.008, "04_Surfer")


def build_studio():
    # Matte peach floor/background for the small clay-diorama aesthetic.
    add_plane_mesh("Peach_Studio_Ground", -100, 100, -100, 100, -0.09, MATS["peach"], "05_Studio")

    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (*PALETTE["peach"], 1.0)
        bg.inputs["Strength"].default_value = 0.65

    # Broad area lights: soft pastel shadows with a slight warm/cool split.
    def area_light(name, location, energy, color, size):
        data = bpy.data.lights.new(name, type="AREA")
        data.energy = energy
        data.color = color
        data.shape = "DISK"
        data.size = size
        ob = bpy.data.objects.new(name, data)
        get_collection("06_Lighting_and_Cameras").objects.link(ob)
        ob.location = location
        target = Vector((0.0, 0.0, 1.5)) - ob.location
        ob.rotation_euler = target.to_track_quat("-Z", "Y").to_euler()
        return ob

    area_light("Key_Light_Warm", (-5.0, -6.0, 10.0), 1050, (1.0, 0.78, 0.64), 7.0)
    area_light("Fill_Light_Soft_Cyan", (5.0, 1.5, 8.0), 700, (0.67, 0.88, 1.0), 6.0)
    area_light("Rim_Light_Cream", (0.0, 6.0, 7.0), 500, (1.0, 0.89, 0.73), 5.0)


def build_cameras():
    target = Vector((0.0, 0.0, 2.0))
    specs = {
        "CAM_ThreeQuarter": Vector((12.0, -15.0, 11.0)),
        "CAM_Front": Vector((0.0, -22.0, 2.0)),
        "CAM_Back": Vector((0.0, 22.0, 2.0)),
        "CAM_Left": Vector((-22.0, 0.0, 2.0)),
        "CAM_Right": Vector((22.0, 0.0, 2.0)),
        "CAM_Top": Vector((0.0, 0.0, 22.0)),
    }
    cameras = {}
    for name, offset in specs.items():
        data = bpy.data.cameras.new(name + "_Data")
        data.type = "ORTHO"
        data.ortho_scale = 12.5
        obj = bpy.data.objects.new(name, data)
        get_collection("06_Lighting_and_Cameras").objects.link(obj)
        obj.location = target + offset
        if name == "CAM_Top":
            obj.rotation_euler = (0.0, 0.0, 0.0)  # Camera local -Z points straight down.
        else:
            obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()
        cameras[name] = obj
    return cameras


def configure_render():
    scene = bpy.context.scene
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except Exception:
        scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = ARGS.resolution
    scene.render.resolution_y = ARGS.resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.filepath = os.path.join(OUT_DIR, "view_three_quarter")
    scene.render.image_settings.compression = 15
    scene.render.use_file_extension = True
    scene.render.resolution_percentage = 100
    scene.render.image_settings.color_depth = "8"
    scene.render.dither_intensity = 1.0
    scene.render.use_overwrite = True
    scene.render.use_placeholder = False
    scene.render.resolution_percentage = 100
    try:
        scene.view_settings.view_transform = "AgX"
    except Exception:
        pass
    scene.render.image_settings.color_mode = "RGBA"
    scene.camera = bpy.data.objects.get("CAM_ThreeQuarter")


def build_scene():
    clear_scene()
    # Build in a readable order so parts can be found easily in the Outliner.
    build_ocean_base()
    build_wave()
    build_coastal_details()
    build_surfboard()
    build_surfer()
    build_studio()
    cameras = build_cameras()
    configure_render()
    scene = bpy.context.scene
    scene.camera = cameras["CAM_ThreeQuarter"]
    scene.render.filepath = os.path.join(OUT_DIR, "view_three_quarter")
    return cameras


def render_views(cameras):
    scene = bpy.context.scene
    # Constant orthographic scale and square aspect make all six views comparable.
    view_jobs = [
        ("CAM_ThreeQuarter", "view_three_quarter.png"),
        ("CAM_Front", "view_front.png"),
        ("CAM_Back", "view_back.png"),
        ("CAM_Left", "view_left.png"),
        ("CAM_Right", "view_right.png"),
        ("CAM_Top", "view_top.png"),
    ]
    for camera_name, filename in view_jobs:
        scene.camera = cameras[camera_name]
        scene.render.filepath = os.path.join(OUT_DIR, filename[:-4])
        bpy.ops.render.render(write_still=True)
        print("[SurferFlow] Rendered:", os.path.join(OUT_DIR, filename))
    scene.camera = cameras["CAM_ThreeQuarter"]
    scene.render.filepath = os.path.join(OUT_DIR, "view_three_quarter")


def main():
    cameras = build_scene()
    blend_path = os.path.join(OUT_DIR, ARGS.blend_name)
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print("[SurferFlow] Saved Blender file:", blend_path)
    if not ARGS.no_render:
        render_views(cameras)
        # Persist the reference view as active camera when opening the project.
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print("[SurferFlow] Done. Output folder:", OUT_DIR)


if __name__ == "__main__":
    main()
