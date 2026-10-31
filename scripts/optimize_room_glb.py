"""Replace the baked RGB PNG inside the room GLB with a high-quality JPEG.

Run after exporting the room from Blender. Requires Pillow. The geometry and
UVs are untouched. The operation is idempotent on already optimized exports.
"""
import io
import json
import struct
import sys
from pathlib import Path
from PIL import Image

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / 'public/assets/original-room-latest.glb'
raw = path.read_bytes()
magic, version, _ = struct.unpack_from('<4sII', raw)
if magic != b'glTF' or version != 2:
    raise ValueError('Expected a GLB 2.0 file')
json_len, json_type = struct.unpack_from('<II', raw, 12)
if json_type != 0x4E4F534A:
    raise ValueError('Expected JSON chunk')
doc = json.loads(raw[20:20 + json_len])
bin_start = 20 + json_len
bin_len, bin_type = struct.unpack_from('<II', raw, bin_start)
if bin_type != 0x004E4942:
    raise ValueError('Expected BIN chunk')
binary = raw[bin_start + 8:bin_start + 8 + bin_len]
image = next(item for item in doc['images'] if item.get('name') == 'bakedDay-shadow-clean-v8')
if image['mimeType'] == 'image/jpeg':
    print('Room texture is already optimized')
    raise SystemExit(0)
view = doc['bufferViews'][image['bufferView']]
start, length = view.get('byteOffset', 0), view['byteLength']
if start + length != len(binary):
    raise ValueError('Expected baked image at end of binary chunk')
texture = Image.open(io.BytesIO(binary[start:start + length]))
if texture.mode != 'RGB':
    raise ValueError('Expected RGB texture without transparency')
out = io.BytesIO()
texture.save(out, format='JPEG', quality=92, subsampling=0, optimize=True)
jpeg = out.getvalue()
view['byteLength'] = len(jpeg)
image['mimeType'] = 'image/jpeg'
binary = binary[:start] + jpeg
binary += b'\0' * (-len(binary) % 4)
doc['buffers'][0]['byteLength'] = len(binary)
encoded = json.dumps(doc, separators=(',', ':')).encode()
encoded += b' ' * (-len(encoded) % 4)
total = 12 + 8 + len(encoded) + 8 + len(binary)
path.write_bytes(struct.pack('<4sII', b'glTF', 2, total) + struct.pack('<II', len(encoded), json_type) + encoded + struct.pack('<II', len(binary), bin_type) + binary)
print(f'{len(raw) / 1024**2:.2f} MiB → {total / 1024**2:.2f} MiB')
