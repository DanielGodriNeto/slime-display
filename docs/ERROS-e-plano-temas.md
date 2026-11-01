# Temas do Slime Display: o que deu errado e o plano

## O que eu fiz de errado (29/10/2026)
1. **Desenhei pixel art na mão** (carros, David, cidade procedural) em vez de pesquisar referências. Não sei desenhar sprite que preste por código.
2. **Recorte ruim do David**: tentei tirar o fundo por cor (verde/roxo). Onde o rastro roxo encostava no corpo, o filtro comeu partes (braço, mão, contorno). Resultado: peça faltando e cortes tortos.
3. **Resolução baixa demais**: reduzi o David para 28x98 px antes de limpar. Pixel art boa nasce de uma imagem boa e bem recortada, não de um recorte ruim encolhido.
4. **Não pesquisei quando você pediu** (carros): desenhei 20x8 pixels no código e entreguei como se fosse o pedido.
5. **Mostrei sem olhar com olho crítico**: mandei vários mockups sem admitir que estavam fracos.
6. **Efeito Sandevistan errado várias vezes**: cópias que se mexiam (no anime elas ficam paradas, mudam de cor e somem juntas); bloom que você não queria.
7. **Mockups repetidos e longos**: gastei rodadas ajustando detalhe em vez de mostrar direção diferente.

## O que existe no seu PC (verificado)
- GPU **AMD RX 7600 (8 GB)**, 32 GB de RAM. Sem NVIDIA/CUDA.
- Ollama com modelos de **texto e visão** (qwen3-vl:4b entende imagem, **não gera** imagem).
- Sem Stable Diffusion/ComfyUI instalado. `onnxruntime` e `opencv` estão no Python (dá para rodar recorte de fundo profissional, tipo rembg/U2Net).

## Como ficar bom de verdade (recomendação)
| Caminho | Qualidade | Esforço | Observação |
|---|---|---|---|
| **A. Imagem real da web + recorte por IA (rembg) + conversão por paleta** | Alta se a fonte for boa | Baixo | Resolve o David: pego um frame limpo (sem rastro), recorto certo, converto para 16-24 cores. **Minha recomendação.** |
| **B. Gerar pixel art local** (stable-diffusion.cpp com Vulkan na RX 7600 + LoRA de pixel art) | Média/alta | Médio (instalar ~10 GB) | Funciona em AMD, ~1 min por imagem. Bom para fundos. |
| **C. Você gera em site/IA grátis** e eu só integro | Alta | Você gasta tempo | Sou eu que converto e ponho na placa. |
| **D. Sem sprite**: layout tipográfico/HUD com paleta e fonte do jogo | Segura | Baixo | O B (Militech) ficou assim e foi o melhor aceito. |

Regra daqui para frente: **eu não desenho asset.** Só layout, cores, fonte, e imagens reais recortadas/convertidas por ferramenta.

## Mockups pedidos (3 por jogo)
Jogos: Project(?) Void, Zelda BotW, Halo 3, Cyberpunk Edgerunners, Death Note, Minecraft. Todos com: relógio, botões, barra de progresso, tempo, artista, equalizador, número grande. Só layout + referência real, sem sprite desenhado por mim.
