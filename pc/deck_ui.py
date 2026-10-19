"""Tema, textos e janelas auxiliares do editor do deck (macros, confirmação de importação)."""
import tkinter as tk
from tkinter import colorchooser, filedialog, simpledialog, ttk

THEME = {'bg': '#16171c', 'panel': '#1e2027', 'field': '#262932', 'hover': '#31343f', 'select': '#363a48',
         'fg': '#e8e9ee', 'muted': '#8a8e9c', 'accent': '#4f8cff', 'danger': '#f87171'}
ACTION_LABELS = {'none': 'Nada', 'launch': 'Abrir programa ou arquivo', 'url': 'Abrir site', 'folder': 'Abrir pasta',
                 'hotkey': 'Atalho de teclado', 'text': 'Digitar texto', 'macro': 'Macro (vários passos)',
                 'media': 'Mídia e volume', 'mic_mute': 'Mutar microfone', 'power': 'Energia do PC'}
MEDIA_LABELS = {'play': 'Play / Pause', 'next': 'Próxima', 'prev': 'Anterior', 'stop': 'Parar',
                'vol_up': 'Volume +', 'vol_down': 'Volume -', 'mute': 'Mudo'}
POWER_LABELS = {'lock': 'Bloquear', 'sleep': 'Suspender', 'restart': 'Reiniciar', 'shutdown': 'Desligar'}
STEP_LABELS = {'hotkey': 'Atalho', 'text': 'Texto', 'wait': 'Esperar', 'launch': 'Programa', 'url': 'Site',
               'media': 'Mídia'}
FIELDS = {'launch': [('path', 'file', 'Programa ou arquivo'), ('args', 'text', 'Argumentos (opcional)')],
          'url': [('url', 'text', 'Endereço (https://...)')],
          'folder': [('path', 'dir', 'Pasta')],
          'hotkey': [('keys', 'text', 'Atalho, ex.: ctrl+shift+m')],
          'text': [('text', 'text', 'Texto a digitar'), ('enter', 'check', 'Apertar Enter no fim')],
          'media': [('cmd', 'media', 'Comando')],
          'power': [('cmd', 'power', 'O que fazer')]}


def apply_theme(root):
    t = THEME
    root.configure(bg=t['bg'])
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('.', background=t['bg'], foreground=t['fg'], fieldbackground=t['field'], bordercolor=t['panel'],
                    lightcolor=t['panel'], darkcolor=t['panel'], font=('Segoe UI', 10))
    style.configure('Panel.TFrame', background=t['panel'])
    style.configure('TLabel', background=t['bg'], foreground=t['fg'])
    style.configure('Panel.TLabel', background=t['panel'])
    style.configure('Muted.TLabel', foreground=t['muted'])
    style.configure('Err.TLabel', foreground=t['danger'])
    style.configure('Head.TLabel', font=('Segoe UI Semibold', 11))
    style.configure('TButton', background=t['field'], padding=(10, 5), borderwidth=0)
    style.map('TButton', background=[('active', t['hover'])])
    style.configure('Accent.TButton', background=t['accent'], foreground='#ffffff')
    style.map('Accent.TButton', background=[('active', '#3b78e8')])
    style.configure('TNotebook', background=t['bg'], borderwidth=0)
    style.configure('TNotebook.Tab', background=t['bg'], foreground=t['muted'], padding=(18, 8), borderwidth=0)
    style.map('TNotebook.Tab', background=[('selected', t['panel'])], foreground=[('selected', '#ffffff')])
    for name in ('TCheckbutton', 'TRadiobutton'):
        style.configure(name, background=t['bg'])
    style.map('TCombobox', fieldbackground=[('readonly', t['field'])], foreground=[('readonly', t['fg'])])
    root.option_add('*TCombobox*Listbox.background', t['field'])
    root.option_add('*TCombobox*Listbox.foreground', t['fg'])


def lookup(labels, text, default=''):
    return next((k for k, v in labels.items() if v == text), default)

class ColorRow(ttk.Frame):
    """Nome + amostra (clique para escolher a cor) + 'Padrão'. value '' = cor padrão; on_set recebe '#rrggbb' ou ''."""

    def __init__(self, parent, label, value, default, on_set, style='TFrame', label_width=18):
        super().__init__(parent, style=style)
        self.value, self.default, self.on_set = value, default, on_set
        name = ttk.Label(self, text=label, width=label_width, style='Muted.TLabel')
        if style == 'Panel.TFrame':
            name.configure(background=THEME['panel'])
        name.pack(side='left')
        self.swatch = tk.Button(self, width=4, relief='flat', command=self.pick)
        self.swatch.pack(side='left', padx=6)
        ttk.Button(self, text='Padrão', padding=(6, 2), command=lambda: self.set('')).pack(side='left')
        self.paint()

    def paint(self):
        color = self.value or self.default
        self.swatch.configure(bg=color, activebackground=color)

    def set(self, value):
        self.value = value
        self.paint()
        self.on_set(value)

    def pick(self):
        _rgb, hexa = colorchooser.askcolor(self.value or self.default, parent=self, title='Escolha a cor')
        if hexa:
            self.set(hexa.lower())


class MacroEditor(ttk.Frame):
    """Lista de passos de uma macro com botões para adicionar, editar, mover e remover."""

    def __init__(self, parent, action, on_change):
        super().__init__(parent, style='Panel.TFrame')
        self.steps, self.on_change = action.setdefault('steps', []), on_change
        self.list = tk.Listbox(self, height=7, bg=THEME['field'], fg=THEME['fg'], selectbackground=THEME['accent'],
                               highlightthickness=0, bd=0, exportselection=False)
        self.list.pack(fill='both', expand=True)
        self.list.bind('<Double-Button-1>', lambda _e: self.edit())
        bar = ttk.Frame(self, style='Panel.TFrame')
        bar.pack(fill='x', pady=(6, 0))
        for kind in ('hotkey', 'text', 'wait', 'launch', 'url', 'media'):
            ttk.Button(bar, text='+ ' + STEP_LABELS[kind], command=lambda k=kind: self.add(k)).pack(side='left', padx=(0, 4))
        bar2 = ttk.Frame(self, style='Panel.TFrame')
        bar2.pack(fill='x', pady=(4, 0))
        for text, cmd in (('Editar', self.edit), ('Subir', lambda: self.move(-1)), ('Descer', lambda: self.move(1)),
                          ('Remover', self.remove)):
            ttk.Button(bar2, text=text, command=cmd).pack(side='left', padx=(0, 4))
        self.fill()

    def fill(self, select=None):
        self.list.delete(0, 'end')
        for step in self.steps:
            self.list.insert('end', f'{STEP_LABELS[step["type"]]}: {self.summary(step)}')
        if select is not None and self.steps:
            self.list.selection_set(max(0, min(select, len(self.steps) - 1)))

    @staticmethod
    def summary(step):
        if step['type'] == 'wait':
            return f'{step.get("ms", 500)} ms'
        if step['type'] == 'media':
            return MEDIA_LABELS[step['cmd']]
        return step.get('keys') or step.get('text') or step.get('path') or step.get('url') or ''

    def ask(self, kind, current=None):
        current = current or {}
        if kind == 'wait':
            ms = simpledialog.askinteger('Esperar', 'Quantos milissegundos?', initialvalue=current.get('ms', 500),
                                         minvalue=0, maxvalue=60000, parent=self)
            return None if ms is None else {'type': 'wait', 'ms': ms}
        if kind == 'media':
            pick = simpledialog.askstring('Mídia', 'Comando: ' + ', '.join(MEDIA_LABELS.values()),
                                          initialvalue=MEDIA_LABELS.get(current.get('cmd'), 'Play / Pause'), parent=self)
            return {'type': 'media', 'cmd': lookup(MEDIA_LABELS, pick, 'play')} if pick else None
        if kind == 'launch':
            path = filedialog.askopenfilename(parent=self, title='Programa ou arquivo')
            return {'type': 'launch', 'path': path.replace('/', '\\'), 'args': current.get('args', '')} if path else None
        prompt = {'hotkey': 'Atalho (ex.: ctrl+c):', 'text': 'Texto a digitar:', 'url': 'Endereço (https://...):'}[kind]
        key = {'hotkey': 'keys', 'text': 'text', 'url': 'url'}[kind]
        value = simpledialog.askstring(STEP_LABELS[kind], prompt, initialvalue=current.get(key, ''), parent=self)
        return {'type': kind, key: value} if value else None

    def add(self, kind):
        step = self.ask(kind)
        if step:
            self.steps.append(step)
            self.fill(len(self.steps) - 1)
            self.on_change()

    def edit(self):
        sel = self.list.curselection()
        if sel and (step := self.ask(self.steps[sel[0]]['type'], self.steps[sel[0]])):
            self.steps[sel[0]] = step
            self.fill(sel[0])
            self.on_change()

    def move(self, delta):
        sel = self.list.curselection()
        if sel and 0 <= sel[0] + delta < len(self.steps):
            i = sel[0]
            self.steps[i], self.steps[i + delta] = self.steps[i + delta], self.steps[i]
            self.fill(i + delta)
            self.on_change()

    def remove(self):
        sel = self.list.curselection()
        if sel:
            del self.steps[sel[0]]
            self.fill(sel[0])
            self.on_change()


def confirm_import(parent, lines):
    """Mostra TODAS as ações do perfil (com rolagem) e devolve True se o usuário aceitar."""
    win = tk.Toplevel(parent)
    win.title('Importar perfil')
    win.configure(bg=THEME['bg'])
    win.transient(parent)
    ttk.Label(win, text='Este perfil tem botões que mexem no seu PC. Só importe de quem você confia.',
              wraplength=520).pack(padx=14, pady=(14, 6))
    box = tk.Text(win, width=70, height=14, wrap='word', bg=THEME['field'], fg=THEME['fg'], bd=0)
    box.insert('1.0', '\n\n'.join(lines))
    box.configure(state='disabled')
    box.pack(padx=14, fill='both', expand=True)
    answer = []
    bar = ttk.Frame(win)
    bar.pack(pady=12)
    ttk.Button(bar, text='Importar', style='Accent.TButton', command=lambda: (answer.append(1), win.destroy())).pack(side='left', padx=6)
    ttk.Button(bar, text='Cancelar', command=win.destroy).pack(side='left')
    win.grab_set()
    win.wait_window()
    return bool(answer)
