"""Converte o PPM P6 do slime_host em PNG. Uso: python ppm2png.py entrada.ppm saida.png"""
import sys

from PIL import Image

Image.open(sys.argv[1]).convert("RGB").save(sys.argv[2])
