"""N3 (L real gigante): o L e o véu vêm do fundo (slot 2); relógio, título, artista, progresso e botões vêm do firmware."""
from layout import MEDIA_KINDS, element

KEY, TITLE, SLOT = 'N3', 'L', 2
WHITE, GREY, SECONDS, TRACK, OUTLINE = '#ffffff', '#8a8a8a', '#7a7a7a', '#333333', '#454545'


def build():
    keys = [element('media', x=25 + 66 * i, y=228, w=60, h=32, kind=k, main=OUTLINE, accent=WHITE)
            for i, k in enumerate(MEDIA_KINDS)]
    return [element('clock', x=26, y=40, scale=4, font=1, dot=9, main=WHITE, accent=SECONDS, seconds=True),
            element('title', x=28, y=174, w=258, scale=1, main=WHITE, font=1),
            element('artist', x=25, y=194, w=260, main=GREY, font=1),
            element('progress', x=26, y=209, w=260, h=8, main=TRACK, accent=WHITE),
            element('eq', x=26, y=270, w=260, h=30, scale=2, main=WHITE, accent=WHITE)] + keys
