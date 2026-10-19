"""Gera sprites.h (firmware) e icons/*.png + slimes.json (app) a partir de sprites_src.js.

Uso: python tools/gen_assets.py   (rodar da raiz do projeto)
"""
import colorsys
import json
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
NAMES = ['Pink', 'Cotton', 'Tabby', 'Rock', 'Phosphor', 'Honey', 'Batty', 'Boom', 'Puddle', 'Hunter',
         'Crystal', 'Angler', 'Rad', 'Fire', 'Quantum', 'Flutter', 'Tangle', 'Ringtail', 'Mosaic',
         'Dervish', 'Yolky', 'Saber', 'Quicksilver', 'Gold', 'Lucky', 'Glitch', 'Twinkle', 'Tarr']
TWINKLE = NAMES.index('Twinkle')
TRANSP = 0xF81F

# (bg_sat, panel_sat, accent_sat, text_sat, bg_l, panel_l, accent_l, text_l); hue vem do sprite
DEFAULT = (35, 32, 80, 70, 11, 20, 68, 93)
# nome -> (hue, sat/luz...) para estilos que a cor dominante do sprite não acerta
OVERRIDE = {
    'Tabby': (215, 6, 5, 8, 8, 11, 20, 66, 93),
    'Quicksilver': (210, 8, 8, 12, 10, 12, 22, 78, 95),
    'Lucky': (190, 10, 10, 25, 25, 14, 24, 88, 97),
}


def parse_source():
    js = (ROOT / 'tools' / 'sprites_src.js').read_text(encoding='utf8')
    palette = re.search(r"PL='([0-9a-f]+)'", js).group(1)
    alphabet = re.search(r"AL='([^']+)'", js).group(1)
    rows = re.findall(r"'(\d+\|[^']+)'", js)
    colors = {alphabet[i]: tuple(int(palette[i * 6 + j:i * 6 + j + 2], 16) for j in (0, 2, 4))
              for i in range(len(palette) // 6)}
    return colors, rows


def build_image(spec, colors):
    width, data = spec.split('|')
    lines = data.split(',')
    img = Image.new('RGBA', (int(width), len(lines)), (0, 0, 0, 0))
    for y, line in enumerate(lines):
        for x, ch in enumerate(line[:int(width)]):
            if ch in colors:
                img.putpixel((x, y), colors[ch] + (255,))
    return img


def add_outline(img):
    w, h = img.size
    out = Image.new('RGBA', (w + 2, h + 2), (0, 0, 0, 0))
    out.paste(img, (1, 1))
    src = out.copy()
    for y in range(h + 2):
        for x in range(w + 2):
            if src.getpixel((x, y))[3]:
                continue
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w + 2 and 0 <= ny < h + 2 and src.getpixel((nx, ny))[3]:
                    out.putpixel((x, y), (255, 255, 255, 255))
                    break
    return out


def dominant_hue(spec, colors):
    counts = {}
    for ch in spec.split('|')[1].replace(',', ''):
        if ch in colors:
            counts[ch] = counts.get(ch, 0) + 1
    best, best_score = 0.0, -1.0
    for ch, n in counts.items():
        r, g, b = (v / 255 for v in colors[ch])
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        score = n * (3 if s > .3 and .3 < l < .85 else 1) * s
        if score > best_score:
            best, best_score = h * 360, score
    return best


def hsl565(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
    return ((round(r * 31) << 11) | (round(g * 63) << 5) | round(b * 31)), '#%02x%02x%02x' % (
        round(r * 255), round(g * 255), round(b * 255))


def theme(name, hue):
    params = OVERRIDE.get(name)
    if params:
        hue, params = params[0], params[1:]
    sb, sp, sa, st, lb, lp, la, lt = params or DEFAULT
    return [hsl565(hue, s, l) for s, l in ((sb, lb), (sp, lp), (sa, la), (st, lt))]


def rgb565(px):
    if px[3] == 0:
        return TRANSP
    r, g, b = px[:3]
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)


def main():
    colors, specs = parse_source()
    assert len(specs) == len(NAMES), (len(specs), len(NAMES))
    (ROOT / 'pc' / 'icons').mkdir(parents=True, exist_ok=True)
    header = ['// Gerado por tools/gen_assets.py - não editar à mão.', '#pragma once', '#include <Arduino.h>',
              f'#define N_SLIMES {len(NAMES)}', f'#define TWINKLE_IDX {TWINKLE}', f'#define SPR_TRANSP 0x{TRANSP:04X}', '']
    themes, meta, sprite_names = [], [], []
    for i, (name, spec) in enumerate(zip(NAMES, specs)):
        img = add_outline(build_image(spec, colors))
        img.save(ROOT / 'pc' / 'icons' / f'{i:02d}.png')
        th = theme(name, dominant_hue(spec, colors))
        themes.append('  {' + ', '.join(f'0x{c[0]:04X}' for c in th) + '}')
        meta.append({'name': name, 'theme': [c[1] for c in th]})
        pixels = [rgb565(img.getpixel((x, y))) for y in range(img.height) for x in range(img.width)]
        header.append(f'const uint16_t SPR_{i}[] PROGMEM = {{' + ','.join(f'0x{p:04X}' for p in pixels) + '};')
        sprite_names.append((img.width, img.height))
    header += ['', 'const uint16_t* const SPR[N_SLIMES] = {' + ','.join(f'SPR_{i}' for i in range(len(NAMES))) + '};',
               'const uint8_t SPR_W[N_SLIMES] = {' + ','.join(str(w) for w, _ in sprite_names) + '};',
               'const uint8_t SPR_H[N_SLIMES] = {' + ','.join(str(h) for _, h in sprite_names) + '};',
               'const char* const SLIME_NAMES[N_SLIMES] = {' + ','.join(f'"{n.upper()}"' for n in NAMES) + '};',
               '// bg, panel, accent, text (RGB565)', 'const uint16_t THEMES[N_SLIMES][4] = {', ',\n'.join(themes), '};', '']
    (ROOT / 'firmware' / 'src' / 'sprites.h').write_text('\n'.join(header), encoding='utf8')
    (ROOT / 'pc' / 'slimes.json').write_text(json.dumps(meta, indent=1), encoding='utf8')
    print(f'{len(NAMES)} slimes -> firmware/src/sprites.h, pc/icons, pc/slimes.json')


if __name__ == '__main__':
    main()
