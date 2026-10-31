import bpy
import math
from mathutils import Vector

SCENE = bpy.data.scenes.get("Pastel Ocean Surfer Diorama") or bpy.context.scene
COL = bpy.data.collections.get("Ocean Surfer Diorama")
if COL is None:
    COL = bpy.data.collections.new("Ocean Surfer Diorama")
    SCENE.collection.children.link(COL)


def mat(name):
    return bpy.data.materials.get(name)


def add_uv(name, loc, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=14, radius=1, location=loc)
    obj = bpy.context.object
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    COL.objects.link(obj)
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material)
    for face in obj.data.polygons:
        face.use_smooth = True
    return obj


def add_curve(name, points, material, radius, cyclic=False):
    data = bpy.data.curves.new(name + " Curve", "CURVE")
    data.dimensions = "3D"
    data.resolution_u = 16
    data.bevel_depth = radius
    data.bevel_resolution = 5
    spline = data.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for bp, point in zip(spline.bezier_points, points):
        bp.co = point
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    spline.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, data)
    COL.objects.link(obj)
    data.materials.append(material)
    return obj


# The reference wave rises across the tile from front-left to back-right. Its
# cross-section is therefore X/Z and its width is extruded across Y.
old_wave = bpy.data.objects.get("Tall curling breaker")
for obj in list(bpy.data.objects):
    if obj.name.startswith(("Tall curling breaker", "Continuous foam", "Irregular crest foam",
                           "Foam crest cloud", "Foamy breaking lip", "Foam cascade lobe",
                           "Foam lobe", "Curving irregular crest foam", "Irregular flowing foam lip",
                           "Foam crest cloud", "Foam crest", "Puffy crest foam", "Foam_Crest_")):
        bpy.data.objects.remove(obj, do_unlink=True)

sea = mat("Turquoise water") or mat("Lagoon depth")
sea_light = mat("Mint current") or sea
foam = mat("Foam light") or mat("Cream foam")
foam_cream = mat("Cream foam") or foam

profile = [
    (-2.55, .86), (-2.08, .92), (-1.68, 1.10), (-1.32, 1.43),
    (-1.02, 1.86), (-.73, 2.32), (-.36, 2.72), (.12, 3.02),
    (.67, 3.14), (1.12, 3.02), (1.38, 2.77), (1.30, 2.55),
    (1.03, 2.42), (.76, 2.35), (.54, 2.22), (.36, 1.96),
    (.18, 1.48), (.04, .88),
]


def catmull(a, b, c, d, t):
    return tuple(.5 * ((2 * y) + (-x + z) * t + (2*x - 5*y + 4*z - w) * t*t
                       + (-x + 3*y - 3*z + w) * t*t*t)
                 for x, y, z, w in zip(a, b, c, d))


path = []
for index in range(len(profile) - 1):
    p0 = profile[max(index - 1, 0)]
    p1 = profile[index]
    p2 = profile[index + 1]
    p3 = profile[min(index + 2, len(profile) - 1)]
    for step in range(6):
        path.append(catmull(p0, p1, p2, p3, step / 6))
path.append(profile[-1])

width_steps = 56
ymin, ymax = -.45, 2.25
vertices, faces = [], []
for j, (x, z) in enumerate(path):
    for i in range(width_steps + 1):
        t = i / width_steps
        y = ymin + (ymax - ymin) * t
        edge = math.sin(math.pi * t) ** .24
        # Softly lift the back/right portion, but keep both wave ends grounded.
        right_peak = 1 + .13 * math.exp(-((t - .73) / .24) ** 2)
        xx = x + .10 * math.sin(math.pi * t) * (t - .22)
        zz = .86 + (z - .86) * edge * right_peak
        vertices.append((xx, y, zz))
for j in range(len(path) - 1):
    for i in range(width_steps):
        a = j * (width_steps + 1) + i
        faces.append((a, a + 1, a + width_steps + 2, a + width_steps + 1))
mesh = bpy.data.meshes.new("Wave Cross Section XZ Extruded Across Y")
mesh.from_pydata(vertices, [], faces)
mesh.materials.append(sea)
wave = bpy.data.objects.new("Tall curling breaker", mesh)
COL.objects.link(wave)
for face in mesh.polygons:
    face.use_smooth = True
solid = wave.modifiers.new("Wave shell thickness", "SOLIDIFY")
solid.thickness = .13
solid.offset = 0
bevel = wave.modifiers.new("Rounded breaker edge", "BEVEL")
bevel.width = .035
bevel.segments = 3
wave.modifiers.new("Wave surface normals", "WEIGHTED_NORMAL")

# The wave occupies the back/right quadrant so its hook frames rather than
# hides the surfer. The narrower depth leaves the barrel opening visible.
# Turquoise flow bands follow the X/Z wave face and stay inside the tile.
for idx, shift in enumerate((-.15, .35, .85, 1.35)):
    pts = [(-2.42, shift, .92), (-1.78, shift, 1.12), (-1.20, shift, 1.70),
           (-.65, shift, 2.34), (-.14, shift, 2.82), (.48, shift, 3.02),
           (1.02, shift, 2.86)]
    add_curve("Wave flow band %02d" % idx, pts, sea_light, .032 if idx % 2 else .046)

# Foam traces the upper contour across the far half and curls down the right lip.
crest_profile = [(-.32, 2.64), (.12, 3.02), (.67, 3.14), (1.12, 3.02),
                 (1.38, 2.77), (1.30, 2.55), (1.03, 2.42), (.76, 2.35)]
foam_y = 1.58
add_curve("Continuous crest foam edge", [(x, foam_y, z + .045) for x, z in crest_profile], foam_cream, .115)
for i, (x, z) in enumerate(crest_profile):
    # Irregular connected puffs: varied size, slightly staggered, not a uniform row.
    radius = (.14, .22, .18, .25, .17, .23, .15, .19)[i]
    add_uv("Crest foam lobe %02d" % i,
           (x + .03 * math.sin(i * 2), foam_y + .02 * math.cos(i), z + .08),
           (radius * 1.28, radius * .86, radius * .82), foam if i % 3 else foam_cream)

# Shore foam wraps the foot of the breaker and branches into two irregular wash lines.
add_curve("Breaker foot foam", [(-1.68, .18, .98), (-1.18, -.05, .97), (-.48, -.20, .96),
                                 (.30, -.28, .96), (1.12, -.20, .96), (1.80, .12, .96)], foam_cream, .085)
add_curve("Front shore foam", [(-2.92, -2.45, .91), (-2.24, -2.24, .93), (-1.72, -2.52, .92),
                                (-.90, -2.46, .92), (-.26, -2.20, .92), (.38, -2.32, .92)], foam_cream, .073)
add_curve("Left wash foam", [(-2.85, -1.92, .92), (-2.48, -1.48, .94), (-2.32, -.95, .94),
                              (-1.96, -.55, .95), (-1.55, -.45, .96)], foam, .065)

# Keep sparse individual spray drops near the upper lip only.
for i, (x, y, z, r) in enumerate([(-.70, 1.95, 3.55, .09), (-.14, 2.08, 3.68, .11),
                                   (.58, 2.13, 3.72, .075), (1.34, 2.18, 3.45, .10)]):
    add_uv("Wave spray %02d" % i, (x, y, z), (r, r * .84, r), foam)

# Compact the existing succulent and rocks into the far-left corner per the top view.
for obj in bpy.data.objects:
    if obj.name.startswith(("Rounded shoreline rock", "Succulent leaf")):
        obj.location.x -= .35
        obj.location.y += .45
        obj.scale *= .82

# Add foam chips around the rocks, contained within the plinth footprint.
add_uv("Coastal foam 1", (-2.72, 2.57, .94), (.22, .13, .08), foam)
add_uv("Coastal foam 2", (-2.03, 2.69, .94), (.16, .12, .07), foam)

# Rotate board/rider as a pair on the diagonal shown by top/isometric references.
board = bpy.data.objects.get("Long ivory surfboard")
surfer_names = ("Surfer", "Bent left", "Right bent", "Left lower", "Right lower", "Left planted", "Right planted")
for obj in bpy.data.objects:
    if obj is board or obj.name.startswith(surfer_names):
        # Undo prior experimental offsets from the previous checkpoint, then
        # apply one shared diagonal placement around the center of the tile.
        if obj is board:
            obj.location = (.05, -.62, 1.18)
            obj.rotation_euler[2] = 0
        else:
            obj.location.x += .48
            obj.location.y -= .22
            obj.rotation_euler[2] -= math.radians(8)
        angle = math.radians(32)
        x, y = obj.location.x, obj.location.y
        obj.location.x = x * math.cos(angle) - y * math.sin(angle) + .10
        obj.location.y = x * math.sin(angle) + y * math.cos(angle) - .28
        obj.rotation_euler[2] += angle

# Reframe at a closer 3/4 isometric read and preserve the original studio setup.
camera = bpy.data.objects.get("Diorama Isometric Camera")
if camera:
    camera.location = (7.7, -9.5, 7.7)
    camera.rotation_euler = (Vector((0, 0, 1.45)) - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 7.8

SCENE.render.resolution_x = SCENE.render.resolution_y = 1200
SCENE.render.resolution_percentage = 100
SCENE.render.image_settings.file_format = "PNG"
SCENE.render.filepath = "/tmp/surferflow-final.png"
SCENE.camera = camera
SCENE.render.engine = "BLENDER_EEVEE"
if bpy.context.window:
    bpy.context.window.scene = SCENE
bpy.ops.wm.save_as_mainfile(filepath="/home/psykr/Projects/Om-Portfolio/blender/pastel-ocean-surfer-diorama.blend")
bpy.ops.render.render(write_still=True)
print("Saved and rendered SurferFlow: objects=", len(SCENE.objects), "camera=", camera.name)
