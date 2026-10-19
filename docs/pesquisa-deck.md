# Pesquisa: features de macro-pad / Stream Deck (uso nao-streaming)

Data: 2026-10-19. Esforco = Python/tkinter/Windows. Valor = casa/gamer/trabalho.
Legenda: B baixo, M medio, A alto. "Verificado" = visto em fonte; "nao verificado" = conhecimento geral.

## Fontes (o que cada uma confirmou)
- Elgato: Multi Action (varios passos: abrir app, pausa, atalho, comando), perfis, Marketplace de plugins/icones: https://www.elgato.com/explorer/products/stream-deck/how-to-be-more-productive-with-stream-deck/ . Toggle, perfil por app e pastas: NAO confirmado nessa pagina (nao verificado aqui; sao features conhecidas do app).
- Companion: triggers, variaveis, feedbacks (booleano on/off e avancado), paginas, Import/Export (backup/restore): https://companion.free/user-guide/v4.3/category/configuration-gui e https://newreleases.io/project/github/bitfocus/companion/release/v5.0.0
- Macro Deck: perfis, pastas, variaveis globais, Cottle (templates/condicoes), Extension Store, plugins (AutoHotkey, Home Assistant, Windows Utils...): https://macro-deck.app/ ; Windows Utils (cmd com saida em variavel, abrir app, volume, hotkeys): https://github.com/VLTNOgithub/Macro-Deck-Windows-Utils-Plugin
- StreamController (Linux): paginas (criar/duplicar/exportar), troca automatica de pagina por janela em foco, loja de plugins, estados por tecla, CLI/D-Bus: https://github.com/StreamController/StreamController
- Touch Portal: multi-acao num botao, simulacao de teclas/mouse, funcoes Windows; paginas ilimitadas, eventos, valores e muitos plugins so no Pro (pago); versao base = 2 paginas 4x2: https://www.touch-portal.com/
- DIY ESP32: FreeTouchDeck/ESP32 Touchdown (ILI9488+XPT2046, HID por Bluetooth): https://hackaday.com/tag/ili9488/ ; ESP32 classico nao tem USB nativo, precisa S2/S3 ou CH9329 (https://github.com/vladyst/esp32-macropad) -> nao verificado em fonte oficial.

## Decisao de arquitetura que muda tudo
CYD (ESP32 classico) nao e teclado USB. Entao o PC executa as acoes: o deck envia "botao N tocado" pela serial e o app Windows faz o resto. Vantagem: todas as acoes abaixo (volume por app, janelas, PowerShell) sao possiveis, o que um HID puro nao faria. Custo: o app precisa estar rodando (bandeja + iniciar com Windows viram obrigatorios).

## 1. Tipos de acao
| Feature | O que faz | Esf | Valor |
|---|---|---|---|
| Abrir app/arquivo | os.startfile / subprocess | B | A |
| Abrir URL | webbrowser.open | B | A |
| Abrir pasta | os.startfile(pasta) | B | M |
| Atalho de teclado (hotkey) | envia Ctrl+Shift+X etc (lib keyboard ou SendInput via ctypes) | M | A |
| Digitar texto | SendInput unicode; texto longo via clipboard+Ctrl+V e mais confiavel | M | A |
| Macro sequencia c/ atrasos | lista de passos (acao + espera ms) = multi-acao | M | A |
| Midia (play/pause/prox/ant) | teclas virtuais VK_MEDIA_* | B | A |
| Volume master / mudo | teclas VK_VOLUME_* ou pycaw | B | A |
| Volume por app | pycaw (sessoes WASAPI) | M | M (gamer: A; Discord vs jogo) |
| Trocar saida de audio | COM nao documentado (PolicyConfig) ou nircmd/SoundVolumeView externo; fragil | A | M |
| Mutar microfone | pycaw endpoint de captura (SetMute) | M | A (reunioes) |
| Energia (bloquear, suspender, desligar, reiniciar) | ctypes LockWorkStation; shutdown.exe; exigir confirmacao | B | M |
| Script/PowerShell/cmd | subprocess com args em lista | B | M (power user) |
| Janela: minimizar/focar/mover | pywin32/ctypes EnumWindows, SetForegroundWindow (Windows limita foco; truque de ALT) | M | M |
| Minimizar tudo (Win+D) | hotkey | B | M |
| Clipe da area de transferencia | colar texto salvo (snippets) | B | A (trabalho) |
| Screenshot | Win+Shift+S ou PIL.ImageGrab salvando em pasta | B | M |
| OBS | fora de escopo (pedido) | - | - |
| Esperar / repetir / condicional | passos extras de macro | M | B (so "esperar" vale) |

## 2. Editor visual
| Feature | O que faz | Esf | Valor |
|---|---|---|---|
| Grade 3x? com clique para editar | tkinter Canvas/Frame com botoes; preview 480x320 | M | A |
| Arrastar para reorganizar | drag&drop em Canvas (trocar 2 botoes) | M | A |
| Biblioteca de icones | pacote de PNG/SVG livres (ex. Lucide/Material) pre-renderizados | M | A |
| Emoji como icone | renderizar com Pillow + fonte Segoe UI Emoji (cor: embedded_color=True) | M | M |
| Imagem propria | Pillow: abrir, recortar quadrado, redimensionar, converter RGB565 | B | A |
| Cor de fundo/texto, rotulo | seletor de cor tk | B | A |
| Estados on/off (icone muda) | 2 aparencias por botao | M | A |
| Desfazer/refazer | pilha de snapshots JSON | M | M |
| Pre-visualizacao fiel do display | desenhar a mesma imagem que vai pro deck | B | A |

## 3. Paginas, pastas, perfis
| Feature | Esf | Valor |
|---|---|---|
| Varias paginas (deslizar/botao proximo) | B | A |
| Pasta (botao abre sub-pagina + voltar) | M | A |
| Perfis nomeados (Trabalho/Jogo/Casa) com troca manual | M | A |
| Perfil automatico por app em foco (GetForegroundWindow -> nome do exe, poll 1s) | M | A (so se mapa exe->perfil for simples na UI) |
| Botao "voltar ao perfil anterior" | B | M |

## 4. Toggle e multi-acao
| Feature | Esf | Valor |
|---|---|---|
| Toggle (ex. mutar mic: liga/desliga, icone muda) | M | A |
| Estado lido do sistema (mic realmente mudo?) em vez de assumido | M | A (evita icone mentir) |
| Multi-acao (sequencia no botao) | M | A |
| Segurar vs toque (long press = 2a acao) | M | M |
| Variaveis/feedbacks/triggers estilo Companion | A | B para leigo - evitar |
| Template Cottle/condicoes | A | B - evitar |

## 5. Widgets
| Feature | Esf | Valor |
|---|---|---|
| Relogio/data | B | A |
| CPU/RAM (psutil) | B | A |
| GPU (NVIDIA via nvidia-smi/pynvml; AMD/Intel dificil) | M | M (gamer A) |
| Temperatura CPU | A (Windows sem API simples) | M - evitar no v1 |
| Clima (API gratis Open-Meteo, sem chave) | M | M |
| Spotify (API OAuth, conta Premium p/ controle) | A | M; usar teclas de midia primeiro |
| "Agora tocando" via SMTC (winsdk) | M | M |
| Contador/timer/pomodoro | M | M |

## 6. Importar/exportar, backup, sistema
| Feature | Esf | Valor |
|---|---|---|
| Config em um JSON + pasta de imagens | B | A |
| Exportar/importar perfil (zip) | B | A |
| Backup automatico (copia datada, manter 5) | B | A |
| Iniciar com o Windows (atalho em shell:startup ou HKCU Run) | B | A |
| Icone na bandeja (pystray) | M | A |
| Reconexao automatica da serial / deteccao de porta | M | A |
| Atualizacao: so checar versao no GitHub e avisar | B | M; auto-update = A esforco, evitar |
| Brilho / tela apagada por inatividade | B | A |
| Loja de plugins / API de plugins | A | B - evitar |
| Acesso remoto/web/celular | A | B - evitar |

## 7. Seguranca (o que impedir)
- Config e dados tratados como nao confiaveis: perfil importado pode conter comandos. Ao importar, mostrar lista de acoes perigosas (script, powershell, energia, URL, abrir exe) e exigir aprovacao antes de ativar.
- subprocess sempre com lista de argumentos, sem shell=True, sem interpolar texto da config em comando.
- Acoes destrutivas (desligar, reiniciar, apagar) pedem confirmacao (segundo toque / dialogo no PC).
- Serial: aceitar so mensagens bem formadas e curtas "botao N"; o deck nunca envia comando livre. Ignorar indices fora do range. Limitar taxa (debounce).
- Nunca guardar senhas/tokens em texto puro no JSON; "digitar texto" nao deve ser usado para senhas (avisar).
- Bloquear script de caminho que nao existe; mostrar o comando completo no editor antes de salvar.
- Opcao "pausar deck com PC bloqueado" (nao executar com tela bloqueada).
- Spotify/clima: token so no Windows Credential Manager (keyring) se usar.

## Mais pedidas/valiosas (v1 sugerido)
1. Abrir app/URL/pasta; 2. hotkey; 3. macro com atrasos; 4. digitar texto/clipe; 5. midia+volume+mutar mic (toggle com estado real); 6. paginas+pastas+perfis; 7. icone/cor/emoji/imagem propria com preview; 8. bandeja + iniciar com Windows + reconexao; 9. exportar/importar + backup; 10. widgets relogio e CPU/RAM.
Segunda onda: perfil por app em foco, volume por app, GPU, clima, long press, desfazer.
Evitar: variaveis/feedbacks/triggers, templates, loja de plugins, auto-update, trocar saida de audio (fragil), temperatura CPU, Spotify OAuth, acesso remoto. Motivo: complexidade alta, um leigo nao usa, ganho pequeno.

## Nao verificado
- Detalhes de toggle/perfil por app/pastas do Elgato (confirmado so Multi Action/perfis/Marketplace nesta pesquisa).
- Paginas oficiais do Macro Deck/Companion/Elgato docs retornaram 404 ou vazias no fetch; features vem de resultados de busca e README de terceiros.
- Notas de esforco/valor sao julgamento proprio, nao medicao.
- Viabilidade de bibliotecas (pycaw, pystray, winsdk) nao testada aqui.
