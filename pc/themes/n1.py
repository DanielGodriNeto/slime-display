"""Capa do caderno: moldura prata sobre preto; relógio, título, artista, progresso e botões vêm do firmware."""
from layout import MEDIA_KINDS, element

KEY, TITLE, SLOT = 'N1', 'Capa do caderno', 0
SILVER, RED, LIGHT, GREY, TRACK = '#cfcfcf', '#b3202a', '#d2d2d2', '#858585', '#555555'
EQ_ACC = '#cacaca'


def build():
    keys = [element('media', x=40 + 104 * i, y=225, w=94, h=31, kind=k, main='#484848', accent=SILVER)
            for i, k in enumerate(MEDIA_KINDS)]
    return [element('clock', x=86, y=84, scale=5, font=1, main=SILVER, accent=RED, seconds=True),
            element('title', x=40, y=171, w=400, scale=1, main=LIGHT, font=1),
            element('artist', x=40, y=192, w=400, main=GREY, font=1),
            element('progress', x=40, y=207, w=400, main=TRACK, accent=SILVER),
            element('eq', x=40, y=270, w=400, h=26, scale=2, main=GREY, accent=EQ_ACC)] + keys
