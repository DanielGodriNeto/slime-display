"""Slime Display - app do Windows: música na placa (CYD) com a tela montada por você.

Abas: Slime (escolhe o tema), Tela (editor visual) e Ajustes (porta, início, perfil).
Uso: pc\\.venv\\Scripts\\python pc\\slime_display.py
"""
import ctypes
import datetime
import sys
import threading
import time
import tkinter as tk
import winreg
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import pystray
import serial.tools.list_ports
from PIL import Image, ImageTk

try:
    from tkinterdnd2 import TkinterDnD
except ImportError:
    TkinterDnD = None

import deck_actions as actions
import deck_model as model
import deck_ui as ui
import layout
import preview
import themes
from deck_service import ActionRunner
from deck_ui import ColorRow
from layout_editor import LayoutEditor
from devices import SLIMES, VK, auto_brightness, Equalizer, Link, Media, Volume, ascii_clean, press_key

HERE = Path(__file__).resolve().parent
RUN_KEY = r'Software\Microsoft\Windows\CurrentVersion\Run'
RUN_NAME = 'SlimeDisplay'


def autostart_command():
    if getattr(sys, 'frozen', False):  # versão .exe: o próprio executável
        return f'"{sys.executable}" --hidden'
    pyw = Path(sys.executable).with_name('pythonw.exe')
    return f'"{pyw if pyw.exists() else sys.executable}" "{Path(__file__).resolve()}" --hidden'


def set_autostart(on):
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
        if on:
            winreg.SetValueEx(key, RUN_NAME, 0, winreg.REG_SZ, autostart_command())
        else:
            try:
                winreg.DeleteValue(key, RUN_NAME)
            except FileNotFoundError:
                pass


class SlimeTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=12)
        self.app, self.icons, self.buttons = app, [], []
        grid = ttk.Frame(self)
        grid.pack()
        for i in range(len(SLIMES)):
            img = Image.open(HERE / 'icons' / f'{i:02d}.png')
            photo = ImageTk.PhotoImage(img.resize((img.width * 3, img.height * 3), Image.NEAREST))
            self.icons.append(photo)
            b = tk.Button(grid, image=photo, width=66, height=66, relief='flat', bd=3, bg=ui.THEME['panel'],
                          activebackground=ui.THEME['accent'], command=lambda n=i: app.choose_slime(n))
            b.grid(row=i // 7, column=i % 7, padx=2, pady=2)
            self.buttons.append(b)
        self.name = ttk.Label(self, style='Head.TLabel', padding=10)
        self.name.pack()
        ttk.Label(self, text='Tema da tela (fundo + layout)', style='Head.TLabel').pack(anchor='w')
        self.theme_box = ttk.Combobox(self, state='readonly', width=34,
                                      values=[f'{m.KEY}  {m.TITLE}' for m in themes.MODULES])
        self.theme_box.pack(anchor='w', pady=(2, 10))
        self.theme_box.bind('<<ComboboxSelected>>', lambda _e: app.choose_theme(self.theme_box.current()))
        box = ttk.Frame(self)
        box.pack(pady=(14, 0))
        ttk.Label(box, text='Cores da tela (valem para tudo; cada item pode ter a sua)', style='Head.TLabel').pack(anchor='w')
        self.rows = [ColorRow(box, text, app.cfg['colors'][key], '#ffffff', lambda v, k=key: app.set_color(k, v))
                     for key, text in (('main', 'Cor principal'), ('accent', 'Cor de destaque'))]
        for row in self.rows:
            row.pack(anchor='w', pady=3)
        self.show()

    def show(self):
        for i, b in enumerate(self.buttons):
            b.configure(bg=ui.THEME['accent'] if i == self.app.cfg['slime'] else ui.THEME['panel'])
        self.name.configure(text=f'{SLIMES[self.app.cfg["slime"]]["name"]} FM')
        active = [i for i, m in enumerate(themes.MODULES) if m.SLOT == self.app.cfg['photo']]
        if active:
            self.theme_box.current(active[0])
        else:
            self.theme_box.set('')
        k = preview.theme(self.app.cfg['slime'])  # o "padrão" de cada cor é a do slime escolhido
        for row, default in zip(self.rows, (k[3], k[2])):
            row.default = default
            row.paint()


class SettingsTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=16)
        self.app, cfg = app, app.cfg
        self.port = tk.StringVar(value=cfg['port'])
        self.auto = tk.BooleanVar(value=cfg['autostart'])
        self.auto_bright = tk.BooleanVar(value=cfg['brightness'] == 0)
        self.bright = tk.IntVar(value=cfg['brightness'] or 160)
        ttk.Label(self, text='Porta USB da placa', style='Head.TLabel').pack(anchor='w')
        row = ttk.Frame(self)
        row.pack(anchor='w', pady=6)
        self.port_box = ttk.Combobox(row, textvariable=self.port, width=12, state='readonly')
        self.port_box.pack(side='left')
        self.port_box.bind('<<ComboboxSelected>>', lambda _e: self.apply())
        ttk.Button(row, text='Atualizar lista', command=self.refresh_ports).pack(side='left', padx=8)
        self.refresh_ports()
        ttk.Checkbutton(self, text='Abrir junto com o Windows (fica na bandeja)', variable=self.auto,
                        command=self.apply).pack(anchor='w', pady=(14, 0))
        ttk.Label(self, text='Brilho da tela', style='Head.TLabel').pack(anchor='w', pady=(14, 4))
        ttk.Checkbutton(self, text='Automático (mais claro de dia, mais escuro de noite)', variable=self.auto_bright,
                        command=self.apply).pack(anchor='w')
        self.scale = ttk.Scale(self, from_=20, to=255, variable=self.bright, length=240, command=lambda _v: self.apply())
        self.scale.pack(anchor='w', pady=4)
        self.scale.state(['disabled'] if self.auto_bright.get() else ['!disabled'])
        ttk.Label(self, text='Perfil (backup e compartilhar)', style='Head.TLabel').pack(anchor='w', pady=(14, 4))
        bar = ttk.Frame(self)
        bar.pack(anchor='w')
        ttk.Button(bar, text='Exportar...', command=app.export_profile).pack(side='left')
        ttk.Button(bar, text='Importar...', command=app.import_profile).pack(side='left', padx=8)

    def refresh_ports(self):
        self.port_box['values'] = ['auto'] + [p.device for p in serial.tools.list_ports.comports()]

    def apply(self):
        self.scale.state(['disabled'] if self.auto_bright.get() else ['!disabled'])
        self.app.apply_settings(self.port.get(), self.auto.get(), 0 if self.auto_bright.get() else int(self.bright.get()))


class App:
    def __init__(self, root):
        self.root, self.cfg = root, model.load()
        self.media, self.eq, self.volume = Media(), Equalizer(), Volume()
        self.link = Link(self.on_line)
        self.link.port = None if self.cfg['port'] == 'auto' else self.cfg['port']
        self.runner = ActionRunner(lambda: self.cfg['layout'], self.volume, self.confirm, self.report)
        self.resync, self.last, self.vol, self.vol_at = True, {}, 6, 0.0
        self.tray, self.error = None, ('', 0.0)
        self._build()
        self.root.protocol('WM_DELETE_WINDOW', self.hide)
        self.start_tray()
        self.root.after(100, self.tick)

    def _build(self):
        self.root.title('Slime Display')
        ui.apply_theme(self.root)
        self.notes = ttk.Notebook(self.root)
        self.notes.pack(fill='both', expand=True, padx=8, pady=8)
        self.slime_tab = SlimeTab(self.notes, self)
        self.editor = LayoutEditor(self.notes, self)
        self.settings = SettingsTab(self.notes, self)
        for tab, text in ((self.slime_tab, 'Slime'), (self.editor, 'Tela'), (self.settings, 'Ajustes')):
            self.notes.add(tab, text=text)
        self.status = ttk.Label(self.root, text='procurando placa...', style='Muted.TLabel', padding=(10, 0, 10, 6))
        self.status.pack(anchor='w')
        self.root.update_idletasks()  # janela alta o bastante para o painel de propriedades
        height = min(self.root.winfo_screenheight() - 100, 900)
        self.root.geometry(f'{self.root.winfo_reqwidth()}x{max(height, self.root.winfo_reqheight())}')

    # ---------- janela e bandeja ----------
    def hide(self):
        if self.tray:
            self.root.withdraw()
        else:
            self.quit()

    def show(self):
        self.root.deiconify()
        self.root.lift()

    def quit(self):
        if self.tray:
            self.tray.stop()
        self.root.destroy()

    def start_tray(self):
        try:
            icon = Image.open(HERE / 'icons' / '00.png').convert('RGBA').resize((64, 64), Image.NEAREST)
            menu = pystray.Menu(pystray.MenuItem('Abrir', lambda: self.root.after(0, self.show), default=True),
                                pystray.MenuItem('Sair', lambda: self.root.after(0, self.quit)))
            self.tray = pystray.Icon('slime-display', icon, 'Slime Display', menu)
            self.tray.run_detached()
        except Exception:  # sem bandeja: fechar a janela encerra o app
            self.tray = None

    # ---------- ligações com o editor ----------
    def background(self, fn, *args):
        threading.Thread(target=fn, args=args, daemon=True).start()

    def commit(self):
        model.save(self.cfg)
        self.resync = True  # reenvia a tela para a placa no próximo ciclo

    def choose_theme(self, index):
        """Troca foto + layout pelo tema escolhido. A foto tem de estar na placa (ver pc/photo_tool.py)."""
        themes.apply_theme(self.cfg, themes.MODULES[index].KEY)
        self.editor.reload()
        self.slime_tab.show()
        self.commit()

    def run_action(self, el):
        """Botão "Experimentar" do editor."""
        problem = actions.validate(el['action'])
        if problem:
            messagebox.showinfo('Experimentar', problem, parent=self.root)
        elif el['action']['type'] != 'none':
            self.background(self.runner.run, el)

    def confirm(self, question):
        """Pergunta na janela (chamado fora da thread do Tk) e espera a resposta."""
        done, answer = threading.Event(), []

        def ask():
            self.show()
            answer.append(messagebox.askyesno('Slime Display', question, parent=self.root))
            done.set()
        self.root.after(0, ask)
        done.wait()
        return answer[0]

    def report(self, text):
        self.error = (text, time.monotonic())

    # ---------- ajustes, perfil ----------
    def choose_slime(self, n):
        self.cfg['slime'] = n
        model.save(self.cfg)
        self.slime_tab.show()
        self.editor.redraw()
        self.resync = True

    def set_color(self, key, value):
        self.cfg['colors'][key] = value
        self.editor.redraw()
        self.commit()

    def apply_settings(self, port, autostart, brightness):
        self.cfg.update(port=port, autostart=autostart, brightness=brightness)
        self.link.port = None if port == 'auto' else port
        try:
            set_autostart(autostart)
        except OSError as err:
            self.report(f'Não consegui mudar a inicialização com o Windows: {err}')
        model.save(self.cfg)

    def export_profile(self):
        path = filedialog.asksaveasfilename(parent=self.root, defaultextension='.json', initialfile='minha-tela.json',
                                            filetypes=[('Perfil do Slime Display', '*.json')])
        if path:
            Path(path).write_text(model.export_profile(self.cfg), encoding='utf8')

    def import_profile(self):
        path = filedialog.askopenfilename(parent=self.root, filetypes=[('Perfil do Slime Display', '*.json')])
        if not path:
            return
        try:
            new, risky = model.import_profile(Path(path).read_text(encoding='utf8'), self.cfg)
        except (OSError, ValueError, RecursionError):
            messagebox.showerror('Importar', 'Esse arquivo não é um perfil válido.', parent=self.root)
            return
        if risky and not ui.confirm_import(self.root, risky):
            return
        self.cfg.clear()
        self.cfg.update(new)
        self.editor.reload()
        self.editor.redraw()
        self.slime_tab.show()
        self.commit()

    # ---------- placa ----------
    def on_line(self, line):
        """Roda na thread da serial: nada que espere o OK da placa pode ficar aqui."""
        if 'HELLO' in line:
            self.last.clear()
            self.resync = True
        elif line.startswith('B a') and line[3:].isdigit():
            self.runner.on_press(int(line[3:]))
        elif line.startswith('B '):
            self.music_button(line[2:])

    def music_button(self, key):
        if key in VK:
            press_key(VK[key])
        elif key == 'vol':
            self.background(self.volume.cycle)

    def send_if_changed(self, key, line):
        if self.resync or self.last.get(key) != line:
            self.last[key] = line
            self.link.send(line)

    def refresh_volume(self):
        now = time.monotonic()
        if now - self.vol_at > 1:
            self.vol_at = now
            self.background(self._read_volume)

    def _read_volume(self):
        self.vol = self.volume.get()

    def tick(self):
        if self.link.connected:
            self.send_music()
        self.show_status()
        self.root.after(100, self.tick)

    def show_status(self):
        text, when = self.error
        if text and time.monotonic() - when < 8:
            self.status.configure(text=text)
        elif self.link.connected and self.link.ser:
            self.status.configure(text=f'conectado ({self.link.ser.port})')
        else:
            self.status.configure(text='procurando placa...')

    def send_music(self):
        m = self.media.state
        self.refresh_volume()
        names = SLIMES[self.cfg['slime']]['name'].upper()
        self.send_if_changed('L', '\n'.join(layout.wire(self.cfg['layout'], names)))
        c = self.cfg['colors']
        self.send_if_changed('K', f'K {layout.rgb565(c["main"])} {layout.rgb565(c["accent"])}')
        self.send_if_changed('S', f'S {self.cfg["slime"]}')
        self.send_if_changed('G', f'G {self.cfg["photo"]}')
        self.send_if_changed('V', f'V {self.vol}')
        self.send_if_changed('D', f'D {self.cfg["brightness"] or auto_brightness(datetime.datetime.now())}')
        self.send_if_changed('T', 'T ' + datetime.datetime.now().strftime('%H:%M:%S' if any(e['seconds'] for e in self.cfg['layout']) else '%H:%M'))
        self.link.send(f'N {m["playing"]}|{m["pos"]}|{m["dur"]}|{ascii_clean(m["title"], 120)}|{ascii_clean(m["artist"], 30)}')
        self.link.send('E ' + self.eq.digits)
        self.resync = False


def main():
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # texto nítido em telas de alta resolução
    root = TkinterDnD.Tk() if TkinterDnD else tk.Tk()
    app = App(root)
    if app.cfg['autostart']:  # renova o caminho se o app foi movido
        try:
            set_autostart(True)
        except OSError:
            pass
    if '--hidden' in sys.argv and app.tray:
        root.withdraw()
    root.mainloop()


if __name__ == '__main__':
    main()
