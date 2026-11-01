"""Arasaka vermelho: listras, faixa preta e trilho do progresso estão na foto (slot 5); o resto vem do firmware."""
from layout import MEDIA_KINDS, element

KEY, TITLE, SLOT = 'A2', 'Arasaka vermelho', 5
LIGHT, RED, BLACK, TRACK = '#f2f2f2', '#e01b24', '#0a0a0a', '#3a0407'


def build():
    keys = [element('media', x=24 + 110 * i, y=238, w=100, h=36, kind=k,
                    accent=RED if k == 'play' else LIGHT)
            for i, k in enumerate(MEDIA_KINDS)]
    return [element('clock', x=24, y=70, scale=5, font=2, dot=11, main=BLACK, accent=LIGHT, seconds=True),
            element('title', x=31, y=168, w=416, scale=1, main=LIGHT, font=2),
            element('artist', x=24, y=203, w=432, main=BLACK, accent=BLACK, font=2),
            element('progress', x=24, y=216, w=432, main=TRACK, accent=BLACK),
            element('eq', x=24, y=284, w=416, h=26, scale=2, main=BLACK, accent=BLACK, dot=8)] + keys
