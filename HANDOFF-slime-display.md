# Handoff: slime-display

Estado: tela de música personalizável (cores globais e por item, ícone 20x20 desenhável) pronta; 9 testes OK e firmware compila. Falta testar na placa (cores TFT_BGR, toque, ícone, elementos sobrepostos).

Comandos:
- Testes: `pc\.venv\Scripts\python pc\test_deck.py`
- Firmware: `cd firmware && pio run` (upload: `pio run -t upload`)
- App: `pc\.venv\Scripts\python pc\slime_display.py`

Próximo passo: quando a placa chegar, gravar o firmware e conferir cores, toque e o ícone desenhado.
