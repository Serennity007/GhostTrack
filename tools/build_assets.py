"""Create the small native application icon without external design dependencies."""
from pathlib import Path
import math
import struct


def build_icon(path):
    size = 64
    pixels = bytearray()
    for y in range(size - 1, -1, -1):
        for x in range(size):
            distance = math.hypot(x - 31.5, y - 31.5)
            ring = 18 <= distance <= 22
            # A radar / G mark built from native geometric primitives.
            mark = ring and not (x > 34 and 18 < y < 31)
            mark = mark or (31 <= x <= 51 and 30 <= y <= 34) or (47 <= x <= 51 and 31 <= y <= 43)
            color = (92, 240, 183) if mark else (16, 27, 42)
            alpha = 255 if 3 <= x <= 60 and 3 <= y <= 60 else 0
            pixels.extend((color[2], color[1], color[0], alpha))
    mask = bytes(((size + 31) // 32) * 4 * size)
    bitmap = struct.pack('<IIIHHIIIIII', 40, size, size * 2, 1, 32, 0, len(pixels), 0, 0, 0, 0) + pixels + mask
    icon = struct.pack('<HHH', 0, 1, 1) + struct.pack('<BBBBHHII', size, size, 0, 0, 1, 32, len(bitmap), 22) + bitmap
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(icon)


if __name__ == '__main__':
    build_icon(Path(__file__).resolve().parents[1] / 'assets' / 'ghosttrack.ico')
