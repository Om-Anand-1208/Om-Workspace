import bpy
import math
from mathutils import Vector

# Rebuild only the standalone diorama collection. The portfolio room is a
# separate scene and is deliberately left alone.
old = bpy.data.scenes.get("Pastel Ocean Surfer Diorama")
old_collection = bpy.data.collections.get("Ocean Surfer Diorama")
if old_collection:
    for obj in list(old_collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
if old:
    bpy.data.scenes.remove(old)
if old_collection:
    bpy.data.collections.remove(old_collection)
scene = bpy.data.scenes.new("Pastel Ocean Surfer Diorama")
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = "Standard"
world = bpy.data.worlds.new("Peach Studio World")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.95, 0.57, 0.46, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.48
scene.world = world
collection = bpy.data.collections.new("Ocean Surfer Diorama")
scene.collection.children.link(collection)


def material(name, color, roughness=0.66):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Roughness"].default_value = roughness
    return mat


def adopt(obj, mat=None):
    for users_collection in list(obj.users_collection):
        users_collection.objects.unlink(obj)
    collection.objects.link(obj)
    if mat:
        obj.data.materials.append(mat)
    return obj


def cube(name, location, dimensions, mat, bevel=0.1):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = adopt(bpy.context.object, mat)
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    modifier = obj.modifiers.new("Rounded edges", "BEVEL")
    modifier.width = bevel
    modifier.segments = 5
    obj.modifiers.new("Corner normals", "WEIGHTED_NORMAL")
    return obj


def ball(name, location, scale, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, location=location)
    obj = adopt(bpy.context.object, mat)
    obj.name = name
    obj.scale = scale
    for face in obj.data.polygons:
        face.use_smooth = True
    return obj


def line(name, points, radius, mat):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = radius
    curve.bevel_resolution = 4
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for bp, point in zip(spline.bezier_points, points):
        bp.co = point
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    curve.materials.append(mat)
    return obj


lagoon = material("Lagoon depth", (0.04, 0.29, 0.32))
turquoise = material("Turquoise water", (0.055, 0.41, 0.40))
mint = material("Mint current", (0.18, 0.56, 0.52))
sea_glass = material("Sea glass current", (0.28, 0.68, 0.62))
muted_cream_current = material("Muted cream current", (0.74, 0.70, 0.61), roughness=.86)
foam = material("Cream foam", (0.96, 0.87, 0.71))
foam_light = material("Foam light", (1.0, 0.94, 0.82))
board_mat = material("Ivory surfboard", (1.0, 0.83, 0.6))
rock_mat = material("Blush stone", (0.39, 0.29, 0.25))
leaf_mat = material("Succulent green", (0.27, 0.43, 0.21))
skin = material("Warm skin", (0.78, 0.38, 0.23))
hair = material("Chestnut hair", (0.22, 0.08, 0.05))
shirt = material("Vanilla tee", (1.0, 0.87, 0.68))
shorts = material("Teal shorts", (0.04, 0.39, 0.43))
peach = material("Peach studio", (0.94, 0.49, 0.4))

# Thick rounded square plinth and top sheet of ocean.
cube("Square turquoise plinth", (0, 0, 0.3), (6.5, 6.5, 0.86), lagoon, 0.22)
cube("Lagoon top", (0, 0, 0.77), (6.38, 6.38, 0.12), turquoise, 0.08)

# A compact, curled breaker behind the rider. This closed cross-section has an
# obvious overhang and hollow, rather than reading as a flat wall across the tile.
profile = [(-1.28, .86), (-.82, .94), (-.34, 1.18), (.05, 1.58), (.36, 2.12),
           (.58, 2.70), (.63, 3.08), (.42, 3.34), (-.04, 3.40), (-.38, 3.25),
           (-.56, 2.98), (-.43, 2.74), (-.12, 2.54), (.22, 2.30),
           (.40, 1.86), (.39, 1.29), (.26, .88)]


def catmull(p0, p1, p2, p3, t):
    return tuple(.5 * ((2*b) + (-a+c)*t + (2*a-5*b+4*c-d)*t*t + (-a+3*b-3*c+d)*t*t*t)
                 for a, b, c, d in zip(p0, p1, p2, p3))


def water_ribbon(name, route, half_width, mat):
    centers = []
    for i in range(len(route)-1):
        p0, p1 = route[max(i-1,0)], route[i]
        p2, p3 = route[i+1], route[min(i+2,len(route)-1)]
        for step in range(8):
            centers.append(catmull(p0,p1,p2,p3,step/8))
    centers.append(route[-1])
    verts, faces = [], []
    for i,(x,y) in enumerate(centers):
        before = centers[max(i-1,0)]
        after = centers[min(i+1,len(centers)-1)]
        dx,dy = after[0]-before[0], after[1]-before[1]
        length = max(math.hypot(dx,dy),1e-6)
        px,py = -dy/length,dx/length
        edge_softness = 1 + .10*math.sin(i*.21+.7) + .045*math.sin(i*.49+1.4)
        local_width = half_width*edge_softness
        verts.extend(((x+px*local_width,y+py*local_width,.858),
                      (x-px*local_width,y-py*local_width,.858)))
    for i in range(len(centers)-1):
        a = 2*i
        faces.append((a,a+1,a+3,a+2))
    mesh = bpy.data.meshes.new(name+" Mesh")
    mesh.from_pydata(verts,[],faces)
    mesh.materials.append(mat)
    obj = bpy.data.objects.new(name,mesh)
    collection.objects.link(obj)
    for face in mesh.polygons:
        face.use_smooth = True
    solid = obj.modifiers.new("Soft water ribbon lift","SOLIDIFY")
    solid.thickness = .018
    solid.offset = -1
    bevel = obj.modifiers.new("Rounded ribbon edges","BEVEL")
    bevel.width = .026
    bevel.segments = 4
    obj.modifiers.new("Ribbon normals","WEIGHTED_NORMAL")
    return obj


path = []
for index in range(len(profile)):
    for step in range(8):
        path.append(catmull(profile[(index-1) % len(profile)], profile[index],
                            profile[(index+1) % len(profile)], profile[(index+2) % len(profile)], step/8))
segments = 52
WAVE_X0 = .20
WAVE_WIDTH = 2.82
WAVE_Y_OFFSET = 1.58
vertices, faces = [], []
for j, (y, z) in enumerate(path):
    for i in range(segments+1):
        t = i / segments
        # Keep the swell in the back/right quadrant and taper it at both ends.
        x = WAVE_X0 + WAVE_WIDTH*t
        edge = math.sin(math.pi*t) ** 0.48
        y_local = y + WAVE_Y_OFFSET + .045*math.sin(t*8+j*.08)*edge
        z_local = .84 + (z-.84)*edge
        vertices.append((x, y_local, z_local))
for j in range(len(path)):
    for i in range(segments):
        a = j*(segments+1)+i
        faces.append((a, a+1, ((j+1)%len(path))*(segments+1)+i+1, ((j+1)%len(path))*(segments+1)+i))
mesh = bpy.data.meshes.new("Curling wave surface")
mesh.from_pydata(vertices, [], faces)
mesh.materials.append(turquoise)
wave = bpy.data.objects.new("Tall curling breaker", mesh)
collection.objects.link(wave)
for face in mesh.polygons:
    face.use_smooth = True
wave.modifiers.new("Wave thickness", "SOLIDIFY").thickness = .12
wave.modifiers.new("Soft contours", "SUBSURF").levels = 1

# Thin currents spiral from the open water over the outer face and into the
# curling lip. Their points use the same sampled cross-section as the wave.
for ribbon_index, (t_start, t_end) in enumerate(((.15,.54),(.31,.73),(.48,.91))):
    start_y, start_z = path[0]
    start_x = WAVE_X0 + WAVE_WIDTH*t_start
    water_routes = (
        ((.08,-2.58),(-.42,-2.68),(-.92,-2.39),(-.82,-1.96),(-.32,-1.48),(.22,-1.03),(.63,-.47)),
        ((-.22,-1.92),(-.62,-1.72),(-.35,-1.36),(.18,-1.25),(.48,-.92),(.92,-.52),(1.08,-.05)),
        ((-1.27,-1.55),(-.85,-1.70),(-.34,-1.53),(.19,-1.15),(.78,-.89),(1.28,-.48),(1.55,-.08)),
    )
    water_route = list(water_routes[ribbon_index]) + [(start_x,start_y+WAVE_Y_OFFSET-.05)]
    current_material = (mint, muted_cream_current, sea_glass)[ribbon_index]
    water_ribbon("Open water flow band %02d" % ribbon_index, water_route,
                 (.13,.105,.09)[ribbon_index], current_material)
    ribbon_points = [(start_x,start_y+WAVE_Y_OFFSET-.05,.86)]
    end_step = 12*8
    for step in range(0, end_step+1, 2):
        s = step/end_step
        t = t_start + (t_end-t_start)*s + .045*math.sin(math.pi*s)*math.sin(2*math.pi*s+ribbon_index*.9)
        t = max(.04, min(.96, t))
        edge = math.sin(math.pi*t) ** .48
        y_profile, z_profile = path[step]
        x = WAVE_X0 + WAVE_WIDTH*t
        y = y_profile + WAVE_Y_OFFSET + .045*math.sin(t*8+step*.08)*edge - .055
        z = .84 + (z_profile-.84)*edge + .045
        ribbon_points.append((x,y,z))
    face_material = (mint, sea_glass, turquoise)[ribbon_index]
    line("Spiraling mint current %02d" % ribbon_index, ribbon_points,
         (.050,.045,.040)[ribbon_index], face_material)

# An uneven, joined crest across the lip, with a short lumpy cascade on the
# right-hand edge. The bubbles are sparse and sit close to the crest.
for q in range(13):
    t = q/12
    x = .78 + 1.96*t
    y = 1.36 + .07*math.sin(math.pi*t)
    z = 3.17 - .10*abs(t-.52) + .025*math.sin(q*1.8)
    radius = .18 + .06*(.5+.5*math.sin(q*2.1))
    ball("Puffy crest foam", (x,y,z), (radius*1.38,radius*.95,radius), foam_light if q%4 else foam)
for q, (z, y, radius) in enumerate([(2.93,1.00,.23),(2.68,1.14,.22),(2.43,1.34,.21),
                                    (2.18,1.58,.19),(1.94,1.82,.17),(1.72,1.96,.14)]):
    ball("Foam lip cascade", (2.73 + .028*math.sin(q*1.4),y,z),
         (radius*1.15,radius*1.28,radius*1.35), foam_light if q%2 else foam)
line("Curling foam ribbon", [(0.97,1.49,3.35),(1.43,1.51,3.39),(1.97,1.49,3.35),
     (2.43,1.40,3.25),(2.74,1.18,3.04),(2.81,1.10,2.75),
     (2.78,1.30,2.43),(2.75,1.57,2.10),(2.69,1.83,1.78)], .19, foam_light)
line("Curl foot foam wash", [(2.72,1.74,.87),(2.91,1.96,.87),(2.85,2.18,.87),
     (2.63,2.34,.87),(2.41,2.30,.87)], .075, foam_light)
for location, scale in [((.55,1.60,3.40),(.07,.07,.05)),
                        ((.98,1.72,3.56),(.08,.07,.05))]:
    ball("Foam spray", location, scale, foam_light)

# Two irregular shoreline ribbons and a short curl around the rocks. These read
# as connected wash, not a row of parallel tubes.
line("Foreground foam wash", [(-3.0,-2.23,.86),(-2.63,-1.86,.86),(-2.08,-1.79,.86),
     (-1.78,-2.02,.86),(-1.28,-2.42,.86),(-.64,-2.34,.86),(.08,-2.58,.86)], .050, foam)
line("Left curling foam wash", [(-3.04,-1.34,.86),(-2.74,-.88,.86),(-2.30,-.58,.86),
     (-1.94,-.79,.86),(-1.72,-1.24,.86),(-1.27,-1.55,.86)], .043, foam_light)
# Two compact taupe-rock and succulent clusters on the left edge.
def faceted_rock(name, loc, scale):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1, location=loc)
    obj = adopt(bpy.context.object, rock_mat)
    obj.name = name
    obj.scale = scale
    obj.rotation_euler = (.10,-.13,.21)
    return obj

faceted_rock("Upper shore rock", (-2.30,1.83,1.04), (.39,.31,.32))
faceted_rock("Upper shore pebble", (-1.83,1.77,1.00), (.27,.23,.22))
faceted_rock("Lower shore rock", (-2.24,-2.08,1.02), (.34,.29,.28))
faceted_rock("Lower shore pebble", (-1.79,-2.24,.99), (.23,.20,.19))
for cx, cy, base_z in [(-1.63,1.82,1.15),(-1.61,-2.25,1.13)]:
    for i, angle in enumerate((-.95,-.30,.38,1.02,2.0)):
        leaf = ball("Succulent leaf", (cx+.16*math.cos(angle),cy+.13*math.sin(angle),base_z),
                    (.19,.13,.26 if i%2 else .30), leaf_mat)
        leaf.rotation_euler[1] = .46*math.cos(angle)
        leaf.rotation_euler[0] = .37*math.sin(angle)

# Soft, connected wash wraps both rock clusters and wanders across the front-left
# water in uneven bends, echoing the cream lace in the reference.
line("Back rock foam wash", [(-2.85,1.50,.86),(-2.56,1.35,.86),(-2.21,1.39,.86),
     (-1.88,1.45,.86),(-1.56,1.56,.86),(-1.38,1.82,.86),(-1.58,2.09,.86)], .046, foam_light)
line("Front rock foam wash", [(-2.82,-2.48,.86),(-2.56,-2.73,.86),(-2.20,-2.79,.86),
     (-1.85,-2.72,.86),(-1.55,-2.51,.86),(-1.47,-2.22,.86),(-1.70,-1.97,.86)], .048, foam)
line("Front-left foam lace", [(-2.82,-1.56,.86),(-2.35,-1.66,.86),(-1.95,-1.49,.86),
     (-1.53,-1.73,.86),(-1.08,-1.91,.86),(-.64,-1.75,.86),(-.22,-1.92,.86)], .043, foam_light)

# Diagonal surfboard, directly under the surfer's feet. Keep the board and rider
# as one translated group so later edits cannot separate them.
RIDER_SHIFT = Vector((1.20,.72,0))
RIDER_ROT = 1.17
def rider_pos(p):
    v = Vector(p)
    c, s = math.cos(RIDER_ROT), math.sin(RIDER_ROT)
    return Vector((v.x*c-v.y*s, v.x*s+v.y*c, v.z)) + RIDER_SHIFT

board = cube("Long ivory surfboard", (0,0,1.18), (1.85,.43,.13), board_mat, .19)
board_original = Vector((.05,-.39,1.18))
board.location = rider_pos(board_original)
board.rotation_euler[2] = .48 + RIDER_ROT

# Clay surfer posed low with arms extended.
def limb(name, start, end, radius, mat):
    direction = Vector(end)-Vector(start)
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=radius, depth=direction.length, location=(Vector(start)+Vector(end))/2)
    obj = adopt(bpy.context.object, mat)
    obj.name = name
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    obj.modifiers.new("Soft rounded form", "BEVEL").width = radius*.55
    obj.modifiers.new("Smooth normals", "WEIGHTED_NORMAL")
    return obj


ball("Surfer torso", rider_pos((0,-.10,1.98)), (.29,.23,.37), shirt)
ball("Surfer shorts", rider_pos((0,.03,1.72)), (.29,.23,.23), shorts)
ball("Surfer face", rider_pos((-.06,-.19,2.40)), (.2,.2,.23), skin)
ball("Swept chestnut hair", rider_pos((-.07,-.16,2.55)), (.25,.23,.16), hair)
for i in range(6):
    ball("Hair curl", rider_pos((-.27+i*.085,-.28,2.63+.035*math.sin(i))), (.11,.09,.075), hair)
limb("Left sleeve", rider_pos((-.2,-.08,2.10)),rider_pos((-.51,-.25,1.98)), .11, shirt)
limb("Left arm", rider_pos((-.51,-.25,1.98)),rider_pos((-.86,-.46,1.82)), .075, skin)
ball("Left palm", rider_pos((-.9,-.48,1.80)), (.1,.07,.07), skin)
limb("Right sleeve", rider_pos((.2,-.05,2.10)),rider_pos((.54,.01,2.22)), .11, shirt)
limb("Right arm", rider_pos((.54,.01,2.22)),rider_pos((.9,-.08,2.48)), .075, skin)
ball("Right palm", rider_pos((.94,-.1,2.50)), (.1,.07,.07), skin)
limb("Bent left thigh", rider_pos((-.1,0,1.72)),rider_pos((-.34,-.18,1.47)), .13, shorts)
limb("Bent left shin", rider_pos((-.34,-.18,1.47)),rider_pos((-.48,-.42,1.32)), .095, skin)
ball("Left foot", rider_pos((-.43,-.53,1.27)), (.16,.11,.07), skin)
limb("Right thigh", rider_pos((.1,.02,1.72)),rider_pos((.37,.18,1.58)), .13, shorts)
limb("Right shin", rider_pos((.37,.18,1.58)),rider_pos((.52,-.08,1.33)), .095, skin)
ball("Right foot", rider_pos((.53,-.25,1.28)), (.16,.11,.07), skin)

cube("Peach seamless ground", (0,0,-.2), (200,200,.1), peach, .01)


def area_light(name, location, energy, size, color):
    data = bpy.data.lights.new(name, "AREA")
    data.energy, data.shape, data.size, data.color = energy, "DISK", size, color
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector((0,0,1.3))-obj.location).to_track_quat("-Z", "Y").to_euler()


area_light("Large peach key", (-4,-5,9), 760, 6, (1,.86,.76))
area_light("Mint fill", (4,1,7), 430, 5, (.80,1,.94))
area_light("Warm rim", (1,5,6), 480, 4, (1,.78,.69))
camera_data = bpy.data.cameras.new("Diorama Isometric Camera")
camera = bpy.data.objects.new("Diorama Isometric Camera", camera_data)
collection.objects.link(camera)
camera.location = (8.2,-8.2,10.6)
camera.rotation_euler = (Vector((0,0,1.7))-camera.location).to_track_quat("-Z", "Y").to_euler()
camera_data.type = "ORTHO"
camera_data.ortho_scale = 9.7
scene.camera = camera
if bpy.context.window:
    bpy.context.window.scene = scene
bpy.ops.wm.save_as_mainfile(filepath="/home/psykr/Projects/Om-Portfolio/blender/pastel-ocean-surfer-diorama.blend")
scene.render.resolution_x = scene.render.resolution_y = 900
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = "/tmp/surferflow-final-preview.png"
bpy.ops.render.render(write_still=True)
print("Saved separate diorama scene and render, objects:", len(collection.objects))
