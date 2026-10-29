"""Verificações rápidas: python test_deck.py (sem placa nem janela)."""
import json

import deck_actions as actions
import deck_model as model
import layout as lay
import preview


def test_hotkeys():
    assert actions.parse_hotkey('Ctrl+Shift+M') == [0x11, 0x10, 0x4D]
    assert actions.parse_hotkey('win+d') == [0x5B, 0x44] and actions.parse_hotkey('F5') == [0x74]
    for bad in ('', '+', 'ctrl+banana'):
        try:
            actions.parse_hotkey(bad)
        except ValueError:
            continue
        raise AssertionError(bad)


def test_urls():
    for ok in ('https://a.com', 'HTTP://a.com'):
        actions.open_url.__globals__['webbrowser'].open = lambda _u: None
        actions.open_url(ok)
    for bad in ('file:///c:/x', 'javascript:1', 'calc.exe', ''):
        try:
            actions.open_url(bad)
        except ValueError:
            continue
        raise AssertionError(bad)


def test_clean_garbage():
    for junk in (None, 5, [], 'x', {'layout': 'x'}, {'layout': [None, 3, {'type': 'zzz'}, {'type': 'slime', 'x': 'a'}]},
                 {'slime': 99, 'layout': [{'type': 'action', 'action': {'type': 'rm -rf'}, 'w': -5, 'h': 10 ** 9}]},
                 {'layout': [{'type': 'action', 'action': {'type': 'macro', 'steps': [1, {'type': 'wait', 'ms': 'a'}]}}]}):
        cfg = model.clean_config(junk)
        assert 0 <= cfg['slime'] < 28 and isinstance(cfg['layout'], list)
        for el in cfg['layout']:
            x, y, w, h = lay.box(el)
            assert 0 <= x and 0 <= y and x + w <= lay.W + 400 and el['action']['type'] in model.ACTION_TYPES
        json.dumps(cfg)


def test_layout_rules():
    many = [{'type': 'slime'}, {'type': 'slime'}, {'type': 'title'}, {'type': 'title'}, {'type': 'eq'}, {'type': 'eq'}]
    assert [e['type'] for e in lay.clean_layout(many)] == ['slime', 'title', 'eq']
    assert len(lay.clean_layout([{'type': 'text'}] * 100)) == lay.MAX_ELEMENTS
    eq = lay.clean_element({'type': 'eq', 'w': 480, 'h': 320})
    assert eq['w'] * eq['h'] <= 20000
    assert len(lay.clean_element({'type': 'text', 'label': 'x' * 99})['label']) == 24


def test_wire():
    lines = lay.wire(lay.default_layout(), 'PINK')
    assert lines[0] == 'L C' and lines[-1] == 'L D' and len(lines) == 14
    assert 'L A x 12 10 100 54 1 0 0 0 - PINK FM' in lines
    btn = lay.element('action', x=4, y=6, label='Álbum | Fotos', slime=3)
    assert lay.wire([btn], 'X')[1] == 'L A a 4 6 100 54 0 3 0 0 - ALBUM FOTOS'
    assert all(c in ' ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-:.#,!?/\'()&+' for c in model.ascii_label('Café "ñ" [z]'))


def test_colors_and_pixels():
    assert lay.clean_color('#ABCDEF') == '#abcdef' and lay.clean_color('red') == '' and lay.clean_color('#12345g') == ''
    assert lay.rgb565('#ffffff') == 0xFFFF and lay.rgb565('#000000') == 1 and lay.rgb565('') == 0
    assert model.clean_config({'colors': {'main': 5, 'accent': '#00ff00'}})['colors'] == {'main': '', 'accent': '#00ff00'}
    bits = [i % 3 == 0 for i in range(400)]
    assert lay.unpack_pixels(lay.pack_pixels(bits)) == bits and lay.clean_pixels('0' * 100) == ''
    assert lay.clean_pixels('zz') == '' and lay.clean_element({'type': 'media', 'pixels': 'f' * 100})['pixels'] == ''
    btn = lay.element('action', label='X', main='#ffffff', accent='#000000', pixels=lay.pack_pixels(bits))
    assert lay.wire([btn], 'S')[1] == f'L A a 0 0 100 54 0 0 65535 1 {btn["pixels"]} X'
    assert preview.render([btn], 0, {'main': '', 'accent': '#ff0000'}).size == (480, 320)


def test_free_spot_and_render():
    layout_ = []
    for kind in ('slime', 'artist', 'clock'):
        el = lay.element(kind)
        el['x'], el['y'] = lay.free_spot(layout_, el)
        layout_.append(el)
    boxes = [lay.box(e) for e in layout_]
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            assert not (a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3])
    for slime in (0, 27):
        assert preview.render(lay.default_layout(), slime).size == (480, 320)


def test_import_hostile():
    cur = model.default_config()
    prof = {'port': 'COM99', 'autostart': True, 'slime': 5,
            'layout': [{'type': 'action', 'label': 'Ok', 'action': {'type': 'launch', 'path': 'C:/x.exe', 'args': '-a'}},
                       {'type': 'action', 'label': 'Hack', 'action': {'type': 'power', 'cmd': 'shutdown'}}]}
    new, risky = model.import_profile(json.dumps(prof), cur)
    assert new['port'] == cur['port'] and new['autostart'] == cur['autostart'] and new['slime'] == 5
    assert len(risky) == 2 and 'x.exe' in risky[0] and 'shutdown' in risky[1]
    for bad in ('[]', '{}', 'nope', '{"layout": 3}'):
        try:
            new, _ = model.import_profile(bad, cur)
            assert bad == '{"layout": 3}' and new['layout'] == lay.default_layout()
        except ValueError:
            pass


def test_roundtrip():
    cfg = model.default_config()
    cfg['layout'].append(lay.clean_element(lay.element('action', label='A', action={'type': 'url', 'url': 'https://x.com'})))
    assert model.clean_config(json.loads(json.dumps(cfg))) == cfg
    new, _ = model.import_profile(model.export_profile(cfg), cfg)
    assert new['layout'] == cfg['layout']


def test_brightness():
    from datetime import datetime
    from devices import auto_brightness
    day, night = auto_brightness(datetime(2026, 1, 1, 13)), auto_brightness(datetime(2026, 1, 1, 1))
    assert day == 255 and night == 60
    step = max(abs(auto_brightness(datetime(2026, 1, 1, h, m)) - auto_brightness(datetime(2026, 1, 1, h, m - 1 if m else 59)))
               for h in range(1, 24) for m in range(1, 60))
    assert step <= 2  # nunca salta de uma vez


def test_brightness_config():
    c = model.clean_config
    base = model.default_config()
    assert [c({**base, 'brightness': v})['brightness'] for v in (0, 5, 100, 999, 'x', True)] == [0, 20, 100, 255, 0, 0]


if __name__ == '__main__':
    for name, fn in sorted(globals().items()):
        if name.startswith('test_'):
            fn()
            print('ok', name)
