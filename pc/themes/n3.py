"""N3 (L real gigante): o L e o véu vêm do fundo (slot 2); relógio, título, artista, progresso e botões vêm do firmware."""
from layout import MEDIA_KINDS, element

KEY, TITLE, SLOT = 'N3', 'L', 2
WHITE, GREY, SECONDS, TRACK, OUTLINE = '#ffffff', '#8a8a8a', '#7a7a7a', '#333333', '#454545'


def build():
    keys = [element('media', x=25 + 72 * i, y=226, w=68, h=40, kind=k, main=OUTLINE, accent=WHITE)
            for i, k in enumerate(MEDIA_KINDS)]
    return [element('clock', x=26, y=40, scale=4, main=WHITE, accent=SECONDS, seconds=True),
            element('title', x=26, y=166, w=262, scale=1, main=WHITE),
            element('artist', x=26, y=190, w=262, main=GREY, font=2),
            element('progress', x=26, y=209, w=260, h=8, main=TRACK, accent=WHITE),
            element('eq', x=26, y=274, w=260, h=26, scale=2, main=WHITE, accent=WHITE)] + keys
