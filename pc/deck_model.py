"""Configuração do app: slime, porta, layout da tela, ações dos botões, importar/exportar. Sem interface gráfica."""
import json
import os
import re
import unicodedata
from pathlib import Path

APPDATA = Path(os.environ.get('APPDATA', Path.home())) / 'slime-display'
CONFIG = APPDATA / 'deck.json'
OLD_CONFIG = APPDATA / 'config.json'

ACTION_TYPES = ('none', 'launch', 'url', 'folder', 'hotkey', 'text', 'macro', 'media', 'mic_mute', 'power')
STEP_TYPES = ('hotkey', 'text', 'wait', 'launch', 'url', 'media')
MEDIA_CMDS = ('play', 'next', 'prev', 'stop', 'vol_up', 'vol_down', 'mute')
POWER_CMDS = ('lock', 'sleep', 'restart', 'shutdown')
RISKY = ('launch', 'macro', 'power', 'text', 'hotkey', 'folder', 'url')
MAX_STR = 500
MAX_STEPS = 50


def ascii_label(text):
    """Sem acentos nem '|': o que a fonte da placa consegue desenhar."""
    import font_data
    text = unicodedata.normalize('NFKD', text or '').encode('ascii', 'ignore').decode().upper()
    text = ''.join(c if c == ' ' or c in font_data.CHARS else ' ' for c in text)
    return ' '.join(text.split())[:24]


# ---------- validação ----------
def _s(value, default=''):
    return value[:MAX_STR] if isinstance(value, str) else default


def _list(value, limit):
    return value[:limit] if isinstance(value, list) else []


def _int(value, default, low, high):
    try:
        return max(low, min(int(value), high))
    except (TypeError, ValueError):
        return default


def _step(raw):
    if not isinstance(raw, dict) or raw.get('type') not in STEP_TYPES:
        return None
    step = {'type': raw['type']}
    if raw['type'] == 'wait':
        step['ms'] = _int(raw.get('ms'), 500, 0, 60000)
    elif raw['type'] == 'media':
        step['cmd'] = raw.get('cmd') if raw.get('cmd') in MEDIA_CMDS else 'play'
    else:
        for key in ('keys', 'text', 'path', 'args', 'url'):
            if key in raw:
                step[key] = _s(raw[key])
    return step


def clean_action(raw):
    if not isinstance(raw, dict) or raw.get('type') not in ACTION_TYPES:
        return {'type': 'none'}
    kind = raw['type']
    action = {'type': kind}
    for key in ('path', 'args', 'url', 'keys', 'text'):
        if key in raw:
            action[key] = _s(raw[key])
    if kind == 'media':
        action['cmd'] = raw.get('cmd') if raw.get('cmd') in MEDIA_CMDS else 'play'
    if kind == 'power':
        action['cmd'] = raw.get('cmd') if raw.get('cmd') in POWER_CMDS else 'lock'
    if kind == 'text':
        action['enter'] = bool(raw.get('enter'))
    if kind == 'macro':
        steps = [_step(s) for s in _list(raw.get('steps'), MAX_STEPS)]
        action['steps'] = [s for s in steps if s]
    return action


def default_config():
    import layout
    return {'version': 2, 'slime': 0, 'port': 'auto', 'autostart': False, 'colors': layout.clean_colors(None), 'layout': layout.default_layout()}


def clean_config(raw):
    """Aceita qualquer JSON e devolve uma configuração válida (campos ruins viram padrão)."""
    import layout
    if not isinstance(raw, dict):
        return default_config()
    return {'version': 2,
            'slime': raw.get('slime') if isinstance(raw.get('slime'), int) and 0 <= raw['slime'] < 28 else 0,
            'port': _s(raw.get('port'), 'auto') or 'auto',
            'autostart': bool(raw.get('autostart')),
            'colors': layout.clean_colors(raw.get('colors')),
            'layout': layout.clean_layout(raw.get('layout'))}


# ---------- arquivo ----------
def load():
    try:
        return clean_config(json.loads(CONFIG.read_text(encoding='utf8')))
    except (OSError, ValueError, RecursionError):
        pass
    cfg = default_config()
    try:  # migra o config.json antigo (só slime e porta)
        old = json.loads(OLD_CONFIG.read_text(encoding='utf8'))
        cfg['slime'], cfg['port'] = old.get('slime', 0), old.get('port', 'auto')
    except (OSError, ValueError):
        pass
    return clean_config(cfg)


def save(cfg):
    APPDATA.mkdir(parents=True, exist_ok=True)
    tmp = CONFIG.with_suffix('.tmp')
    tmp.write_text(json.dumps(cfg, ensure_ascii=False, indent=1), encoding='utf8')
    tmp.replace(CONFIG)


# ---------- exportar / importar ----------
def export_profile(cfg):
    return json.dumps({'slime': cfg['slime'], 'colors': cfg['colors'], 'layout': cfg['layout']}, ensure_ascii=False, indent=1)


def import_profile(text, current):
    """Valida um perfil e devolve (config nova, ações a revisar). Não salva nada."""
    if len(text) > 4_000_000:
        raise ValueError('arquivo grande demais')
    raw = json.loads(text)
    if not isinstance(raw, dict) or 'layout' not in raw:
        raise ValueError('arquivo inválido')
    new = clean_config(raw)
    new['port'], new['autostart'] = current['port'], current['autostart']
    return new, risky_actions(new)


def describe(action):
    """Texto completo do que a ação faz (mostrado ao aprovar um perfil importado)."""
    kind = action['type']
    if kind == 'macro':
        return 'macro: ' + ' → '.join(_describe_step(s) for s in action.get('steps', []))
    if kind == 'text':
        return f'digitar "{action.get("text", "")}"' + (' + Enter' if action.get('enter') else '')
    return _describe_step(dict(action))


def _describe_step(step):
    kind = step['type']
    detail = {'launch': f'{step.get("path", "")} {step.get("args", "")}'.strip(), 'folder': step.get('path', ''),
              'url': step.get('url', ''), 'hotkey': step.get('keys', ''), 'text': f'"{step.get("text", "")}"',
              'power': step.get('cmd', ''), 'media': step.get('cmd', ''),
              'wait': f'{step.get("ms", 500)} ms'}.get(kind, '')
    return f'{kind} {detail}'.strip()


def risky_actions(cfg):
    """Lista legível das ações que mexem no PC, para o usuário aprovar ao importar."""
    return [re.sub(r'[\x00-\x1f\x7f]', '·', f'{el["label"] or "(sem nome)"} → {describe(el["action"])}')
            for el in cfg['layout'] if el['type'] == 'action' and el['action']['type'] in RISKY]
