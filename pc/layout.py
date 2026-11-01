"""A tela de música como uma lista de elementos (slime, título, botões...). Sem interface gráfica.

Cada elemento é um dict: type, x, y, w, h, scale, slime, label, kind (botão de mídia), action (botão de ação),
main/accent (cores próprias, '' = usa as da tela) e pixels (desenho 20x20 do botão de ação, '' = ícone de slime).
O mesmo layout é desenhado na prévia do editor (preview.py) e enviado à placa (wire).
"""
import copy

import deck_model as model
import vfont

W, H = 480, 320
MAX_ELEMENTS = 24
ICON = 20
MEDIA_KINDS = ('prev', 'play', 'next', 'vol')
SAMPLE_VOLUME = 'VOL ' + '#' * 6 + '-' * 4

# tipo -> (código da placa, nome, escala (min, max) ou None, tem largura/altura, único na tela)
TYPES = {
    'slime': ('s', 'Slime', (1, 5), '', True),
    'title': ('t', 'Nome da música', (1, 3), 'w', True),
    'artist': ('r', 'Artista', (1, 2), 'w', False),
    'eq': ('e', 'Equalizador', (1, 2), 'wh', True),  # escala 2 = barras largas (só foto)
    'progress': ('p', 'Tempo e barra', (1, 2), 'w', False),  # escala 2 = barra em 60 segmentos (só foto)
    'clock': ('c', 'Relógio', (1, 5), '', False),
    'volume': ('v', 'Volume', (1, 2), '', False),
    'text': ('x', 'Texto', (1, 3), '', False),
    'media': ('m', 'Botão de mídia', None, 'wh', False),
    'action': ('a', 'Botão de ação', None, 'wh', False),
}
UNIQUE = {'slime', 'title', 'eq'}  # a placa tem um buffer só para cada um


def element(type_, /, **fields):
    base = {'type': type_, 'x': 0, 'y': 0, 'w': 100, 'h': 54, 'scale': 1, 'slime': 0, 'label': '', 'kind': 'play',
            'action': {'type': 'none'}, 'main': '', 'accent': '', 'pixels': '', 'seconds': False, 'font': 0, 'dot': 0}
    base.update(fields)
    return base


def default_layout():
    return [
        element('slime', x=14, y=30, scale=3),
        element('title', x=106, y=40, w=360, scale=2),
        element('artist', x=106, y=78, w=360),
        element('eq', x=22, y=125, w=440, h=45),
        element('progress', x=14, y=184, w=452),
        element('text', x=12, y=10, label='{slime} FM'),
        element('clock', x=316, y=2, scale=2),
        element('media', x=14, y=220, w=97, kind='prev'),
        element('media', x=119, y=220, w=136, kind='play'),
        element('media', x=263, y=220, w=97, kind='next'),
        element('media', x=368, y=220, w=97, kind='vol'),
        element('volume', x=300, y=284),
    ]


PHOTO_SLOTS = 8
PHOTO_ACCENTS = ('#8fe3d0', '#37ffa0', '#ffe600', '#4dffd0')  # destaque de cada foto do template


def photo_layout(accent):
    """Template de foto: relógio pixel com segundos, nome, artista, linha de progresso com o tempo que falta e botões."""
    white = '#ffffff'
    keys = [element('media', x=50 + 100 * i, y=294, w=80, h=24, kind=k, accent=accent if k == 'play' else white)
            for i, k in enumerate(MEDIA_KINDS)]
    return [element('clock', x=97, y=52, scale=4, main=white, seconds=True),
            element('title', x=40, y=204, w=400, scale=2, main=white),
            element('artist', x=40, y=240, w=400, accent=white),
            element('progress', x=40, y=262, w=400, main=white, accent=accent)] + keys


def clean_color(value):
    """'#rrggbb' em minúsculas, ou '' (usar a cor padrão)."""
    ok = isinstance(value, str) and len(value) == 7 and value[0] == '#'
    try:
        return value.lower() if ok and int(value[1:], 16) >= 0 else ''
    except ValueError:
        return ''


def rgb565(color):
    """Cor da placa (RGB565); 0 quer dizer 'sem cor própria', então preto puro vira 1."""
    if not color:
        return 0
    r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    return ((r >> 3) << 11 | (g >> 2) << 5 | b >> 3) or 1


def clean_colors(raw):
    raw = raw if isinstance(raw, dict) else {}
    return {'main': clean_color(raw.get('main')), 'accent': clean_color(raw.get('accent'))}


def clean_pixels(value):
    """100 dígitos hexadecimais = 20x20 bits; qualquer outra coisa (ou tudo apagado) vira ''."""
    ok = isinstance(value, str) and len(value) == ICON * ICON // 4
    try:
        return value.lower() if ok and int(value, 16) else ''
    except ValueError:
        return ''


def pack_pixels(bits):
    return '%0*x' % (ICON * ICON // 4, int(''.join('1' if b else '0' for b in bits), 2))


def unpack_pixels(value):
    return [c == '1' for c in bin(int(value or '0', 16))[2:].zfill(ICON * ICON)]


def text_width(chars, scale):
    return chars * 12 * scale - 2 * scale if chars else 0


def label_for(el, slime_name):
    return el['label'].replace('{slime}', slime_name)


def vector_font(el):
    """Fonte vetorial de título ou artista: 'exo' (padrão) ou 'gara' (Garamond, os temas Death Note)."""
    if el['type'] == 'artist' and el['font'] == 2:
        return 'mich'
    return 'gara' if el['font'] == 1 else 'exo'


def vector_px(el):
    """Tamanho em px por escala: Exo 2 = 20; Garamond = 15 no título e 12 no artista (como o mockup)."""
    if el['font'] == 2:
        return (12 if el['type'] == 'artist' else 16) * el['scale']
    if not el['font']:
        return 20 * el['scale']
    return (15 if el['type'] == 'title' else 12) * el['scale']


def box(el, slime_name=''):
    """Retângulo (x, y, w, h) que o elemento ocupa na tela."""
    kind, s = el['type'], el['scale']
    if kind == 'slime':
        return el['x'], el['y'], ICON * s, ICON * s + 4
    if kind == 'title':  # caixa = altura das maiúsculas da fonte (ver vfont.py)
        return el['x'], el['y'], el['w'], vfont.cap(vector_font(el), vector_px(el)) + 4
    if kind == 'artist' and el['font']:
        return el['x'], el['y'], el['w'], vfont.cap(vector_font(el), vector_px(el)) + 4
    if kind == 'clock':  # Michroma: largura fixa de "00:00" e, se houver, dos segundos
        w = vfont.width('mich', 20 * s, '00:00')
        if el['seconds']:
            w += 8 + vfont.width('mich', 20 * max(1, s // 2), '00')
        return el['x'], el['y'], w, vfont.cap('mich', 20 * s)
    if kind == 'artist':
        return el['x'], el['y'], el['w'], 14 * s
    if kind == 'progress':
        return el['x'], el['y'], el['w'], 28
    if kind == 'volume':
        return el['x'], el['y'], text_width(len(SAMPLE_VOLUME), s), 14 * s
    if kind == 'text':
        return el['x'], el['y'], max(text_width(len(label_for(el, slime_name)), s), 12), 14 * s
    return el['x'], el['y'], el['w'], el['h']


# ---------- validação ----------
def _int(value, default, low, high):
    try:
        return max(low, min(int(value), high))
    except (TypeError, ValueError):
        return default


def clean_element(raw):
    if not isinstance(raw, dict) or raw.get('type') not in TYPES:
        return None
    kind = raw['type']
    _code, _name, scales, sized, _unique = TYPES[kind]
    el = element(kind)
    el['x'], el['y'] = _int(raw.get('x'), 0, 0, W - 4), _int(raw.get('y'), 0, 0, H - 4)
    low, high = scales or (1, 1)
    el['scale'] = _int(raw.get('scale'), low, low, high)
    el['w'] = _int(raw.get('w'), el['w'], 8, W - el['x']) if 'w' in sized else el['w']
    el['h'] = _int(raw.get('h'), el['h'], 20, H - el['y']) if 'h' in sized else el['h']
    if kind == 'eq':
        el['h'] = min(el['h'], 20000 // el['w'])
    el['slime'] = _int(raw.get('slime'), 0, 0, 27)
    el['label'] = raw['label'][:24] if isinstance(raw.get('label'), str) else ''
    el['kind'] = raw.get('kind') if raw.get('kind') in MEDIA_KINDS else 'play'
    el['action'] = model.clean_action(raw.get('action'))
    el['main'], el['accent'] = clean_color(raw.get('main')), clean_color(raw.get('accent'))
    el['pixels'] = clean_pixels(raw.get('pixels')) if kind == 'action' else ''
    el['seconds'] = kind == 'clock' and raw.get('seconds') is True
    el['font'] = _int(raw.get('font'), 0, 0, 2 if kind in ('clock', 'title', 'artist') else 1) if kind in ('title', 'artist', 'clock') else 0  # relógio: 2 = pixel + segundos em Michroma
    el['dot'] = _int(raw.get('dot'), 0, 0, 15) if kind == 'clock' and el['font'] else _int(raw.get('dot'), 0, 0, 16) if kind == 'eq' else 0  # relógio pixel: lado do ponto (0 = 2 px por escala); equalizador sobre foto: passo das barras (0 = padrão)
    return el


def clean_layout(raw):
    """Aceita qualquer JSON; descarta o que não é elemento e o que a placa recusaria (repetidos, excesso)."""
    if not isinstance(raw, list):
        return default_layout()
    out, seen = [], set()
    for item in raw:
        el = clean_element(item)
        if el is None or (el['type'] in UNIQUE and el['type'] in seen):
            continue
        seen.add(el['type'])
        out.append(el)
        if len(out) == MAX_ELEMENTS:
            break
    return out


# ---------- placa ----------
def wire(layout, slime_name):
    """Linhas que a placa entende (ver firmware/src/main.cpp)."""
    lines = ['L C']
    for i, el in enumerate(layout):
        code = TYPES[el['type']][0]
        a = {'media': MEDIA_KINDS.index(el['kind']), 'action': i}.get(el['type'], el['scale'])
        label = model.ascii_label(label_for(el, slime_name)) if el['type'] in ('text', 'action') else ''
        b = int(el['seconds']) | (el['font'] > 0) << 1 | el['dot'] << 2 | (el['font'] == 2) << 6 if el['type'] == 'clock' else el['font'] if el['type'] in ('title', 'artist') else el['dot'] if el['type'] == 'eq' else el['slime']
        colors = f'{rgb565(el["main"])} {rgb565(el["accent"])} {el["pixels"] or "-"}'
        lines.append(f'L A {code} {el["x"]} {el["y"]} {el["w"]} {el["h"]} {a} {b} {colors} {label}'.rstrip())
    return lines + ['L D']


def free_spot(layout, el, slime_name=''):
    """Posição que não cobre outro elemento (varre a tela de 20 em 20); sem espaço, empilha em cascata."""
    _, _, w, h = box(el, slime_name)
    taken = [box(o, slime_name) for o in layout]
    for y in range(0, H - h + 1, 20):
        for x in range(0, W - w + 1, 20):
            if not any(x < bx + bw and bx < x + w and y < by + bh and by < y + h for bx, by, bw, bh in taken):
                return x, y
    step = len(layout) * 12 % 120
    return step, step


def snapshot(layout):
    return copy.deepcopy(layout)
