"""Executa as ações dos botões. Tudo roda sem shell; só ações vindas da configuração do usuário."""
import ctypes
import os
import re
import subprocess
import time
import webbrowser
from ctypes import wintypes
from pathlib import Path


user32 = ctypes.windll.user32
KEYUP, UNICODE = 0x0002, 0x0004
MEDIA_VK = {'play': 0xB3, 'next': 0xB0, 'prev': 0xB1, 'stop': 0xB2, 'vol_up': 0xAF, 'vol_down': 0xAE, 'mute': 0xAD}
NAMED_KEYS = {'ctrl': 0x11, 'control': 0x11, 'shift': 0x10, 'alt': 0x12, 'win': 0x5B, 'windows': 0x5B,
              'enter': 0x0D, 'esc': 0x1B, 'escape': 0x1B, 'tab': 0x09, 'space': 0x20, 'backspace': 0x08,
              'delete': 0x2E, 'del': 0x2E, 'insert': 0x2D, 'home': 0x24, 'end': 0x23, 'pageup': 0x21,
              'pagedown': 0x22, 'up': 0x26, 'down': 0x28, 'left': 0x25, 'right': 0x27, 'printscreen': 0x2C,
              'capslock': 0x14, 'menu': 0x5D}
PUNCT = {',': 0xBC, '.': 0xBE, '-': 0xBD, '=': 0xBB, ';': 0xBA, '/': 0xBF, '[': 0xDB, ']': 0xDD, '`': 0xC0}
URL_RE = re.compile(r'^https?://', re.I)


# ---------- teclado ----------
def key_code(name):
    name = name.strip().lower()
    if name in NAMED_KEYS:
        return NAMED_KEYS[name]
    if re.fullmatch(r'f([1-9]|1\d|2[0-4])', name):
        return 0x6F + int(name[1:])
    if len(name) == 1 and name.isalnum() and name.isascii():
        return ord(name.upper())
    if name in PUNCT:
        return PUNCT[name]
    raise ValueError(f'tecla desconhecida: {name!r}')


def parse_hotkey(text):
    """'ctrl+shift+m' -> [0x11, 0x10, 0x4D]; levanta ValueError se alguma tecla for desconhecida."""
    keys = [key_code(part) for part in text.split('+') if part.strip()]
    if not keys:
        raise ValueError('atalho vazio')
    return keys


def press_keys(codes):
    for code in codes:
        user32.keybd_event(code, 0, 0, 0)
    for code in reversed(codes):
        user32.keybd_event(code, 0, KEYUP, 0)


class _Key(ctypes.Structure):
    _fields_ = [('wVk', wintypes.WORD), ('wScan', wintypes.WORD), ('dwFlags', wintypes.DWORD),
                ('time', wintypes.DWORD), ('dwExtraInfo', ctypes.c_size_t)]


class _Union(ctypes.Union):
    _fields_ = [('ki', _Key), ('pad', ctypes.c_byte * 32)]


class _Input(ctypes.Structure):
    _fields_ = [('type', wintypes.DWORD), ('u', _Union)]


def _send_unit(vk, scan, flags):
    inp = _Input(1, _Union(ki=_Key(vk, scan, flags, 0, 0)))
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(_Input))


def type_text(text, enter=False):
    for ch in text.replace('\r', ''):
        if ch == '\n':
            press_keys([0x0D])
            continue
        units = ch.encode('utf-16-le')
        for i in range(0, len(units), 2):
            unit = int.from_bytes(units[i:i + 2], 'little')
            _send_unit(0, unit, UNICODE)
            _send_unit(0, unit, UNICODE | KEYUP)
        time.sleep(0.004)
    if enter:
        press_keys([0x0D])


# ---------- abrir coisas ----------
def launch(path, args=''):
    if not path or not os.path.exists(path):
        raise FileNotFoundError(f'não encontrei: {path}')
    if args.strip():
        subprocess.Popen([path] + _split_args(args), cwd=str(Path(path).parent))  # sem shell
    else:
        os.startfile(path)  # funciona para .exe, atalhos .lnk, scripts e documentos


def _split_args(args):
    import shlex
    return shlex.split(args, posix=False)


def open_url(url):
    if not URL_RE.match(url):
        raise ValueError('só links http:// ou https://')
    webbrowser.open(url)


def open_folder(path):
    if not os.path.isdir(path):
        raise FileNotFoundError(f'pasta não encontrada: {path}')
    os.startfile(path)


def power(cmd, confirm):
    if cmd == 'lock':
        user32.LockWorkStation()
        return
    labels = {'sleep': 'Suspender o computador?', 'restart': 'Reiniciar o computador?', 'shutdown': 'Desligar o computador?'}
    if cmd not in labels or not confirm(labels[cmd]):
        return
    if cmd == 'sleep':
        subprocess.Popen(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'])
    else:
        subprocess.Popen(['shutdown', '/r' if cmd == 'restart' else '/s', '/t', '15'])


# ---------- executor ----------
class Context:
    """O que o executor precisa do resto do app (microfone, confirmação)."""

    def __init__(self, confirm, volume):
        self.confirm, self.volume = confirm, volume


def run_step(step, ctx):
    kind = step['type']
    if kind == 'wait':
        time.sleep(step.get('ms', 500) / 1000)
    elif kind == 'hotkey':
        press_keys(parse_hotkey(step.get('keys', '')))
    elif kind == 'text':
        type_text(step.get('text', ''))
    elif kind == 'launch':
        launch(step.get('path', ''), step.get('args', ''))
    elif kind == 'url':
        open_url(step.get('url', ''))
    elif kind == 'media':
        press_keys([MEDIA_VK[step['cmd']]])


def run(action, ctx):
    """Executa uma ação; levanta exceção com mensagem legível se algo estiver errado."""
    kind = action['type']
    if kind == 'launch':
        launch(action.get('path', ''), action.get('args', ''))
    elif kind == 'url':
        open_url(action.get('url', ''))
    elif kind == 'folder':
        open_folder(action.get('path', ''))
    elif kind == 'hotkey':
        press_keys(parse_hotkey(action.get('keys', '')))
    elif kind == 'text':
        type_text(action.get('text', ''), action.get('enter', False))
    elif kind == 'macro':
        for step in action.get('steps', []):
            run_step(step, ctx)
    elif kind == 'media':
        press_keys([MEDIA_VK[action['cmd']]])
    elif kind == 'mic_mute':
        ctx.volume.toggle_mic()
    elif kind == 'power':
        power(action['cmd'], ctx.confirm)


def validate(action):
    """Texto de erro se a ação não pode rodar como está configurada, ou '' se está ok (usado no editor)."""
    kind = action['type']
    try:
        if kind == 'hotkey':
            parse_hotkey(action.get('keys', ''))
        elif kind == 'launch' and not os.path.exists(action.get('path', '')):
            return 'Escolha o programa ou arquivo a abrir.'
        elif kind == 'folder' and not os.path.isdir(action.get('path', '')):
            return 'Escolha a pasta.'
        elif kind == 'url' and not URL_RE.match(action.get('url', '')):
            return 'O link precisa começar com http:// ou https://'
        elif kind == 'macro':
            for step in action.get('steps', []):
                if step['type'] == 'hotkey':
                    parse_hotkey(step.get('keys', ''))
    except ValueError as err:
        return str(err)
    return ''

