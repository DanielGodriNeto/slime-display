"""Capa do caderno vermelha: moldura, cantos e textos fixos vêm do fundo (bg.png); relógio, título, artista, progresso e botões vêm do firmware."""
from layout import MEDIA_KINDS, element

KEY, TITLE, SLOT = 'N1b', 'Capa do caderno vermelha', 1
SAND, MUTED, GREY, RED, TRACK = '#cfcfcf', '#d8d8d8', '#8a8a8a', '#b3202a', '#7a7a7a'


def build():
    keys = [element('media', x=40 + 104 * i, y=225, w=94, h=31, kind=k, main='#484848',
                    accent=RED if k == 'play' else SAND)
            for i, k in enumerate(MEDIA_KINDS)]
    return [element('clock', x=35, y=90, scale=4, main=SAND, accent=RED, seconds=True),
            element('title', x=40, y=171, w=400, scale=1, main=MUTED, font=1),
            element('artist', x=40, y=192, w=400, main=GREY, accent=GREY, font=1),
            element('progress', x=40, y=207, w=400, main=TRACK, accent=RED),
            element('eq', x=40, y=270, w=400, h=26, scale=2, main=GREY, accent=RED)] + keys
