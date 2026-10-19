"""Editor da tela: paleta de elementos à esquerda, a tela da placa no centro (arrastar), propriedades à direita."""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

import deck_actions as actions
import deck_model
import layout as lay
import preview
from deck_ui import ColorRow, ACTION_LABELS, FIELDS, MEDIA_LABELS, POWER_LABELS, THEME, MacroEditor, lookup

ZOOM = 1.5
HISTORY = 50
HANDLE = 14  # área de pegar para redimensionar, em pixels da tela da placa
KIND_LABELS = {'prev': 'Anterior', 'play': 'Play / Pause', 'next': 'Próxima', 'vol': 'Volume'}

# (nome na paleta, tipo, valores iniciais)
INFO = [('Slime', 'slime', {'scale': 3}), ('Nome da música', 'title', {'w': 300, 'scale': 2}),
        ('Artista', 'artist', {'w': 300}), ('Equalizador', 'eq', {'w': 300, 'h': 60}),
        ('Tempo e barra', 'progress', {'w': 300}), ('Relógio', 'clock', {'scale': 2}),
        ('Volume', 'volume', {}), ('Texto', 'text', {'label': 'TEXTO', 'scale': 2})]
MEDIA = [(KIND_LABELS[k], 'media', {'kind': k, 'w': 90, 'h': 54}) for k in lay.MEDIA_KINDS]
# (nome, slime do ícone, ação)
ACTION_PRESETS = [
    ('Programa', 14, {'type': 'launch', 'path': '', 'args': ''}),
    ('Site', 10, {'type': 'url', 'url': 'https://'}),
    ('Pasta', 9, {'type': 'folder', 'path': ''}),
    ('Atalho', 25, {'type': 'hotkey', 'keys': ''}),
    ('Digitar texto', 2, {'type': 'text', 'text': '', 'enter': False}),
    ('Mutar microfone', 6, {'type': 'mic_mute'}),
    ('Bloquear PC', 22, {'type': 'power', 'cmd': 'lock'}),
    ('Macro', 19, {'type': 'macro', 'steps': []}),
]


class IconPicker(tk.Toplevel):
    """Grade com os slimes; escolher já aplica."""

    def __init__(self, parent, on_pick):
        super().__init__(parent)
        self.title('Ícone do botão')
        self.configure(bg=THEME['bg'])
        self.transient(parent)
        self.photos = []
        grid = ttk.Frame(self, padding=10)
        grid.pack()
        for i in range(28):
            img = preview.icon_image(i).resize((60, 60), Image.NEAREST)
            self.photos.append(ImageTk.PhotoImage(img))
            tk.Button(grid, image=self.photos[-1], relief='flat', bg=THEME['panel'], activebackground=THEME['accent'],
                      command=lambda n=i: (on_pick(n), self.destroy())).grid(row=i // 7, column=i % 7, padx=2, pady=2)


class IconDrawer(tk.Toplevel):
    """Quadro 20x20 para desenhar o ícone do botão: clique ou arraste para pintar; clicar num ponto pintado apaga."""
    CELL = 16

    def __init__(self, parent, pixels, color, on_change):
        super().__init__(parent)
        self.title('Desenhar ícone')
        self.configure(bg=THEME['bg'])
        self.transient(parent)
        self.bits, self.on_change, self.color, self.paint_to = lay.unpack_pixels(pixels), on_change, color, True
        size = lay.ICON * self.CELL
        self.canvas = tk.Canvas(self, width=size, height=size, bg=THEME['field'], highlightthickness=0)
        self.canvas.pack(padx=12, pady=12)
        self.canvas.bind('<Button-1>', self.down)
        self.canvas.bind('<B1-Motion>', self.drag)
        bar = ttk.Frame(self)
        bar.pack(pady=(0, 6))
        ttk.Button(bar, text='Limpar', command=self.clear).pack(side='left', padx=4)
        ttk.Button(bar, text='Pronto', style='Accent.TButton', command=self.destroy).pack(side='left', padx=4)
        ttk.Label(self, style='Muted.TLabel', text='Apagar tudo volta ao ícone de slime.').pack(pady=(0, 10))
        self.show()

    def cell(self, event):
        x, y = event.x // self.CELL, event.y // self.CELL
        return y * lay.ICON + x if 0 <= x < lay.ICON and 0 <= y < lay.ICON else None

    def down(self, event):
        i = self.cell(event)
        if i is not None:
            self.paint_to = not self.bits[i]
            self.drag(event)

    def drag(self, event):
        i = self.cell(event)
        if i is not None and self.bits[i] != self.paint_to:
            self.bits[i] = self.paint_to
            self.show()

    def clear(self):
        self.bits = [False] * len(self.bits)
        self.show()

    def show(self):
        self.canvas.delete('all')
        c = self.CELL
        for i in range(lay.ICON * lay.ICON):
            x, y = i % lay.ICON * c, i // lay.ICON * c
            self.canvas.create_rectangle(x, y, x + c, y + c, fill=self.color if self.bits[i] else THEME['field'],
                                         outline=THEME['panel'])
        self.on_change(lay.pack_pixels(self.bits) if any(self.bits) else '')


class Props(ttk.Frame):
    """Painel da direita: mostra os campos do elemento selecionado."""

    def __init__(self, parent, editor):
        super().__init__(parent, style='Panel.TFrame', padding=12, width=270)
        self.editor, self.loading, self.vars, self.photo = editor, False, {}, None
        self.pack_propagate(False)
        self.head = ttk.Label(self, style='Head.TLabel', background=THEME['panel'])
        self.head.pack(anchor='w')
        self.body = ttk.Frame(self, style='Panel.TFrame')
        self.body.pack(fill='both', expand=True, pady=(8, 0))

    # ---------- montagem ----------
    def show(self, el):
        for child in self.body.winfo_children():
            child.destroy()
        self.vars = {}
        if el is None:
            self.head.configure(text='Nada selecionado')
            ttk.Label(self.body, style='Muted.TLabel', background=THEME['panel'], wraplength=240, justify='left',
                      text='Clique num item da tela para editar.\nPara ter outro item, escolha na lista da esquerda.\n'
                           'Para tirar, selecione e use "Remover item" (ou a tecla Delete).').pack(anchor='w')
            return
        self.loading = True
        kind = el['type']
        self.head.configure(text=lay.TYPES[kind][1])
        self._size_fields(el)
        if kind == 'media':
            self._combo('kind', 'Qual botão', [KIND_LABELS[k] for k in lay.MEDIA_KINDS], KIND_LABELS[el['kind']])
        if kind in ('text', 'action'):
            self._entry('label', 'Texto' + (' ({slime} = nome do slime)' if kind == 'text' else ''), el['label'])
        if kind == 'action':
            self._icon_row(el)
        if kind != 'slime':
            self._color_rows(el)
        if kind == 'action':
            self._action_part(el)
        self.loading = False

    def _size_fields(self, el):
        scales, sized = lay.TYPES[el['type']][2], lay.TYPES[el['type']][3]
        if scales:
            self._spin('scale', 'Tamanho', *scales, el['scale'])
        if 'w' in sized:
            self._spin('w', 'Largura', 8, lay.W, el['w'])
        if 'h' in sized:
            self._spin('h', 'Altura', 20, lay.H, el['h'])

    def _label(self, text):
        ttk.Label(self.body, text=text, style='Muted.TLabel', background=THEME['panel']).pack(anchor='w', pady=(6, 0))

    def _spin(self, key, label, low, high, value):
        self._label(label)
        var = tk.StringVar(value=str(value))
        box = ttk.Spinbox(self.body, from_=low, to=high, textvariable=var, width=8, command=self.on_change)
        box.pack(anchor='w')
        box.bind('<KeyRelease>', lambda _e: self.on_change())
        self.vars[key] = var

    def _entry(self, key, label, value):
        self._label(label)
        var = tk.StringVar(value=value)
        ttk.Entry(self.body, textvariable=var).pack(fill='x')
        var.trace_add('write', lambda *_a: self.on_change())
        self.vars[key] = var

    def _combo(self, key, label, values, value):
        self._label(label)
        var = tk.StringVar(value=value)
        box = ttk.Combobox(self.body, textvariable=var, values=values, state='readonly')
        box.pack(fill='x')
        box.bind('<<ComboboxSelected>>', lambda _e: self.on_change())
        self.vars[key] = var

    def _icon_row(self, el):
        self._label('Ícone')
        self.icon_btn = tk.Button(self.body, relief='flat', bg=THEME['field'], activebackground=THEME['accent'],
                                  command=self.pick_icon)
        self.icon_btn.pack(anchor='w')
        self.set_icon_image(el['slime'])
        ttk.Button(self.body, text='Desenhar o meu ícone...', command=self.draw_icon).pack(anchor='w', pady=(4, 0))

    def draw_icon(self):
        def apply(pixels):
            self.editor.selected()['pixels'] = pixels
            self.editor.after_edit()
        el = self.editor.selected()
        cfg = self.editor.app.cfg
        IconDrawer(self, el['pixels'], el['accent'] or preview.theme(cfg['slime'], cfg['colors'])[2], apply)

    def _color_rows(self, el):
        self._label('Cores deste item')
        cfg = self.editor.app.cfg
        k = preview.theme(cfg['slime'], cfg['colors'])
        for key, text, default in (('accent', 'Destaque', k[2]), ('main', 'Texto', k[3])):
            def apply(value, key=key):
                self.editor.selected()[key] = value
                self.editor.after_edit()
            ColorRow(self.body, text, el[key], default, apply, 'Panel.TFrame', 9).pack(anchor='w', pady=2)

    def set_icon_image(self, n):
        self.photo = ImageTk.PhotoImage(preview.icon_image(n).resize((40, 40), Image.NEAREST))
        self.icon_btn.configure(image=self.photo)

    def pick_icon(self):
        def apply(n):
            self.editor.selected()['slime'] = n
            self.set_icon_image(n)
            self.editor.after_edit()
        IconPicker(self, apply)

    # ---------- ação do botão ----------
    def _action_part(self, el):
        self._combo('atype', 'Ao tocar', [ACTION_LABELS[t] for t in deck_model.ACTION_TYPES], ACTION_LABELS[el['action']['type']])
        self.afields = ttk.Frame(self.body, style='Panel.TFrame')
        self.afields.pack(fill='x')
        self.avars = {}
        self.build_action_fields(el['action'])
        self.status = ttk.Label(self.body, style='Err.TLabel', background=THEME['panel'], wraplength=240)
        self.status.pack(anchor='w', pady=(4, 0))
        ttk.Button(self.body, text='Experimentar', command=lambda: self.editor.app.run_action(self.editor.selected())).pack(
            anchor='w', pady=(6, 0))
        self.show_problem(el['action'])

    def build_action_fields(self, action):
        for child in self.afields.winfo_children():
            child.destroy()
        self.avars = {}
        for key, ftype, label in FIELDS.get(action['type'], []):
            self._action_field(key, ftype, label, action)
        if action['type'] == 'macro':
            MacroEditor(self.afields, action, self.editor.after_edit).pack(fill='both', expand=True)

    def _action_field(self, key, ftype, label, action):
        raw = action.get(key, '')
        shown = {'media': MEDIA_LABELS.get(raw, MEDIA_LABELS['play']), 'power': POWER_LABELS.get(raw, POWER_LABELS['lock'])}.get(ftype, raw)
        var = tk.BooleanVar(value=bool(raw)) if ftype == 'check' else tk.StringVar(value=shown)
        self.avars[key] = (var, ftype)
        var.trace_add('write', lambda *_a: self.on_change())
        if ftype == 'check':
            ttk.Checkbutton(self.afields, text=label, variable=var).pack(anchor='w', pady=3)
            return
        ttk.Label(self.afields, text=label, style='Muted.TLabel', background=THEME['panel']).pack(anchor='w', pady=(6, 0))
        values = {'media': list(MEDIA_LABELS.values()), 'power': list(POWER_LABELS.values())}.get(ftype)
        if values:
            ttk.Combobox(self.afields, textvariable=var, state='readonly', values=values).pack(fill='x')
            return
        ttk.Entry(self.afields, textvariable=var).pack(fill='x')
        if ftype in ('file', 'dir'):
            ttk.Button(self.afields, text='Procurar...', command=lambda: self.browse(var, ftype)).pack(anchor='e', pady=2)

    def browse(self, var, ftype):
        if ftype == 'file':
            path = filedialog.askopenfilename(parent=self, title='Escolha o programa ou arquivo')
        else:
            path = filedialog.askdirectory(parent=self, title='Escolha a pasta')
        if path:
            var.set(path.replace('/', '\\'))

    def show_problem(self, action):
        self.status.configure(text=actions.validate(action))

    # ---------- edição ----------
    def on_change(self):
        if self.loading:
            return
        el = self.editor.selected()
        if el is None:
            return
        raw = dict(el)
        for key in ('scale', 'w', 'h'):
            if key in self.vars:
                raw[key] = self.vars[key].get()
        if 'label' in self.vars:
            raw['label'] = self.vars['label'].get()
        if 'kind' in self.vars:
            raw['kind'] = lookup(KIND_LABELS, self.vars['kind'].get(), 'play')
        if el['type'] == 'action':
            raw['action'] = self._read_action(el)
        el.update(lay.clean_element(raw))
        if el['type'] == 'action':
            self.show_problem(el['action'])
        self.editor.after_edit()

    @staticmethod
    def _stored(ftype, value):
        if ftype == 'media':
            return lookup(MEDIA_LABELS, value, 'play')
        if ftype == 'power':
            return lookup(POWER_LABELS, value, 'lock')
        return value

    def _read_action(self, el):
        kind = lookup(ACTION_LABELS, self.vars['atype'].get(), 'none')
        if kind != el['action']['type']:  # trocou o tipo: campos novos
            self.loading = True
            action = {'type': kind}
            self.build_action_fields(action)
            self.loading = False
            return action
        action = {'type': kind}
        if 'steps' in el['action']:
            action['steps'] = el['action']['steps']
        for key, (var, ftype) in self.avars.items():
            action[key] = self._stored(ftype, var.get())
        return action


class LayoutEditor(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=8)
        self.app, self.sel, self.drag, self.photo, self.save_job = app, None, None, None, None
        self.palette_buttons = {}
        self.reset_history()
        self._build_palette()
        self._build_center()
        self.props = Props(self, self)
        self.props.pack(side='right', fill='y', padx=(8, 0))
        self.props.show(None)
        top = self.winfo_toplevel()
        top.bind('<Control-z>', lambda _e: self.undo_step())
        top.bind('<Control-y>', lambda _e: self.redo_step())
        self.redraw()

    @property
    def layout(self):
        return self.app.cfg['layout']

    def selected(self):
        return self.layout[self.sel] if self.sel is not None and self.sel < len(self.layout) else None

    # ---------- montagem ----------
    def _build_palette(self):
        side = ttk.Frame(self, style='Panel.TFrame', padding=10)
        side.pack(side='left', fill='y', padx=(0, 8))
        for title, items in (('Informações', INFO), ('Botões de música', MEDIA), ('Botões que abrem coisas', None)):
            ttk.Label(side, text=title, style='Head.TLabel', background=THEME['panel']).pack(anchor='w', pady=(8, 4))
            grid = ttk.Frame(side, style='Panel.TFrame')
            grid.pack(anchor='w')
            entries = items or [(name, 'action', {'slime': icon, 'action': dict(act), 'label': name.upper(), 'w': 90, 'h': 70})
                                for name, icon, act in ACTION_PRESETS]
            for i, (name, kind, fields) in enumerate(entries):
                b = ttk.Button(grid, text=name, width=14, command=lambda k=kind, f=fields: self.add(k, f))
                b.grid(row=i // 2, column=i % 2, padx=2, pady=2)
                if kind in lay.UNIQUE:
                    self.palette_buttons[kind] = b

    def _build_center(self):
        center = ttk.Frame(self)
        center.pack(side='left', fill='both', expand=True)
        bar = ttk.Frame(center)
        bar.pack(fill='x', pady=(0, 6))
        for text, cmd in (('Desfazer', self.undo_step), ('Refazer', self.redo_step), ('Remover item', self.delete_selected),
                          ('Restaurar padrão', self.reset_layout)):
            ttk.Button(bar, text=text, command=cmd).pack(side='left', padx=(0, 6))
        w, h = int(lay.W * ZOOM), int(lay.H * ZOOM)
        self.canvas = tk.Canvas(center, width=w, height=h, bg='#000000', highlightthickness=1,
                                highlightbackground=THEME['hover'], takefocus=True)
        self.canvas.pack(anchor='w')
        self.canvas.create_image(0, 0, anchor='nw', tags='screen')
        self.canvas.bind('<Button-1>', self.on_down)
        self.canvas.bind('<B1-Motion>', self.on_move)
        self.canvas.bind('<ButtonRelease-1>', self.on_up)
        self.canvas.bind('<Double-Button-1>', self.on_double)
        self.canvas.bind('<Delete>', lambda _e: self.delete_selected())
        for key, (dx, dy) in {'Left': (-1, 0), 'Right': (1, 0), 'Up': (0, -1), 'Down': (0, 1)}.items():
            self.canvas.bind(f'<{key}>', lambda _e, d=(dx, dy): self.nudge(*d, 2))
            self.canvas.bind(f'<Shift-{key}>', lambda _e, d=(dx, dy): self.nudge(*d, 10))
        self.hint = ttk.Label(center, style='Muted.TLabel', text='Arraste para mover. O quadradinho no canto muda o tamanho.')
        self.hint.pack(anchor='w', pady=(6, 0))

    def say(self, text):
        self.hint.configure(text=text)

    # ---------- desenho ----------
    def redraw(self):
        """Redesenha a tela (também chamado pelo app quando o slime muda)."""
        img = preview.render(self.layout, self.app.cfg['slime'], self.app.cfg['colors']).convert('RGB')
        self.photo = ImageTk.PhotoImage(img.resize((int(lay.W * ZOOM), int(lay.H * ZOOM)), Image.NEAREST))
        self.canvas.itemconfigure('screen', image=self.photo)
        self.canvas.delete('sel')
        el = self.selected()
        if el:
            x, y, w, h = (round(v * ZOOM) for v in self.box(el))
            self.canvas.create_rectangle(x, y, x + w, y + h, outline=THEME['accent'], width=2, dash=(4, 3), tags='sel')
            if self.resizable(el):
                self.canvas.create_rectangle(x + w - 8, y + h - 8, x + w + 2, y + h + 2, fill=THEME['accent'], outline='white',
                                             tags='sel')
        for kind, button in self.palette_buttons.items():
            button.state(['disabled'] if any(e['type'] == kind for e in self.layout) else ['!disabled'])

    def box(self, el):
        return lay.box(el, preview.SLIMES[self.app.cfg['slime']]['name'].upper())

    @staticmethod
    def resizable(el):
        return bool(lay.TYPES[el['type']][3])

    # ---------- mouse e teclado ----------
    def on_down(self, event):
        self.canvas.focus_set()
        x, y = event.x / ZOOM, event.y / ZOOM
        el = self.selected()
        if el and self.resizable(el):
            bx, by, bw, bh = self.box(el)
            if bx + bw - HANDLE <= x <= bx + bw + 4 and by + bh - HANDLE <= y <= by + bh + 4:
                self.drag = ('resize', 0, 0, False)
                return
        hit = next((i for i in reversed(range(len(self.layout))) if self._inside(self.layout[i], x, y)), None)
        self.select(hit)
        if hit is not None:
            bx, by, _, _ = self.box(self.layout[hit])
            self.drag = ('move', x - bx, y - by, False)

    def on_double(self, _event):
        el = self.selected()
        if el and el['type'] == 'action':
            self.props.draw_icon()

    def _inside(self, el, x, y):
        bx, by, bw, bh = self.box(el)
        return bx <= x < bx + bw and by <= y < by + bh

    def on_move(self, event):
        el = self.selected()
        if not self.drag or el is None:
            return
        mode, ox, oy, _ = self.drag
        x, y = event.x / ZOOM, event.y / ZOOM
        if mode == 'move':
            _, _, bw, bh = self.box(el)
            el['x'] = max(0, min(round((x - ox) / 2) * 2, lay.W - bw))
            el['y'] = max(0, min(round((y - oy) / 2) * 2, lay.H - bh))
        else:
            raw = dict(el, w=round((x - el['x']) / 2) * 2, h=round((y - el['y']) / 2) * 2)
            el.update(lay.clean_element(raw))
        self.drag = (mode, ox, oy, True)
        self.redraw()

    def on_up(self, _event):
        moved = self.drag and self.drag[3]
        self.drag = None
        if moved:
            self.props.show(self.selected())
            self.changed()

    def nudge(self, dx, dy, step):
        el = self.selected()
        if el:
            _, _, bw, bh = self.box(el)
            el['x'] = max(0, min(el['x'] + dx * step, lay.W - bw))
            el['y'] = max(0, min(el['y'] + dy * step, lay.H - bh))
            self.after_edit()
        return 'break'

    def select(self, index):
        self.sel = index
        self.props.show(self.selected())
        self.redraw()

    # ---------- mudanças ----------
    def add(self, kind, fields):
        existing = next((i for i, e in enumerate(self.layout) if e['type'] == kind), None)
        if kind in lay.UNIQUE and existing is not None:
            self.select(existing)
            self.say('Esse item só pode aparecer uma vez; ele já está na tela.')
            return
        if len(self.layout) >= lay.MAX_ELEMENTS:
            self.say(f'A tela aguenta no máximo {lay.MAX_ELEMENTS} itens. Remova algum primeiro.')
            return
        el = lay.clean_element(lay.element(kind, **fields))
        el['x'], el['y'] = lay.free_spot(self.layout, el, preview.SLIMES[self.app.cfg['slime']]['name'].upper())
        self.layout.append(el)
        self.say('Arraste o item para onde quiser.')
        self.select(len(self.layout) - 1)
        self.changed()
        if el['type'] == 'action' and el['action']['type'] in ('launch', 'folder'):
            self.after(50, self.ask_path)

    def ask_path(self):
        el = self.selected()
        if not el:
            return
        if el['action']['type'] == 'launch':
            path = filedialog.askopenfilename(parent=self, title='Escolha o programa ou arquivo')
        else:
            path = filedialog.askdirectory(parent=self, title='Escolha a pasta')
        if path:
            el['action']['path'] = path.replace('/', '\\')
            self.props.show(el)
            self.after_edit()

    def delete_selected(self):
        if self.selected() is not None:
            del self.layout[self.sel]
            self.select(None)
            self.changed()

    def after_edit(self):
        self.redraw()
        self.changed()

    def reset_layout(self):
        if messagebox.askyesno('Restaurar padrão', 'Voltar a tela ao jeito original? Os botões que você criou serão apagados.',
                               parent=self):
            self.flush()
            self.restore(lay.default_layout(), 'Tela restaurada')

    # ---------- salvar e histórico ----------
    def changed(self):
        """Salva e manda para a placa pouco depois da última alteração."""
        if self.save_job:
            self.after_cancel(self.save_job)
        self.save_job = self.after(400, self._commit)

    def _commit(self):
        self.save_job = None
        now = lay.snapshot(self.layout)
        if now != self.base:
            self.undo.append(self.base)
            del self.undo[:-HISTORY]
            self.redo.clear()
            self.base = now
        self.app.commit()

    def flush(self):
        if self.save_job:
            self.after_cancel(self.save_job)
            self._commit()

    def reset_history(self):
        self.undo, self.redo, self.base = [], [], lay.snapshot(self.app.cfg['layout'])

    def undo_step(self):
        self.flush()
        if self.winfo_ismapped() and self.undo:
            self.redo.append(self.base)
            self.restore(self.undo.pop(), 'Desfeito')

    def redo_step(self):
        self.flush()
        if self.winfo_ismapped() and self.redo:
            self.undo.append(self.base)
            self.restore(self.redo.pop(), 'Refeito')

    def restore(self, snapshot, text):
        self.layout[:] = lay.snapshot(snapshot)
        if text == 'Tela restaurada':  # restaurar vira um passo que dá para desfazer
            self.undo.append(self.base)
            self.redo.clear()
        self.base = lay.snapshot(self.layout)
        self.select(None)
        self.app.commit()
        self.say(text)

    def reload(self):
        """Chamado depois de importar um perfil."""
        self.reset_history()
        self.select(None)
