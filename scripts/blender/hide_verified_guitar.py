"""Reversibly hide the user-approved, visually isolated guitar components."""

import bpy


GUITAR_OBJECT_NAMES = [
    "Decor_0010",
    "Decor_0011",
    "Decor_0012",
    "Decor_0013",
    "Decor_0014",
    "Decor_0015",
    "Decor_0016",
    "Decor_0017",
    "Decor_0018",
    "Shelf_0200",
    "Shelf_0201",
    "Shelf_0202",
    "Shelf_0203",
    "Shelf_0204",
    "Shelf_0206",
    "Shelf_0207",
    "Shelf_0208",
    "Shelf_0209",
    "Shelf_0210",
    "Shelf_0211",
    "Shelf_0212",
    "Shelf_0213",
    "Shelf_0214",
    "Shelf_0215",
    "Shelf_0217",
    "Shelf_0218",
    "Shelf_0219",
    "Shelf_0220",
    "Shelf_0221",
    "Shelf_0222",
    "Shelf_0223",
    "Shelf_0224",
    "Shelf_0225",
    "Shelf_0226",
    "Shelf_0228",
    "Shelf_0229",
    "Shelf_0230",
    "Shelf_0231",
    "Shelf_0232",
    "Shelf_0233",
    "Shelf_0234",
    "Shelf_0235",
    "Shelf_0236",
    "Shelf_0238",
    "Shelf_0239",
    "Shelf_0240",
    "Shelf_0241",
    "Shelf_0243",
    "Shelf_0244",
    "Shelf_0245",
    "Shelf_0246",
    "Shelf_0247",
    "Shelf_0248",
    "Shelf_0249",
    "Shelf_0250",
    "Shelf_0252",
    "Shelf_0253",
    "Shelf_0254",
    "Shelf_0255",
    "Shelf_0256",
    "Shelf_0257",
    "Shelf_0258",
    "Shelf_0259",
    "Shelf_0260",
]

missing = [name for name in GUITAR_OBJECT_NAMES if bpy.data.objects.get(name) is None]
if missing:
    raise RuntimeError(f"Missing approved guitar components: {missing}")

removed = bpy.data.collections.get("REMOVED_Guitar_Recoverable")
if removed is None:
    removed = bpy.data.collections.new("REMOVED_Guitar_Recoverable")
    bpy.context.scene.collection.children.link(removed)

for name in GUITAR_OBJECT_NAMES:
    obj = bpy.data.objects[name]
    for collection in list(obj.users_collection):
        collection.objects.unlink(obj)
    removed.objects.link(obj)
    obj.hide_set(True)
    obj.hide_render = True

removed.hide_viewport = True
removed.hide_render = True
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath, check_existing=False, compress=True)
print(f"HIDDEN_APPROVED_GUITAR_OBJECTS={len(GUITAR_OBJECT_NAMES)}")
