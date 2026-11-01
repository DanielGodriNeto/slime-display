"""Texto vetorial igual ao da placa (firmware/src/main.cpp: vtext, vTextW, vAscent).

Usa as mesmas TTFs que vão embutidas na placa (firmware/tools/build). Glifo sem mistura de cor:
pixel fica cheio ou apagado (limiar de 50%), como o stb_truetype desenha na placa.
"""
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONTS = Path(__file__).resolve().parent.parent / 'firmware' / 'tools' / 'build'
FILES = {'mich': 'Michroma-ascii.ttf', 'exo': 'Exo2-ascii.ttf', 'gara': 'EBGaramond-ascii.ttf'}  # relógio, título, Death Note


@lru_cache(maxsize=None)
def font(name, px):
    return ImageFont.truetype(str(FONTS / FILES[name]), px)


def width(name, px, s):
    """Soma dos avanços arredondados por caractere, como a placa."""
    f = font(name, px)
    return sum(round(f.getlength(c)) for c in s)


def cap(name, px):
    """Altura das maiúsculas: o y do texto é o topo do 'H' (linha de base em y + cap)."""
    return -font(name, px).getbbox('H', anchor='ls')[1]


def draw(img, name, px, s, x, y, color, shadow=False):
    """Desenha s em img (RGBA). shadow = sombra preta deslocada px/20, como o texto sobre foto."""
    if shadow:
        draw(img, name, px, s, x + px // 20, y + px // 20, '#000000')
    mask = Image.new('L', img.size, 0)
    ImageDraw.Draw(mask).text((x, y + cap(name, px)), s, font=font(name, px), fill=255, anchor='ls')
    mask = mask.point(lambda v: 255 if v >= 128 else 0)
    img.paste(Image.new('RGBA', img.size, color), (0, 0), mask)
