# Slime Display

Display de música estilo Slime Rancher para a CYD ESP32-3248S035C (3.5", 480×320). O app do Windows escolhe o slime (28 temas) e manda música, equalizador, volume e hora pela USB, e a tela é **uma só, toda montada por você**: slime, nome da música, tempo, relógio, botões... o que não quiser, você tira.

## Placa (firmware)
1. Instale o PlatformIO (extensão do VS Code ou `pip install platformio`).
2. `cd firmware` e `pio run -t upload` (placa na USB). Monitor serial: `pio device monitor`.
3. No boot aparece uma barra de teste: deve ser **R, G, B** nessa ordem.
   - Vermelho/azul trocados: em `platformio.ini` troque `TFT_BGR` por `TFT_RGB`.
   - Cores invertidas (fundo claro): descomente `-DTFT_INVERSION_ON=1`.
4. Toque errado (espelhado): ajuste `TOUCH_FLIP_X` / `TOUCH_FLIP_Y` no topo de `src/main.cpp`. Com `TOUCH_DEBUG=1` a placa imprime `TOUCH x y` no serial.
5. Pinos do toque (SDA 33, SCL 32, INT 21, RST 25) são os usuais dessa CYD; se não responder, confira no seu modelo.

## App do Windows
```
python -m venv pc\.venv
pc\.venv\Scripts\pip install -r pc\requirements.txt
pc\.venv\Scripts\python pc\slime_display.py
```
- A porta é detectada sozinha (CH340); ou escolha na lista.
- Clique num slime: tema e nome ("<NOME> FM") mudam na placa; a escolha fica salva e a placa a guarda também.
- Música: lê a mídia atual do Windows (Spotify, navegador etc.). Equalizador: áudio das caixas padrão.
- Botões da placa: anterior / play / próxima enviam teclas de mídia; o botão de volume gira 0-2-4-6-8-10.

## Tela (aba "Tela")
- A prévia é a tela da placa. Clique num item para editar, arraste para mover, use o quadradinho do canto para mudar o tamanho. Setas movem 2 px (Shift: 10). Delete ou "Remover item" tira. Ctrl+Z / Ctrl+Y desfazem e refazem; "Restaurar padrão" volta ao original.
- Itens da lista à esquerda: slime, nome da música, artista, equalizador, tempo e barra, relógio, volume, texto livre (`{slime}` vira o nome do slime), botões de música (anterior/play/próxima/volume) e botões que abrem coisas (ícone de slime + texto).
- Ações dos botões: abrir programa, site, pasta, atalho de teclado, digitar texto, macro (vários passos com pausas), mutar microfone, bloquear o PC. "Experimentar" testa sem tocar na placa.
- Tudo o que muda é salvo e enviado para a placa na hora. Ao ligar sem o app, a placa mostra a tela padrão.
- Aba Ajustes: porta, abrir com o Windows (fica na bandeja), exportar/importar tela. Importar mostra os botões que mexem no PC antes de aceitar: só importe de quem você confia.
- Dados em `%APPDATA%\slime-display\deck.json`. Testes: `pc\.venv\Scripts\python pc\test_deck.py`.

## Regenerar sprites
`python tools/gen_assets.py` (da raiz) refaz `firmware/src/sprites.h`, `pc/icons` e `pc/slimes.json` a partir de `tools/sprites_src.js`.

## Protocolo serial (921600, linhas com LF)
PC→placa: `S n` · `N play|pos|dur|titulo|artista` · `V 0-10` · `E <24 dígitos 0-9>` · `T HH:MM` · layout: `L C` (limpa), `K corTexto corDestaque` (RGB565, 0 = do slime) · `L A <tipo> x y w h a b corTexto corDestaque desenho|- [texto]` (um item; desenho = 100 dígitos hex, 20x20 bits), `L D` (aplica). Tipos: s slime, t título, r artista, e equalizador, p progresso, c relógio, v volume, m botão de mídia, a botão de ação, x texto.
Placa→PC: `HELLO` (boot) · `B prev|play|next|vol` · `B a<n>` (botão de ação de índice n) · `TOUCH x y` (só com `TOUCH_DEBUG`)

## Cores e desenho

Na aba **Slime** há duas cores globais (principal e de destaque); "Padrão" volta às cores do slime. Na aba **Tela**, cada item tem suas próprias cores ("Cores deste item"). Botões de ação têm **Desenhar o meu ícone...** (também por duplo clique no botão): quadro 20x20 pintado com a cor de destaque do item.

## Aviso
Projeto de fã, sem fins lucrativos e sem ligação com a Monomi Park. Slime Rancher e seus personagens pertencem aos seus donos; os sprites aqui são redesenhos em pixel art para uso pessoal. O código é livre para estudar e adaptar.
