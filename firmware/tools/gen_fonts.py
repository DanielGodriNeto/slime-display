"""Gera src/fonts.h a partir das TTFs de tools/build (Michroma, Exo 2 Regular e EB Garamond Bold, só ASCII).

Uso: python tools/gen_fonts.py   (na pasta firmware; regere se trocar as fontes)
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'src' / 'fonts.h'
FONTS = (('FONT_MICH', 'Michroma-ascii.ttf'), ('FONT_EXO', 'Exo2-ascii.ttf'), ('FONT_GARA', 'EBGaramond-ascii.ttf'))


def array(name, data):
    rows = [', '.join(f'0x{b:02x}' for b in data[i:i + 16]) for i in range(0, len(data), 16)]
    return f'const uint32_t {name}_LEN = {len(data)};\nconst uint8_t {name}[] = {{\n  ' + ',\n  '.join(rows) + '\n};\n'


def main():
    parts = ['// Gerado por tools/gen_fonts.py: Michroma, Exo 2 Regular e EB Garamond Bold, só ASCII. Não editar à mão.',
             '#pragma once', '#include <Arduino.h>', '']
    for name, file in FONTS:
        parts.append(array(name, (HERE / 'build' / file).read_bytes()))
    OUT.write_text('\n'.join(parts), encoding='utf8')
    print('gravado', OUT)


if __name__ == '__main__':
    main()
