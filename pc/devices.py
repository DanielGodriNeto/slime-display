"""Fontes de dados e porta serial do Slime Display (sem interface gráfica)."""
import asyncio
import ctypes
import datetime
import json
import math
import threading
import time
import unicodedata
import warnings
from pathlib import Path

import numpy as np
import serial
import serial.tools.list_ports

HERE = Path(__file__).resolve().parent
BAUD = 921600
NB = 24
VK = {'prev': 0xB1, 'play': 0xB3, 'next': 0xB0}
SLIMES = json.loads((HERE / 'slimes.json').read_text(encoding='utf8'))


# ---------- helpers puros ----------
def ascii_clean(text, limit):
    """Remove acentos e tudo que a fonte da placa não desenha; '|' e quebras viram espaço."""
    text = unicodedata.normalize('NFKD', text or '').encode('ascii', 'ignore').decode()
    return ' '.join(text.replace('|', ' ').split())[:limit]


def eq_digits(chunk, rate, state):
    """24 barras (0-9) em escala log de 60 Hz a 12 kHz, com ganho automático."""
    spec = np.abs(np.fft.rfft(chunk * np.hanning(len(chunk))))
    freqs = np.fft.rfftfreq(len(chunk), 1 / rate)
    edges = np.geomspace(60, 12000, NB + 1)
    vals = np.array([spec[(freqs >= lo) & (freqs < hi)].mean() if ((freqs >= lo) & (freqs < hi)).any() else 0.0
                     for lo, hi in zip(edges[:-1], edges[1:])])
    state['peak'] = max(state.get('peak', 1e-6) * 0.995, float(vals.max()), 1e-3)
    levels = np.clip(np.sqrt(vals / state['peak']), 0, 1)
    return ''.join(str(int(v * 9 + 0.5)) for v in levels)


def auto_brightness(now):
    """Brilho 60-255 que sobe e desce suave ao longo do dia: máximo às 13h, mínimo à 1h."""
    h = now.hour + now.minute / 60
    return round(60 + 195 * (0.5 + 0.5 * math.cos(2 * math.pi * (h - 13) / 24)))


def press_key(vk):
    user32 = ctypes.windll.user32
    user32.keybd_event(vk, 0, 0, 0)
    user32.keybd_event(vk, 0, 2, 0)


def load_config():
    try:
        return json.loads(CONFIG.read_text(encoding='utf8'))
    except (OSError, ValueError):
        return {}


def save_config(cfg):
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps(cfg), encoding='utf8')


# ---------- fontes de dados (threads) ----------
class Media:
    """Lê a sessão de mídia atual do Windows uma vez por segundo."""

    def __init__(self):
        self.state = {'playing': 0, 'pos': 0, 'dur': 0, 'title': '', 'artist': ''}
        threading.Thread(target=lambda: asyncio.run(self._loop()), daemon=True).start()

    async def _loop(self):
        from winrt.windows.media.control import (
            GlobalSystemMediaTransportControlsSessionManager as Manager,
            GlobalSystemMediaTransportControlsSessionPlaybackStatus as Status)
        mgr = await Manager.request_async()
        while True:
            try:
                self.state = await self._read(mgr, Status)
            except Exception:  # sessão sumiu no meio da leitura
                self.state = {'playing': 0, 'pos': 0, 'dur': 0, 'title': '', 'artist': ''}
            await asyncio.sleep(1)

    @staticmethod
    async def _read(mgr, Status):
        session = mgr.get_current_session()
        if session is None:
            return {'playing': 0, 'pos': 0, 'dur': 0, 'title': '', 'artist': ''}
        props = await session.try_get_media_properties_async()
        timeline = session.get_timeline_properties()
        playing = session.get_playback_info().playback_status == Status.PLAYING
        dur = max(0, int((timeline.end_time - timeline.start_time).total_seconds()))
        pos = (timeline.position - timeline.start_time).total_seconds()
        if playing:
            pos += (datetime.datetime.now(datetime.timezone.utc) - timeline.last_updated_time).total_seconds()
        return {'playing': int(playing), 'pos': int(max(0, min(pos, dur or pos))), 'dur': dur,
                'title': props.title, 'artist': props.artist}


class Equalizer:
    """Captura o áudio que sai nas caixas (loopback WASAPI) e mantém as 24 barras atuais."""

    def __init__(self):
        self.digits = '0' * NB
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        import soundcard as sc
        warnings.filterwarnings('ignore', module='soundcard')
        state = {}
        while True:
            try:
                mic = sc.get_microphone(str(sc.default_speaker().name), include_loopback=True)
                with mic.recorder(samplerate=44100, channels=2, blocksize=1024) as rec:
                    while True:
                        data = rec.record(numframes=1024)
                        self.digits = eq_digits(data.mean(axis=1), 44100, state)
            except Exception:  # troca de dispositivo de saída: tenta de novo
                self.digits = '0' * NB
                time.sleep(2)


def _com_endpoint(getter):
    """Endpoint de volume novo a cada chamada: o COM só vale na thread que o criou."""
    import comtypes
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import IAudioEndpointVolume
    comtypes.CoInitialize()
    iface = getter().Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return iface.QueryInterface(IAudioEndpointVolume)


def _speakers_device():
    from pycaw.pycaw import AudioUtilities
    return AudioUtilities.GetSpeakers()._dev


def _mic_device():
    from pycaw.pycaw import AudioUtilities
    return AudioUtilities.GetMicrophone()


class Volume:
    """Volume mestre do Windows em 0-10 e microfone mudo (pycaw)."""

    @staticmethod
    def get():
        try:
            return round(_com_endpoint(_speakers_device).GetMasterVolumeLevelScalar() * 10)
        except Exception:
            return 6

    def cycle(self):
        try:
            endpoint = _com_endpoint(_speakers_device)
            endpoint.SetMasterVolumeLevelScalar((round(endpoint.GetMasterVolumeLevelScalar() * 10) // 2 * 2 + 2) % 12 / 10, None)
        except Exception:
            pass

    @staticmethod
    def mic_muted():
        try:
            return bool(_com_endpoint(_mic_device).GetMute())
        except Exception:
            return False

    @staticmethod
    def toggle_mic():
        try:
            endpoint = _com_endpoint(_mic_device)
            endpoint.SetMute(0 if endpoint.GetMute() else 1, None)
        except Exception:
            pass


class Link:
    """Porta serial com reconexão; chama on_line para cada linha vinda da placa."""

    def __init__(self, on_line):
        self.on_line, self.port, self.ser, self.connected = on_line, None, None, False
        self._wlock = threading.Lock()
        threading.Thread(target=self._loop, daemon=True).start()

    @staticmethod
    def detect():
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            if p.vid == 0x1A86 or 'CH340' in (p.description or '') or 'USB-SERIAL' in (p.description or ''):
                return p.device
        return None

    def send(self, line):
        with self._wlock:
            self._write((line + '\n').encode('ascii', 'ignore'))

    def _write(self, data):
        try:
            if self.ser:
                self.ser.write(data)
                return True
        except (serial.SerialException, OSError):
            self._drop()
        return False

    def _drop(self):
        self.connected = False
        try:
            if self.ser:
                self.ser.close()
        finally:
            self.ser = None

    def _loop(self):
        while True:
            port = self.port or self.detect()
            if not port:
                time.sleep(2)
                continue
            try:
                self.ser = serial.Serial(port, BAUD, timeout=0.5)
                time.sleep(1.5)
                try:
                    self.ser.reset_input_buffer()
                except Exception:
                    pass
                self.connected = True
                self.on_line('HELLO')
                ser = self.ser
                while self.ser:
                    raw = ser.readline().decode('ascii', 'ignore').strip()
                    if raw:
                        self.on_line(raw)
            except (serial.SerialException, OSError):
                self._drop()
                time.sleep(2)

