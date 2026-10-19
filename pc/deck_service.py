"""Roda a ação do botão tocado na placa (B a<n>), sem travar a leitura serial."""
import threading
import time

import deck_actions as actions

PRESS_DEBOUNCE = 0.25


class ActionRunner:
    def __init__(self, get_layout, volume, confirm, on_error):
        self.get_layout, self.on_error = get_layout, on_error
        self.ctx = actions.Context(confirm, volume)
        self.last_press = {}

    def on_press(self, index):
        """Toque no botão de ação `index` do layout (o índice que a placa recebeu no `L A`)."""
        layout, now = self.get_layout(), time.monotonic()
        if not 0 <= index < len(layout) or layout[index]['type'] != 'action':
            return
        if now - self.last_press.get(index, 0) < PRESS_DEBOUNCE:
            return
        self.last_press[index] = now
        if layout[index]['action']['type'] != 'none':
            threading.Thread(target=self.run, args=(layout[index],), daemon=True).start()

    def run(self, el):
        try:
            actions.run(el['action'], self.ctx)
        except Exception as err:
            self.on_error(f'{el["label"] or "Botão"}: {err}')
