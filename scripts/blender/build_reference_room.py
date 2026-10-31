"""Build and export the cozy isometric office from the supplied reference."""
import bpy
import math
import os
from mathutils import Matrix, Vector

ROOT = "/home/psykr/Projects/Om-Portfolio"
OUT = os.path.join(ROOT, "public", "assets", "reference-room.glb")
BLEND = os.path.join(ROOT, "blender", "reference-room.blend")
PREVIEW = os.path.join(ROOT, "blender", "reference-room-preview.png")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# This file runs in a dedicated Blender process and intentionally builds a clean scene.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.cameras, bpy.data.lights, bpy.data.materials):
    for block in list(datablocks):
        if block.users == 0:
            datablocks.remove(block)

def mat(name, color, rough=0.75, emission=None, strength=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Roughness"].default_value = rough
    if emission:
        (bs.inputs.get("Emission Color") or bs.inputs.get("Emission")).default_value = (*emission, 1)
        bs.inputs["Emission Strength"].default_value = strength
    return m

oak = mat("Pale honey oak", (0.55, 0.34, 0.17))
oak2 = mat("Oak variation", (0.63, 0.42, 0.23))
trim = mat("Oak edge", (0.37, 0.22, 0.12))
sage = mat("Muted sage plaster", (0.36, 0.43, 0.42))
ivory = mat("Warm ivory wall", (0.78, 0.72, 0.62))
slat = mat("Ivory wall slats", (0.87, 0.81, 0.71))
white = mat("Soft white", (0.88, 0.85, 0.78))
gray = mat("Desk gray", (0.35, 0.39, 0.38))
dark = mat("Graphite", (0.12, 0.14, 0.14), 0.36)
meshgray = mat("Chair mesh", (0.31, 0.35, 0.34))
blue = mat("Screen glass", (0.10, 0.22, 0.26), 0.2, (0.08, 0.19, 0.22), 0.5)
screen_hi = mat("Screen details", (0.42, 0.69, 0.66), 0.5, (0.35, 0.68, 0.62), 0.6)
plantgreen = [mat("Leaf green", (0.16, 0.31, 0.18)), mat("Leaf sage", (0.31, 0.42, 0.24)), mat("Leaf deep", (0.10, 0.24, 0.15))]
potmat = mat("Muted terracotta", (0.50, 0.29, 0.20))
linen = mat("Rug warm gray", (0.45, 0.45, 0.42))
glow = mat("Warm lamp glow", (1.0, 0.79, 0.52), emission=(1.0, 0.70, 0.40), strength=1.6)
hexglow = mat("Soft hex wall lights", (1.0, 0.83, 0.65), emission=(1.0, 0.75, 0.48), strength=2.0)

def cube(name, loc, size, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        mod = o.modifiers.new("Rounded furniture edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        o.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return o

def cyl(name, loc, radius, depth, material, vertices=20, top=None):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius, radius2=radius if top is None else top, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    return o

def ico(name, loc, scale, material, subdivisions=1):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    o.data.materials.append(material)
    for p in o.data.polygons: p.use_smooth = True
    return o

def rod(name, a, b, radius, material, vertices=10):
    d = Vector(b) - Vector(a)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=d.length, location=(Vector(a)+Vector(b))/2)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    o.data.materials.append(material)
    return o

def leaf(name, origin, direction, length, width, material):
    d = Vector(direction).normalized()
    mid = Vector(origin) + d * length * 0.53
    o = ico(name, mid, (width, width*0.43, length*0.53), material, 2)
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return o

def plant(name, x, y, z, scale=1.0):
    cyl(name+" pot", (x,y,z+0.22*scale), 0.25*scale, 0.44*scale, potmat, 18, 0.31*scale)
    cyl(name+" soil", (x,y,z+0.45*scale), 0.23*scale, 0.03*scale, trim)
    for i in range(9):
        a = i * 2.399
        direction = (math.cos(a)*(0.85+(i%2)*0.12), math.sin(a)*(0.85+(i%2)*0.12), 0.55 + (i%4)*0.18)
        leaf(name+" leaf %02d"%i, (x,y,z+0.48*scale), direction, scale*(0.75+(i%4)*0.10), scale*0.25, plantgreen[i%3])

# The floating cutaway base and warm oak floor.
cube("Diorama shadow base", (0,0,-0.20), (10.8,8.9,0.42), trim, 0.12)
cube("Oak floor top", (0,0,0.025), (10.62,8.72,0.08), oak, 0.04)
for i in range(16):
    y=-4.15+i*0.55
    cube("Floor plank %02d"%i, (0,y,0.085), (10.48,0.53,0.035), oak2 if i%3==0 else oak, 0.006)
# L-shaped walls: left wall muted sage; rear wall ivory vertical boards.
cube("Left sage wall", (-5.12,0,2.53), (0.18,8.55,4.95), sage, 0.03)
cube("Rear ivory wall", (0,4.20,2.53), (10.35,0.18,4.95), ivory, 0.03)
cube("Left wall baseboard", (-4.98,0,0.25), (0.10,8.4,0.25), oak, 0.025)
cube("Rear wall baseboard", (0,4.06,0.25), (10.2,0.10,0.25), oak, 0.025)
for i in range(25):
    x=-4.95+i*0.41
    cube("Vertical wall panel %02d"%i, (x,4.095,2.63), (0.018,0.016,4.30), slat if i%3 else ivory, 0.005)
# Soft daylight curtain panel/window at rear, around the screen position.
cube("Blue daylight window", (1.55,4.075,3.28), (2.45,0.045,2.73), mat("Pale blue window", (0.47,0.62,0.63), emission=(0.37,0.55,0.57), strength=0.25), 0.015)
for i in range(9):
    x=0.42+i*0.28
    cube("Curtain pleat %02d"%i, (x,4.035,3.26), (0.035,0.04,2.66), white if i%2 else ivory, 0.015)

# Rug and compact pale wood desk on rear wall.
cube("Large soft gray rug", (0.35,-0.82,0.17), (6.0,3.56,0.08), linen, 0.06)
desk_x, desk_y = 1.15, 2.62
cube("Desk top", (desk_x,desk_y,1.46), (5.45,1.30,0.16), oak2, 0.07)
cube("Desk front edge", (desk_x,desk_y-0.65,1.43), (5.33,0.035,0.09), white, 0.012)
for x in (-1.15,3.45):
    cube("Slim desk leg", (x,desk_y,0.76), (0.12,1.13,1.30), white, 0.035)
# Left drawer pedestal with three shallow drawers.
cube("Drawer pedestal", (-0.63,2.79,0.82), (0.84,1.08,1.30), oak, 0.07)
for i in range(3):
    z=0.40+i*0.38
    cube("Drawer front %d"%i, (-0.63,2.225,z), (0.73,0.025,0.31), oak2, 0.035)
    cube("Drawer pull %d"%i, (-0.63,2.202,z), (0.18,0.025,0.035), trim, 0.012)
# Monitor with a bespoke graphic UI face and stand.
cube("Monitor dark bezel", (1.60,3.48,2.91), (2.33,0.13,1.68), dark, 0.07)
cube("Monitor display", (1.60,3.405,2.94), (2.08,0.025,1.38), blue, 0.025)
cube("Screen top bar", (1.60,3.384,3.54), (2.03,0.012,0.10), gray, 0.01)
cube("Screen sidebar", (0.81,3.374,2.93), (0.28,0.012,1.05), dark, 0.008)
cube("Screen artwork teal", (1.66,3.375,3.13), (1.62,0.012,0.75), screen_hi, 0.01)
cube("Screen artwork landscape", (1.66,3.365,3.12), (0.79,0.014,0.58), mat("Screen landscape blue", (0.20,0.43,0.48), emission=(0.10,0.32,0.37), strength=0.45), 0.015)
cube("Screen artwork coral", (2.10,3.352,2.97), (0.53,0.016,0.27), mat("Screen landscape ochre", (0.68,0.42,0.27), emission=(0.42,0.20,0.08), strength=0.35), 0.012)
for i in range(4):
    cube("Screen text line %d"%i, (2.17,3.35,2.66+i*0.10), (0.72-(i%2)*0.17,0.012,0.025), white, 0.008)
rod("Monitor stand neck", (1.60,3.48,2.06), (1.60,3.48,2.50), 0.065, gray)
cube("Monitor stand foot", (1.60,3.40,2.02), (0.73,0.46,0.06), gray, 0.03)
# Compact speaker pair.
for x in (0.20,2.97):
    cube("Small speaker", (x,3.28,2.05), (0.38,0.36,0.62), dark, 0.055)
    cyl("Speaker cone", (x,3.085,2.13), 0.11, 0.028, gray, 24)
# Mouse and notebook sit beside the keyboard with clear wrist space.
ico("Mouse", (2.36,2.28,1.58), (0.06,0.12,0.04), dark, 2)
cube("Notebook", (-0.40,2.22,1.57), (0.70,0.52,0.055), white, 0.025)

# Left ladder shelf, books, pinboard, hexagon wall lights.
for y in (-0.42,1.42):
    rod("Shelf upright", (-4.58,y,0.34), (-4.58,y,3.52),0.055,trim)
for i,z in enumerate((0.68,1.42,2.16,2.90)):
    cube("Ladder shelf %d"%i, (-4.28,0.50,z), (0.58,2.03,0.12), oak, 0.035)
for i in range(13):
    y=-0.27+(i%5)*0.34
    z=(0.82,1.56,2.30)[i%3]
    cube("Shelf book %d"%i, (-4.25,y,z), (0.38,0.20,0.42+(i%3)*0.06), [trim,white,sage][i%3], 0.015)
cube("Pinboard frame", (-4.90,1.95,3.35), (0.07,1.55,1.35), trim, 0.04)
cube("Pinboard cork", (-4.85,1.95,3.35), (0.035,1.39,1.19), potmat, 0.025)
for i in range(4):
    cube("Pinned note %d"%i, (-4.82,1.48+i*0.30,3.18+(i%2)*0.38), (0.035,0.22,0.30), white if i%2 else oak2, 0.012)
# Hex tiles represented by flat glowing hexagonal cylinders, attached to left wall.
for i in range(5):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.24, depth=0.05, location=(-4.73, -1.05+i*0.40,3.70+i*0.19), rotation=(0,math.pi/2,0))
    bpy.context.object.name="Hex light %d"%i
    bpy.context.object.data.materials.append(hexglow)

# Tall tripod floor lamp front-left.
lx,ly=-4.10,-2.72
for dx,dy in ((-0.36,-0.22),(0.36,-0.22),(0,0.30)):
    rod("Tripod lamp leg", (lx,ly,0.14),(lx+dx,ly+dy,2.08),0.035,trim)
cyl("Lamp stem", (lx,ly,1.76),0.045,0.80,trim)
cyl("Cream tripod lamp shade", (lx,ly,2.33),0.47,0.52,white,32,0.42)
cyl("Lamp shade glowing diffuser", (lx,ly,2.07),0.39,0.025,glow,32)

# Broad-leaf plants in the room corners and on a shelf.
plant("Large right plant",4.14,-2.84,0.15,1.15)
plant("Small shelf plant",-4.24,0.74,2.97,0.48)
plant("Corner floor plant",-3.78,2.88,0.15,0.82)
plant("Desk corner plant",4.35,2.38,0.15,0.72)

# Scale the blockout shell and built-in props to physical room dimensions.
for obj in list(bpy.context.scene.objects):
    if obj.type == "MESH":
        obj.location *= 0.5
        obj.scale *= 0.5


def import_model_asset(filepath, label, location, scale=(1.0, 1.0, 1.0), rotation_z=0.0):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=filepath)
    imported = [obj for obj in bpy.data.objects if obj not in before]
    mesh_objects = [obj for obj in imported if obj.type == "MESH"]
    if not mesh_objects:
        raise RuntimeError("No meshes imported from " + filepath)
    points = [obj.matrix_world @ Vector(corner) for obj in mesh_objects for corner in obj.bound_box]
    low = Vector(tuple(min(p[i] for p in points) for i in range(3)))
    high = Vector(tuple(max(p[i] for p in points) for i in range(3)))
    anchor = Vector(((low.x + high.x) * 0.5, (low.y + high.y) * 0.5, low.z))
    imported_set = set(imported)
    top_level = [obj for obj in imported if obj.parent not in imported_set]
    root = bpy.data.objects.new(label + " placement", None)
    bpy.context.scene.collection.objects.link(root)
    for obj in top_level:
        world_matrix = obj.matrix_world.copy()
        obj.parent = root
        obj.matrix_parent_inverse = Matrix.Identity(4)
        obj.matrix_world = world_matrix
    rotation = Matrix.Rotation(rotation_z, 4, "Z")
    scale_matrix = Matrix.Diagonal((scale[0], scale[1], scale[2], 1.0))
    root.matrix_world = Matrix.Translation(Vector(location)) @ rotation @ scale_matrix @ Matrix.Translation(-anchor)
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in mesh_objects:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        baked = mesh.copy()
        baked.transform(evaluated.matrix_world)
        evaluated.to_mesh_clear()
        obj.data = baked
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
    asset.data.transform(Matrix.Translation(-Vector(location)))
    asset.location = location
    bpy.data.objects.remove(root, do_unlink=True)
    asset["source_asset_file"] = os.path.relpath(filepath, ROOT)
    asset["source_asset_license"] = "CC0"
    return asset

# Chair faces the desk: its upholstered back is rotated away from the monitor.
# Keyboard is a full-size 44 cm model, centered with the monitor and 7 cm behind the desk edge.
chair_asset = import_model_asset(os.path.join(ROOT,"blender","assets","ergonomic-chair.glb"), "Ergonomic office chair", (0.78,0.40,0.0), scale=(1.0,1.0,0.92), rotation_z=math.pi)
chair_materials = {
    "satin hardware": mat("Chair satin hardware", (0.43,0.46,0.45), 0.48),
    "coat |": mat("Chair shell soft graphite", (0.30,0.34,0.33), 0.58),
    "charcoal |": mat("Chair frame graphite", (0.17,0.20,0.20), 0.62),
    "woven upholstery": mat("Soft graphite chair upholstery", (0.43,0.47,0.45), 0.88),
    "tailored welt": mat("Chair upholstery piping", (0.29,0.32,0.31), 0.82),
}
for index, existing in enumerate(chair_asset.data.materials):
    if not existing:
        continue
    for marker, replacement in chair_materials.items():
        if marker in existing.name.lower():
            chair_asset.data.materials[index] = replacement
            break
import_model_asset(os.path.join(ROOT,"blender","assets","mechanical-keyboard.glb"), "Full-size mechanical keyboard", (0.78,1.12,0.775))

# Soft studio lighting and isometric preview.
world=bpy.data.worlds.new("Soft blue gray studio")
world.use_nodes=True
world.node_tree.nodes["Background"].inputs["Color"].default_value=(0.25,0.30,0.32,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value=0.24
scene=bpy.context.scene
scene.world=world
scene.render.engine="BLENDER_EEVEE"
scene.eevee.taa_render_samples=16
scene.render.resolution_x=836
scene.render.resolution_y=978
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.film_transparent=False
scene.render.image_settings.color_mode="RGBA"
scene.view_settings.view_transform="Standard"
scene.render.image_settings.color_depth="8"
scene.camera=None

def area(name, loc, energy, color, size, target):
    data=bpy.data.lights.new(name,"AREA")
    data.energy=energy; data.color=color; data.shape="DISK"; data.size=size
    obj=bpy.data.objects.new(name,data); scene.collection.objects.link(obj); obj.location=loc
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()

area("Late afternoon key",(-2.5,-3,5),380,(1.0,0.77,0.57),3.5,(0,0,0.6))
area("Cool window fill",(1.5,2,3.5),240,(0.63,0.80,0.92),2.5,(0,0,0.75))
camdata=bpy.data.cameras.new("Reference isometric camera")
camera=bpy.data.objects.new("Reference isometric camera",camdata); scene.collection.objects.link(camera)
camera.location=(6.5,-8.5,7.25)
camera.rotation_euler=(Vector((0,0,1.025))-camera.location).to_track_quat("-Z","Y").to_euler()
camdata.type="ORTHO"; camdata.ortho_scale=8.0; scene.camera=camera
scene.render.filepath=PREVIEW
scene.camera.data.dof.use_dof=False

bpy.ops.wm.save_as_mainfile(filepath=BLEND)
# Export all visible meshes. Keep camera/lights for the editable Blender scene only.
bpy.ops.object.select_all(action="DESELECT")
for obj in bpy.context.scene.objects:
    if obj.type == "MESH": obj.select_set(True)
bpy.context.view_layer.objects.active=next(o for o in bpy.context.scene.objects if o.type=="MESH")
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", use_selection=True, export_apply=True, export_materials="EXPORT", export_image_format="AUTO", export_cameras=False, export_lights=False)
bpy.ops.render.render(write_still=True)
print("EXPORTED",OUT,os.path.getsize(OUT),"bytes")
print("BLEND",BLEND)
print("PREVIEW",PREVIEW)
