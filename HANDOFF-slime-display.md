# Handoff Slime Display (2026-10-29)

Repo: C:\Users\Mancato\Documents\Github\slime-display. CYD ESP32-3248S035C (480x320 ST7796, GT911, COM5), app Python no PC (pc/), firmware PlatformIO (firmware/).
Usuário: fala português, iniciante em hardware, usa ditado, se frustra fácil com trabalho desleixado. Respostas curtas, perguntas no fim.

## Feito nesta sessão (NADA commitado; git mostra 6 arquivos modificados)
- Firmware (firmware/src/main.cpp, partitions.csv, platformio.ini): fundo de foto (8 vagas de 480x320 RGB565 little-endian na partição `photos` 0x170000, mmap), relógio com segundos (`T HH:MM:SS`, flag `b` do clock), linha de progresso fina com "-tempo que falta", botões só ícone, sombra preta sólida no texto sobre foto, comandos `G <vaga|-1>` e `U <vaga> <bytes>` (blocos de 4096, resposta "A" por bloco e "OK" no fim). Compila e foi GRAVADO na placa (pio run -t upload --upload-port COM5).
- PC: layout.py (`seconds`, clock escala 1-5, `photo_layout(accent)`, `PHOTO_ACCENTS`), deck_model.py (chave `photo`, -1..7), slime_display.py (envia `G` e `T` com segundos), preview.py, e **pc/photo_tool.py** (`photo_tool.py <vaga> <imagem> [COM5]`, feche o app antes; espera 2 s após abrir a porta).
- Fotos P1-P4 já enviadas às vagas 0-3 (assets-src/raw3: s0.jpg, s1.webp, s2.jpg, s3.webp, corte central).
- %APPDATA%\slime-display\deck.json está com photo=0 e layout photo_layout; testes: `pc/.venv/Scripts/python.exe pc/test_deck.py` (passam).
- O dist/SlimeDisplay.exe é o ANTIGO (sem foto); refazer com tools/build_exe.bat. Rodando por fonte: `pc/.venv/Scripts/pythonw.exe slime_display.py`.

## PROBLEMA ABERTO (começar por aqui)
Na placa só aparece a foto, sem nenhuma interface (hora, música, botões). Sem foto/sem app a tela fica preta. Na última checagem o app (pythonw) estava rodando e a placa continuava APAGADA.
Fatos apurados:
- A placa apaga a tela sozinha se não receber dados (`screenOff()`: lastRx==0 ou SLEEP_AFTER_MS). Abrir a serial reseta a placa (DTR); layout/foto não persistem, o app precisa reenviar após o HELLO. Testes manuais com script apagam/zeram a placa e confundem.
- Sem crash/reboot loop (HELLO uma vez). Layout em deck.json está correto (8 elementos).
- Hipóteses a verificar: (1) app não conecta/reenvia após reset (checar status do app, porta presa por outro processo; matar todos os pythonw e SlimeDisplay.exe antes); (2) com foto, elementos não aparecem: ver `redraw()` e `drawClock/drawTitle/...` em modo `ph` (sprites com `bg()`/pushImage setSwapBytes, ordem dStatic); testar `G -1` COM app rodando para separar bug de foto vs bug de layout; (3) conferir `lastRx` atualizado em readSerial e o upload não deixar `upLeft` preso.
- Ferramenta de depuração: reset por RTS (dtr False, rts True 0.1 s, rts False), ler a 921600 após ~1.5 s; o boot log sai a 115200 (lixo a 921600 é normal).
- Combine com o usuário olhar a placa com o app rodando; ele não vê logs.

## Pendente depois
- Tela no app para escolher foto/fonte/layout e adicionar imagens (o usuário quer editar "tudo"); refazer .exe; atualizar comentário de protocolo no topo do main.cpp (G, U, T com segundos, clock b); scan de segurança do diff + commits Conventional, sem atribuição de IA; perguntar antes de dar push.
- Temas Z1/Z2, A1/A2, K1-K3, N1/N1b/N3/N4 (docs/temas-jogos-v5.html) ainda não existem no firmware (só paletas).
