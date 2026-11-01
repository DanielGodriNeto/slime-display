"""Arasaka terminal: moldura e logo estão na foto (slot 4); relógio, título, artista, progresso e botões vêm do firmware."""
from layout import MEDIA_KINDS, element

KEY, TITLE, SLOT = 'A1', 'Arasaka terminal', 4
LIGHT, RED, DIM = '#f2f2f2', '#e01b24', '#9a4a4e'


def build():
    keys = [element('media', x=70 + 98 * i, y=231, w=88, h=24, kind=k, accent=LIGHT)
            for i, k in enumerate(MEDIA_KINDS)]
    return [element('clock', x=70, y=72, scale=5, font=2, dot=11, main=LIGHT, accent=RED, seconds=True),
            element('title', x=70, y=170, w=386, scale=1, main=LIGHT, font=2),
            element('artist', x=70, y=190, w=386, scale=1, main='#d0d0d0', accent=RED, font=2),
            element('progress', x=70, y=211, w=386, scale=2, main=DIM, accent=RED),
            element('eq', x=70, y=274, w=360, h=32, main=RED, accent=RED, dot=6)] + keys
