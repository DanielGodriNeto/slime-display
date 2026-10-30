"""Envia uma foto para a placa: python photo_tool.py <vaga 0-7> <imagem> [COM5]  (feche o SlimeDisplay antes)."""
import sys
import time

import serial
from PIL import Image

W, H, CHUNK = 480, 320, 4096


def to_rgb565(path):
    """Corta a imagem para 480x320 (cover) e devolve RGB565 little-endian."""
    im = Image.open(path).convert('RGB')
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    l, t = (im.width - W) // 2, (im.height - H) // 2
    px = im.crop((l, t, l + W, t + H)).tobytes()
    out = bytearray()
    for i in range(0, len(px), 3):
        v = (px[i] & 0xF8) << 8 | (px[i + 1] & 0xFC) << 3 | px[i + 2] >> 3
        out += v.to_bytes(2, 'little')
    return bytes(out)


def wait(ser, want):
    line = ser.readline().strip()
    while line and line not in (b'A', b'OK', b'U ERR'):
        line = ser.readline().strip()
    if line != want and not (want == b'A' and line == b'OK'):
        raise RuntimeError(f'placa respondeu {line!r}')


def upload(slot, path, port):
    data = to_rgb565(path)
    with serial.Serial(port, 921600, timeout=5) as ser:
        time.sleep(2)
        ser.reset_input_buffer()
        ser.write(f'U {slot} {len(data)}\n'.encode())
        wait(ser, b'A')
        for i in range(0, len(data), CHUNK):
            ser.write(data[i:i + CHUNK])
            wait(ser, b'A')
    print('ok', slot, path)


if __name__ == '__main__':
    upload(int(sys.argv[1]), sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else 'COM5')
