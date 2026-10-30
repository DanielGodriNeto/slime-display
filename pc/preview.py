"""Desenha o layout em 480x320 do mesmo jeito que a placa (fonte 5x7, botões, barra, equalizador)."""
import json
from pathlib import Path

from PIL import Image, ImageDraw

import font_data
import layout as lay

HERE = Path(__file__).parent
SLIMES = json.loads((HERE / 'slimes.json').read_text(encoding='utf8'))
IC_PREV = ["#.......#", "#......##", "#.....###", "#....####", "#...#####", "#....####", "#.....###", "#......##",
           "#.......#"]
IC_PLAY = ["##......", "####....", "######..", "########", "######..", "####....", "##......"]
IC_VOL = ["....#......", "...##..#...", "#####...#..", "#####.#.#..", "#####.#.#..", "#####.#.#..", "#####...#..",
          "...##..#...", "....#......"]
EQ_SAMPLE = [3, 5, 7, 4, 8, 6, 9, 5, 3, 6, 8, 4, 7, 9, 5, 3, 6, 8, 5, 4, 7, 6, 3, 5]
_icons = {}


def theme(slime, colors=None):
    """[fundo, painel, destaque, texto] do slime, com as cores globais por cima (se houver)."""
    k = list(SLIMES[max(0, min(slime, len(SLIMES) - 1))]['theme'])
    return with_colors(k, colors or {})


def with_colors(k, own):
    k = list(k)
    k[2], k[3] = own.get('accent') or k[2], own.get('main') or k[3]
    return k


def icon_image(n):
    if n not in _icons:
        _icons[n] = Image.open(HERE / 'icons' / f'{n:02d}.png').convert('RGBA')
    return _icons[n]


def mix(a, b, amount):
    """a misturado com b (amount 0-255), como a placa faz."""
    pa, pb = (tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in (a, b))
    return '#%02x%02x%02x' % tuple((x * (255 - amount) + y * amount) // 255 for x, y in zip(pa, pb))


def text(d, s, x, y, scale, color):
    px = 2 * scale
    for n, ch in enumerate(s):
        rows = font_data.GLYPHS.get(ch)
        if not rows or ch == ' ':
            continue
        for r, bits in enumerate(rows):
            for c in range(5):
                if bits >> (4 - c) & 1:
                    gx, gy = x + (n * 6 + c) * px, y + r * px
                    d.rectangle([gx, gy, gx + px - 1, gy + px - 1], fill=color)


def bitmap(d, rows, cx, cy, color, mirror=False):
    h, w = len(rows), len(rows[0])
    x0, y0 = (cx - w * 2) // 2 * 2, (cy - h * 2) // 2 * 2
    for y, row in enumerate(rows):
        for x, ch in enumerate(row[::-1] if mirror else row):
            if ch == '#':
                d.rectangle([x0 + x * 4, y0 + y * 4, x0 + x * 4 + 3, y0 + y * 4 + 3], fill=color)


def sprite(img, slime, ox, oy, scale):
    big = icon_image(slime).resize((lay.ICON * scale,) * 2, Image.NEAREST)
    img.paste(big, (ox, oy), big)


def rect(d, x, y, w, h, color):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=color)


def button(img, d, el, k, slime_name):
    x, w, h = el['x'], el['w'], el['h'] - 8
    y = el['y']
    rect(d, x, y + h, w, 6, mix(k[0], '#000000', 120))
    rect(d, x + 4, y, w - 8, h, k[2])
    rect(d, x, y + 4, w, h - 8, k[2])
    rect(d, x + 6, y + 4, w - 12, h - 8, k[1])
    rect(d, x + 4, y + 6, w - 8, h - 12, k[1])
    rect(d, x + 8, y + 6, w - 16, 2, mix(k[1], '#ffffff', 40))
    cx, cy = x + w // 2, y + h // 2
    if el['type'] == 'action':
        label = lay.model.ascii_label(lay.label_for(el, slime_name))[:max(0, (w - 10) // 12)]
        sc = max(1, (h - 12 - (16 if label else 0)) // lay.ICON)
        ox, oy = cx - lay.ICON * sc // 2, cy - (8 if label else 0) - lay.ICON * sc // 2
        if el['pixels']:
            for i, on in enumerate(lay.unpack_pixels(el['pixels'])):
                if on:
                    rect(d, ox + i % lay.ICON * sc, oy + i // lay.ICON * sc, sc, sc, k[2])
        else:
            sprite(img, el['slime'], ox, oy, sc)
        if label:
            text(d, label, cx - lay.text_width(len(label), 1) // 2, y + h - 18, 1, k[3])
    elif el['kind'] == 'prev':
        bitmap(d, IC_PREV, cx, cy, k[2])
    elif el['kind'] == 'next':
        bitmap(d, IC_PREV, cx, cy, k[2], True)
    elif el['kind'] == 'play':
        bitmap(d, IC_PLAY, cx, cy, k[2])
    else:
        bitmap(d, IC_VOL, cx, cy, k[2])


def equalizer(d, el, k):
    pitch = max(2, el['w'] // 24)
    bw, top = max(1, pitch * 3 // 4), el['h'] - 4
    for j, level in enumerate(EQ_SAMPLE):
        h = max(3, level * top // 9)
        color = k[2] if j % 2 else k[3]
        x, y = el['x'] + j * pitch, el['y'] + el['h'] - h
        rect(d, x, y, bw, h, color)
        rect(d, x, y, bw, 2, mix(color, '#ffffff', 60))


def progress(d, el, k):
    x, y, w = el['x'], el['y'], el['w']
    rect(d, x, y, w, 8, k[2])
    rect(d, x + 2, y + 2, w - 4, 4, k[1])
    rect(d, x + 2, y + 2, (w - 4) * 2 // 5 // 2 * 2, 4, k[2])
    text(d, '1:24', x, y + 14, 1, k[3])
    text(d, '-2:10', x + w - lay.text_width(5, 1), y + 14, 1, k[3])


def render(layout, slime, colors=None):
    """Imagem PIL 480x320 da tela, com dados de exemplo (música tocando)."""
    base = theme(slime, colors)
    k = base
    name = SLIMES[slime]['name'].upper()
    img = Image.new('RGBA', (lay.W, lay.H), k[0])
    d = ImageDraw.Draw(img)
    for el in layout:
        kind, s = el['type'], el['scale']
        k = with_colors(base, el)
        if kind == 'slime':
            sprite(img, slime, el['x'], el['y'] + 4, s)
        elif kind == 'title':
            text(d, 'MUSICA EXEMPLO', el['x'], el['y'] + 2, s, k[3])
        elif kind == 'artist':
            text(d, 'ARTISTA EXEMPLO', el['x'], el['y'], s, k[2])
        elif kind == 'eq':
            equalizer(d, el, k)
        elif kind == 'progress':
            progress(d, el, k)
        elif kind == 'clock':
            text(d, '21:45:30' if el['seconds'] else '21:45', el['x'], el['y'], s, k[3])
        elif kind == 'volume':
            text(d, lay.SAMPLE_VOLUME, el['x'], el['y'], s, k[2])
        elif kind == 'text':
            text(d, lay.model.ascii_label(lay.label_for(el, name)), el['x'], el['y'], s, k[2])
        else:
            button(img, d, el, k, name)
    return img
