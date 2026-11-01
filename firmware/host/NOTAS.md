# Harness nativo do firmware (firmware/host)

Compila `firmware/src/main.cpp` sem alterá-lo, com mocks do Arduino/TFT_eSPI/partições, e grava o framebuffer 480x320 como PPM P6. Converte para PNG com `ppm2png.py`.

## Arquivos
- `include/Arduino.h`: String (sobre std::string), Serial (entrada alimentada pelo harness, saída em stdout), relógio falso (`g_fake_ms`, começa em 5000), `ledcWrite` (guarda o duty), `ESP` (heap fixo), `min`/`max`/`constrain` tipados.
- `include/TFT_eSPI.h`: TFT (480x320) e TFT_eSprite (herda do TFT, buffer próprio). Cada pixel guarda a cor RGB565 lógica.
- `include/esp_partition.h`: partição "photos" em memória (0x280000 bytes, 0xFF = apagada), `esp_partition_mmap`, `erase_range`, `write`.
- `include/Preferences.h`: NVS em memória (zera a cada execução).
- `include/TAMC_GT911.h`: sem toque (`isTouched` sempre false).
- `main_host.cpp`: `#include "../src/main.cpp"`, lê o script, roda `setup()`/`loop()`, grava o PPM.
- `build.sh`: `g++ -std=c++17 -O1 -Wall -Wextra -I host/include -I src host/main_host.cpp -o host/slime_host.exe`. Resultado: 0 warnings.
- `ppm2png.py`: PPM para PNG (Pillow, usar `pc/.venv/Scripts/python.exe`).
- `demo.txt`: tema de exemplo (S 0, T 21:48, N, V 7, E 24 dígitos, layout padrão do `setup()`, @wait 1000).
- `out/demo.ppm`, `out/demo.png`: saída do demo (sólido, sem foto).
- `out/demo_foto.ppm`, `out/demo_foto.png`: mesmo demo com `G 0` e foto sintética (gradiente RGB565 little-endian, gerada em scratchpad, não versionada). Usado para validar o caminho da foto.
- `slime_host.exe`: binário gerado (não está no .gitignore).

## Uso
```
firmware/host/build.sh
firmware/host/slime_host.exe <photos.bin|-> <script.txt> <saida.ppm>
pc/.venv/Scripts/python.exe firmware/host/ppm2png.py saida.ppm saida.png
```
- `-` = partição "photos" ausente (fundo liso). Um .bin = partição presente, com slots de 0x50000 bytes.
- Script: uma linha = um comando serial (S, N, V, E, T, K, L ...), injetado no buffer da Serial seguido de `loop()`. `@wait <ms>` avança o relógio falso de 10 em 10 ms chamando `loop()`. Linhas `#` e vazias são ignoradas. Comando `@` desconhecido aborta com código 1.
- Ao fim: 5 `loop()` para estabilizar, depois grava o PPM. O stderr informa o duty do backlight e se a tela estaria apagada pelo timeout.

## Semântica de cor (lida no código do TFT_eSPI 2.5.43; a ordem dos bytes no fio é inferência, não testada em hardware)
- `pushPixels` com `_swapBytes=true` chama `pushSwapBytePixels`, que empacota com `DAT8TO32(P) = P[0]<<8 | P[1] | ...` (em `Processors/TFT_eSPI_ESP32.h`). O resultado é que o painel recebe o valor lido. Com `false`, o painel recebe `bswap16`.
- Logo: cor lógica = `swap ? v : bswap16(v)`. Com `setSwapBytes(true)` (que o `bg()` sempre usa), uma foto little-endian aparece com as cores que o arquivo codifica. O teste de gradiente confirmou isso: vermelho à direita, azul à esquerda, verde para baixo.
- Sprite: o buffer do sprite guarda a cor pronta para o painel; `pushSprite` copia sem trocar bytes. O modelo lógico é equivalente.
- `fillRect` e `fillScreen` usam a cor direta (sem swap). Isso bate com o TFT_eSPI.

## O que NÃO é fiel (limites)
- Tempo: relógio falso. Não há intervalo real de UART, SPI, DMA, nem interrupção. O harness redesenha uma vez por linha de comando. A placa faz `loop()` em alta frequência, então a ordem de desenho entre comandos pode diferir em casos de corrida.
- Heap: `createSprite` sempre sucede se w,h > 0. Na placa, heap baixo faz o código cair no caminho sem sprite (desenho direto). `ESP.getFreeHeap()` e `getMaxAllocHeap()` devolvem valores fixos.
- Serial: sem limite de RX (8192 na placa), sem perda, sem tempo de transmissão. Upload de foto (`U`, bytes binários) não é suportado no script de texto; o timeout de 4000 ms é atingido só via `@wait`.
- Toque: nunca pressionado. Não há injeção de toque no script. A calibração e o `onTap` não são exercitados.
- Backlight: não é renderizado. A tela é sempre gravada (mesmo "apagada" por `screenOff()`). Só o duty é reportado.
- NVS: começa vazio a cada execução (o `slime` salvo na placa não é lido).
- Rotação: fixa em 480x320 (`setRotation` é no-op).
- Fontes: stb_truetype é o mesmo código, mas o ponto flutuante do MinGW x86 pode diferir do ESP32 em arredondamentos de 1 px. Não medido.
- Não implementados (não usados por `main.cpp`): `pinMode`, `digitalWrite`, `Serial.print`, `getSwapBytes`, `drawPixel`. Adicionar se o sketch passar a usá-los.
- A cor da TFT_BGR/RGB do `platformio.ini` (`TFT_RGB_ORDER=TFT_BGR`) não é modelada: o TFT_eSPI já corrige a ordem no init, então a cor lógica é a correta.
- Nada foi verificado em hardware.

## Observações
- Demo (`out/demo.png`): relógio, título em rolagem, equalizador, botões e barra de progresso aparecem. O relógio sai cortado ("21:4"). Isso vem do próprio firmware: `drawClock` limita a largura a `W - e.x` (352 px de x, 128 px de largura, escala 2). O layout padrão do `setup()` faz isso. Se o PC mandar outra posição para o relógio, o corte some. Não é bug do harness; vale checar o layout do PC.
- O `git status` do repo mostrava `firmware/src/main.cpp` modificado antes desta tarefa. Não foi tocado aqui. O harness compila a versão atual do working tree.
- Sugestão: adicionar `firmware/host/slime_host.exe` e `firmware/host/out/*.ppm` ao .gitignore (não foi feito; fora do escopo).
