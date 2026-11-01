"""Light / Kira: fundo com moldura, kanji e 'KIRA' vem da foto (slot 3); relógio, título, artista, progresso e botões vêm do firmware."""
from layout import MEDIA_KINDS, element

KEY, TITLE, SLOT = 'N4', 'Light / Kira', 3
CREAM, RED, DIM, MUTED, TRACK = '#efe3cf', '#c0261f', '#8a6a58', '#9a8a78', '#2a1612'


def build():
    keys = [element('media', x=27 + 106 * i, y=227, w=100, h=34, kind=k, main='#6a5648',
                    accent=RED if k == 'play' else CREAM)
            for i, k in enumerate(MEDIA_KINDS)]
    return [element('clock', x=28, y=70, scale=5, font=1, dot=11, main=CREAM, accent=RED, seconds=True),
            element('title', x=28, y=171, w=424, scale=1, main=CREAM, font=1),
            element('artist', x=28, y=192, w=424, main=MUTED, font=1),
            element('progress', x=28, y=207, w=424, main=TRACK, accent=RED),
            element('eq', x=28, y=272, w=360, h=28, scale=2, main=MUTED, accent=RED)] + keys
