"""Temas da tela. Cada módulo traz KEY, TITLE, SLOT (foto de fundo, -1 = sem foto) e build() (elementos do layout)."""
from . import classic, a1, a2, n1, n1b, n3, n4

MODULES = (classic, a1, a2, n1, n1b, n3, n4)
THEMES = {m.KEY: m for m in MODULES}


def apply_theme(cfg, key):
    """Põe no config a foto e o layout do tema escolhido."""
    theme = THEMES[key]
    cfg['photo'] = theme.SLOT
    cfg['layout'] = theme.build()
    return cfg
