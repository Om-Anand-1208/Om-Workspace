"""Build an editable Blender master from the untouched my-room-in-3d sources.

Run inside Blender. The script intentionally does not export or modify the
portfolio website. It imports the source project's GLBs, assigns source
textures, separates the baked room mesh into connected components, adds the
dynamic source-code layers, organizes everything, and saves a reusable .blend.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import bpy
from mathutils import Vector


SOURCE_ROOT = Path("/home/psykr/Projects/my-room-in-3d")
ASSET_ROOT = SOURCE_ROOT / "static" / "assets"
OUTPUT_BLEND = Path(
    "/home/psykr/Projects/Om-Portfolio/blender/original-room-editable-master.blend"
)

# Exact 64-bit prefixes of SHA-256 component fingerprints. Each fingerprint is
# derived from vertex count, face count, and 3-decimal world bounds after GLB
# import. All 73 entries were visually verified as guitar or octopus geometry.
REMOVED_COMPONENT_DIGESTS = frozenset(
    """
03480bd7bb04bac0 0ca59cade017da03 14dc7c66063cf720 1fed8ea0413370d9
229c4cb86d44b1d4 23029fc4813f337d 24e6d4762ae5364a 2a833020d5bce8be
2cffab51d03e79d2 30839a78e15113aa 35985300a4aac7bb 366fe18d8b46f881
374c61507fe78c87 3b3272c991468df8 3f4e301378e4a686 41ae4a4f26d7f29d
441315acb458a3ca 44b4ba1fc2bf51f7 495336ea1964bd4f 49d5a9d6f4c3b816
50a405d92b70fcd0 540e5e72f8631105 5619cd4be8e6a3f4 5c8bb14233f01c81
5e0d9631345e05b8 629db5161cbdac68 6853a61d6d439e3c 68a90b7f750eb3b5
6aad9900bf53670a 6f96d75a3f7ac01e 7393baf13aeadb37 769074388d2901c1
76c65041460d2aae 7d4c16a6808b93c6 7ed6f6c213273838 85803fe1b6dc9cc0
88dbe2b74a10c4b8 8a1620082850e18e 8af7d1a3fd392be4 8b61bc7134891b29
8c2372d79f7ca709 8f0201c0cab0eb53 9383de567fd26b61 95432e4639b5c857
9552e6043abda54c 968c2862598fa9f6 9aed8a15cb8fca54 9b9115056204bea4
9c5b6f57544e3283 9fc2d809491e357f ace7e95de38a525c ae3b6448c7269e9d
aed9cbcdcdd277a9 b06c3cb35d21326d b0968199794678f8 b1968ad0d4f6bed9
b2102dda5df39242 b3567bc66dd17c04 b5644bb4fb304f65 c601363e69073608
c824b109d64b59f5 d1f4d8c144b3a958 d376fbe539c3c4f7 d5862379fa4c7a3f
da27631c7ecf15d3 ecd277c126853764 f330ef2afe6c8673 f4f8d40f28917f80
f53b15763de45547 f7deecf901d2ed26 f7f79a2f3726a683 faf6cc13a8f46a91
fc06cbd3d8a8bf39
""".split()
)

def clear_scene() -> None:
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    for collection in list(bpy.data.collections):
        bpy.data.collections.remove(collection)
    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.cameras,
        bpy.data.lights,
        bpy.data.materials,
        bpy.data.images,
    ):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def make_collection(name: str, parent: bpy.types.Collection | None = None):
    collection = bpy.data.collections.new(name)
    if parent is None:
        bpy.context.scene.collection.children.link(collection)
    else:
        parent.children.link(collection)
    return collection


def move_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection.objects.link(obj)


def make_emission_texture_material(name: str, image_path: Path, strength: float = 1.0):
    image = bpy.data.images.load(str(image_path), check_existing=True)
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Strength"].default_value = strength
    texture = nodes.new("ShaderNodeTexImage")
    texture.image = image
    texture.interpolation = "Linear"
    links.new(texture.outputs["Color"], emission.inputs["Color"])
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return material


def make_color_material(name: str, color: tuple[float, float, float, float], emission=0.0):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    principled = next(
        node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED"
    )
    principled.inputs["Base Color"].default_value = color
    principled.inputs["Roughness"].default_value = 0.45
    if "Emission Color" in principled.inputs:
        principled.inputs["Emission Color"].default_value = color
        principled.inputs["Emission Strength"].default_value = emission
    return material


def world_bounds(obj: bpy.types.Object):
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    low = tuple(min(point[axis] for point in corners) for axis in range(3))
    high = tuple(max(point[axis] for point in corners) for axis in range(3))
    return low, high


def bbox_center(low, high):
    return tuple((low[index] + high[index]) * 0.5 for index in range(3))


def is_removed_source_component(obj: bpy.types.Object) -> bool:
    """Match only exact, visually verified guitar/octopus fingerprints."""
    low, high = world_bounds(obj)
    signature = (
        len(obj.data.vertices),
        len(obj.data.polygons),
        tuple(round(float(value), 3) for value in low),
        tuple(round(float(value), 3) for value in high),
    )
    digest = hashlib.sha256(repr(signature).encode("utf-8")).hexdigest()[:16]
    return digest in REMOVED_COMPONENT_DIGESTS


def in_box(center, low, high):
    return all(low[i] <= center[i] <= high[i] for i in range(3))


def classify_room_part(obj: bpy.types.Object):
    low, high = world_bounds(obj)
    center = bbox_center(low, high)
    dimensions = tuple(high[i] - low[i] for i in range(3))
    largest = max(dimensions)

    # Semantic groups for the source-code office corner. The objects remain
    # separate loose pieces inside each group, so keys, leaves, pots, frames,
    # cables, and stands stay individually selectable.
    if (
        in_box(center, (-0.40, 3.30, 1.84), (0.60, 3.62, 2.05))
        or in_box(center, (1.82, 3.18, 1.84), (2.22, 3.66, 2.05))
    ):
        return "14_External_Keyboards", "ExternalKeyboard"
    if in_box(center, (1.30, 3.30, 2.00), (2.75, 3.84, 2.40)):
        return "17_Mouse_And_Mousepad", "Mouse"
    if in_box(center, (1.35, 3.80, 2.20), (2.90, 4.60, 3.50)):
        return "13_Laptop", "Laptop"
    if in_box(center, (-1.05, 4.40, 2.30), (1.80, 5.12, 4.80)):
        return "12_Monitor_And_Stand", "Monitor"
    if in_box(center, (-0.80, 2.85, 2.20), (0.00, 3.65, 3.05)):
        return "15_Microphone", "Microphone"
    if center[1] > 3.35 and center[0] < -2.45:
        return "11_Shelf_Books_Decor", "Shelf"
    if center[1] > 2.85 and center[0] > 2.85 and center[2] > 1.75:
        return "16_Office_Plants_Pots", "OfficePlant"
    if center[1] > 2.75 and center[2] > 1.70:
        return "10_Office_Desk_And_Props", "Office"

    # Large room shell pieces are kept together in an architecture collection.
    if largest > 4.0 or (
        center[2] < 0.30 and dimensions[0] > 2.0 and dimensions[1] > 2.0
    ):
        return "00_Architecture", "Architecture"
    if center[0] < -1.20 and center[1] < 2.75:
        return "20_Living_Seating", "LivingSeating"
    if -2.20 <= center[0] <= 2.20 and center[1] < 2.75:
        return "21_Coffee_Table_And_Props", "CoffeeTable"
    if center[0] > 2.20 and center[1] < 3.25:
        return "22_TV_Wall_And_Console", "MediaWall"
    return "30_Decor_And_Transition", "Decor"


def import_gltf(path: Path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    return [obj for obj in bpy.data.objects if obj not in before]


def assign_material(obj: bpy.types.Object, material: bpy.types.Material) -> None:
    if obj.type != "MESH":
        return
    obj.data.materials.clear()
    obj.data.materials.append(material)


def add_movie_material(name: str, movie_path: Path):
    image = bpy.data.images.load(str(movie_path), check_existing=True)
    image.source = "MOVIE"
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    texture = nodes.new("ShaderNodeTexImage")
    texture.image = image
    texture.image_user.use_auto_refresh = True
    links.new(texture.outputs["Color"], emission.inputs["Color"])
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return material


def add_source_camera(master: bpy.types.Collection) -> None:
    camera_data = bpy.data.cameras.new("Source_Web_Camera")
    camera_data.lens = 127.0  # approximately Three.js 20 degree vertical FOV
    camera_data.clip_start = 0.1
    camera_data.clip_end = 150.0
    camera = bpy.data.objects.new("Source_Web_Camera", camera_data)
    master.objects.link(camera)

    # Three.js default view converted from Y-up to Blender Z-up.
    camera.location = (-18.902, -18.902, 13.620)
    target = Vector((0.0, 0.0, 2.0))
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = camera


def add_bouncing_logo(collection: bpy.types.Collection):
    # Exact static source-code pose. Three.js PlaneGeometry(4, 1), rotated -90
    # degrees around Y, then scaled Y=.359 and Z=.424.
    x = 4.2
    y0, z0 = 2.717, 1.630
    half_y, half_z = 0.5 * 0.359, 2.0 * 0.424
    verts = [
        (x, y0 - half_y, z0 - half_z),
        (x, y0 + half_y, z0 - half_z),
        (x, y0 + half_y, z0 + half_z),
        (x, y0 - half_y, z0 + half_z),
    ]
    mesh = bpy.data.meshes.new("Bouncing_Logo_Mesh")
    mesh.from_pydata(verts, [], [(0, 1, 2, 3)])
    mesh.uv_layers.new(name="UVMap")
    uvs = ((0, 0), (1, 0), (1, 1), (0, 1))
    for loop, uv in zip(mesh.uv_layers.active.data, uvs):
        loop.uv = uv
    obj = bpy.data.objects.new("Bouncing_Logo", mesh)
    collection.objects.link(obj)
    assign_material(
        obj,
        make_emission_texture_material(
            "SRC_ThreeJS_Logo", ASSET_ROOT / "threejsJourneyLogo.png"
        ),
    )
    obj["source_code"] = "src/Experience/BouncingLogo.js"
    return obj


def add_manifest_text(part_count: int, object_count: int) -> None:
    text = bpy.data.texts.get("README_ORIGINAL_ROOM_MASTER") or bpy.data.texts.new(
        "README_ORIGINAL_ROOM_MASTER"
    )
    text.clear()
    text.write(
        f"""ORIGINAL ROOM EDITABLE MASTER

Built from: {SOURCE_ROOT}
Main source: static/assets/roomModel.glb
Source composition: src/Experience/assets.js and src/Experience/World.js

The baked room mesh is split into {part_count} connected pieces.
Total scene objects at save time: {object_count}.
All source UVs are preserved and the room pieces use bakedDay.jpg.
Dynamic source layers (chair top, screens, LEDs, buttons, steam, light,
and bouncing logo) are stored in 90_Source_Code_Layers.
The baked texture and logo are packed. Blender movie textures stay linked to
static/assets/videoPortfolio.mp4 and static/assets/videoStream.mp4.
Guitar/octopus cleanup is performed only after explicit visual confirmation.

Nothing in the portfolio website is exported or changed by this script.
Edit this .blend first; export intentionally happens in a later workflow.
"""
    )


def main() -> None:
    clear_scene()

    master = make_collection("ORIGINAL_ROOM_MASTER")
    room_parts_root = make_collection("01_Baked_Room_Separated", master)
    layers_root = make_collection("90_Source_Code_Layers", master)
    guides = make_collection("99_Guides_And_Reference", master)

    group_collections = {}
    for name in (
        "00_Architecture",
        "10_Office_Desk_And_Props",
        "11_Shelf_Books_Decor",
        "12_Monitor_And_Stand",
        "13_Laptop",
        "14_External_Keyboards",
        "15_Microphone",
        "16_Office_Plants_Pots",
        "17_Mouse_And_Mousepad",
        "20_Living_Seating",
        "21_Coffee_Table_And_Props",
        "22_TV_Wall_And_Console",
        "30_Decor_And_Transition",
    ):
        group_collections[name] = make_collection(name, room_parts_root)

    baked_material = make_emission_texture_material(
        "SRC_Baked_Day", ASSET_ROOT / "bakedDay.jpg"
    )

    imported = import_gltf(ASSET_ROOT / "roomModel.glb")
    room_meshes = [obj for obj in imported if obj.type == "MESH"]
    if len(room_meshes) != 1:
        raise RuntimeError(f"Expected one room mesh, found {len(room_meshes)}")
    room = room_meshes[0]
    room.name = "SOURCE_Room_Combined"
    assign_material(room, baked_material)
    room["source_asset"] = str(ASSET_ROOT / "roomModel.glb")

    # Bake the GLB's import transform into geometry before separation. This
    # keeps every part in correct world coordinates with intuitive transforms.
    bpy.ops.object.select_all(action="DESELECT")
    room.select_set(True)
    bpy.context.view_layer.objects.active = room
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.separate(type="LOOSE")
    bpy.ops.object.mode_set(mode="OBJECT")
    parts = sorted(
        [obj for obj in bpy.context.selected_objects if obj.type == "MESH"],
        key=lambda obj: obj.name,
    )

    # Give every part a useful pivot and durable metadata, then organize it.
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    counters = {}
    for source_index, obj in enumerate(parts, start=1):
        group_name, prefix = classify_room_part(obj)
        counters[group_name] = counters.get(group_name, 0) + 1
        obj.name = f"{prefix}_{counters[group_name]:04d}"
        obj.data.name = f"{obj.name}_Mesh"
        move_to_collection(obj, group_collections[group_name])
        low, high = world_bounds(obj)
        obj["source_asset"] = "roomModel.glb"
        obj["source_component_index"] = source_index
        obj["semantic_group"] = group_name
        obj["vertex_count"] = len(obj.data.vertices)
        obj["face_count"] = len(obj.data.polygons)
        obj["world_bounds_min"] = [round(value, 6) for value in low]
        obj["world_bounds_max"] = [round(value, 6) for value in high]

    # Import the source-code layers exactly as the original World.js composes them.
    source_specs = [
        ("googleHomeLedsModel.glb", "GoogleHome_LED", "Google_Home_LEDs"),
        ("loupedeckButtonsModel.glb", "Loupedeck_Button", "Loupedeck_Buttons"),
        ("topChairModel.glb", "Chair_Upper_Animated", "Chair_Animated_Top"),
        ("coffeeSteamModel.glb", "Coffee_Steam", "Coffee_Steam"),
        ("elgatoLightModel.glb", "Elgato_Light", "Elgato_Light"),
        ("pcScreenModel.glb", "Monitor_Screen_Dynamic", "Monitor_Screen"),
        ("macScreenModel.glb", "Laptop_Screen_Dynamic", "Laptop_Screen"),
    ]
    layer_collections = {}
    for filename, prefix, collection_name in source_specs:
        target = make_collection(collection_name, layers_root)
        layer_collections[filename] = target
        new_objects = import_gltf(ASSET_ROOT / filename)
        meshes = [obj for obj in new_objects if obj.type == "MESH"]
        for index, obj in enumerate(meshes, start=1):
            obj.name = prefix if len(meshes) == 1 else f"{prefix}_{index:02d}"
            obj.data.name = f"{obj.name}_Mesh"
            move_to_collection(obj, target)
            obj["source_asset"] = filename
        for obj in new_objects:
            if obj.type != "MESH":
                move_to_collection(obj, target)

        if filename == "topChairModel.glb":
            for obj in meshes:
                assign_material(obj, baked_material)

    led_colors = (
        (0.01, 0.15, 1.0, 1.0),
        (1.0, 0.0, 0.0, 1.0),
        (1.0, 0.15, 0.0, 1.0),
        (0.2, 0.65, 0.02, 1.0),
    )
    for index, obj in enumerate(
        sorted(layer_collections["googleHomeLedsModel.glb"].objects, key=lambda item: item.name)
    ):
        if obj.type == "MESH":
            assign_material(
                obj,
                make_color_material(
                    f"SRC_Google_LED_{index + 1}", led_colors[index % 4], emission=3.0
                ),
            )

    button_colors = (
        (0.55, 0.12, 0.8, 1.0),
        (0.86, 0.65, 0.08, 1.0),
        (0.95, 0.2, 0.03, 1.0),
        (0.55, 0.03, 0.18, 1.0),
    )
    for index, obj in enumerate(
        sorted(layer_collections["loupedeckButtonsModel.glb"].objects, key=lambda item: item.name)
    ):
        if obj.type == "MESH":
            assign_material(
                obj,
                make_color_material(
                    f"SRC_Loupedeck_{index + 1}", button_colors[index % 4], emission=1.5
                ),
            )

    white_light = make_color_material("SRC_Elgato_White", (1, 1, 1, 1), emission=5.0)
    for obj in layer_collections["elgatoLightModel.glb"].objects:
        assign_material(obj, white_light)

    steam_material = make_color_material(
        "SRC_Coffee_Steam_Preview", (0.64, 0.30, 0.25, 0.22), emission=0.3
    )
    for obj in layer_collections["coffeeSteamModel.glb"].objects:
        assign_material(obj, steam_material)

    monitor_movie = add_movie_material(
        "SRC_Monitor_Video", ASSET_ROOT / "videoPortfolio.mp4"
    )
    laptop_movie = add_movie_material(
        "SRC_Laptop_Video", ASSET_ROOT / "videoStream.mp4"
    )
    for obj in layer_collections["pcScreenModel.glb"].objects:
        assign_material(obj, monitor_movie)
    for obj in layer_collections["macScreenModel.glb"].objects:
        assign_material(obj, laptop_movie)

    logo_collection = make_collection("Bouncing_Logo", layers_root)
    add_bouncing_logo(logo_collection)

    add_source_camera(guides)

    # A neutral world makes the emission-baked source textures readable.
    world = bpy.data.worlds.new("Source_Room_World")
    world.use_nodes = True
    background = next(node for node in world.node_tree.nodes if node.type == "BACKGROUND")
    background.inputs["Color"].default_value = (0.025, 0.025, 0.025, 1.0)
    background.inputs["Strength"].default_value = 0.25
    bpy.context.scene.world = world
    bpy.context.scene.render.engine = "BLENDER_EEVEE"
    bpy.context.scene.render.resolution_x = 1600
    bpy.context.scene.render.resolution_y = 1000
    bpy.context.scene.render.resolution_percentage = 50
    bpy.context.scene.render.image_settings.file_format = "PNG"
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.scale_length = 1.0

    add_manifest_text(len(parts), len(bpy.context.scene.objects))
    bpy.ops.object.select_all(action="DESELECT")

    OUTPUT_BLEND.parent.mkdir(parents=True, exist_ok=True)
    # Pack supported static resources into the master. Blender keeps movie
    # textures external, so their original source paths remain in the file.
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(
        filepath=str(OUTPUT_BLEND), check_existing=False, compress=True
    )
    print(
        "MASTER_SAVED",
        str(OUTPUT_BLEND),
        "room_parts",
        len(parts),
        "scene_objects",
        len(bpy.context.scene.objects),
    )
    print("GROUP_COUNTS", dict(sorted(counters.items())))


if __name__ == "__main__":
    main()
