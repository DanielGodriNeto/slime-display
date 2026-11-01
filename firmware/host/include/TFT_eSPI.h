// Mock do TFT_eSPI 2.5.43 (ST7796, 480x320 após setRotation(1)) para o harness de firmware/host.
// Modelo de cor: cada pixel guarda a cor RGB565 LÓGICA, a que o painel mostraria.
//   fillRect/fillScreen: cor direta.
//   pushImage com swapBytes=true: cor = valor lido; com false: cor = bswap16(valor).
//   Fonte: pushSwapBytePixels/DAT8TO32 em Processors/TFT_eSPI_ESP32.h e .c (TFT_eSPI 2.5.43).
//   Sprite: mesma regra; pushSprite copia a cor lógica para o alvo.
#pragma once
#include <Arduino.h>

#include <algorithm>
#include <vector>

#define TFT_BL 27  // pino do backlight (platformio.ini)
#define TFT_RED 0xF800
#define TFT_GREEN 0x07E0
#define TFT_BLUE 0x001F

class TFT_eSPI {
 public:
  TFT_eSPI() : w_(480), h_(320), px_(480 * 320, 0) {}
  void init() {}
  void setRotation(uint8_t) {}  // painel fixo em 480x320 (o sketch usa setRotation(1))
  void setSwapBytes(bool on) { swap_ = on; }

  void fillRect(int32_t x, int32_t y, int32_t w, int32_t h, uint32_t color) {
    int32_t x0 = std::max<int32_t>(x, 0), y0 = std::max<int32_t>(y, 0);
    int32_t x1 = std::min<int32_t>(x + w, w_), y1 = std::min<int32_t>(y + h, h_);
    for (int32_t j = y0; j < y1; ++j)
      for (int32_t i = x0; i < x1; ++i) px_[j * w_ + i] = static_cast<uint16_t>(color);
  }
  void fillScreen(uint32_t color) { fillRect(0, 0, w_, h_, color); }

  void pushImage(int32_t x, int32_t y, int32_t w, int32_t h, const uint16_t* data) {
    const bool swap = swap_;
    blit(x, y, w, h, data, [swap](uint16_t v) { return swap ? v : bswap16(v); });
  }

  // Copia com recorte; conv converte cada valor de src na cor lógica.
  template <typename Conv>
  void blit(int32_t x, int32_t y, int32_t w, int32_t h, const uint16_t* src, Conv conv) {
    int32_t x0 = std::max<int32_t>(x, 0), y0 = std::max<int32_t>(y, 0);
    int32_t x1 = std::min<int32_t>(x + w, w_), y1 = std::min<int32_t>(y + h, h_);
    for (int32_t j = y0; j < y1; ++j)
      for (int32_t i = x0; i < x1; ++i) px_[j * w_ + i] = conv(src[(j - y) * w + (i - x)]);
  }

  int32_t width() const { return w_; }
  int32_t height() const { return h_; }
  const uint16_t* framebuffer() const { return px_.data(); }  // cores lógicas RGB565 (lido pelo harness)

  static uint16_t bswap16(uint16_t v) { return static_cast<uint16_t>((v >> 8) | (v << 8)); }

 protected:
  struct NoAlloc {};
  explicit TFT_eSPI(NoAlloc) {}

  int32_t w_ = 0, h_ = 0;
  std::vector<uint16_t> px_;
  bool swap_ = false;
};

// Sprite: mesmo buffer da classe base, com tamanho próprio. Herda a API de desenho.
class TFT_eSprite : public TFT_eSPI {
 public:
  explicit TFT_eSprite(TFT_eSPI* parent) : TFT_eSPI(NoAlloc{}), parent_(parent) {}
  ~TFT_eSprite() { deleteSprite(); }

  void setColorDepth(int) {}  // sempre 16 bits (RGB565)

  void* createSprite(int16_t w, int16_t h) {
    deleteSprite();
    if (w <= 0 || h <= 0) return nullptr;
    w_ = w;
    h_ = h;
    px_.assign(static_cast<size_t>(w) * static_cast<size_t>(h), 0);
    return px_.data();
  }
  void deleteSprite() {
    px_.clear();
    px_.shrink_to_fit();
    w_ = h_ = 0;
  }
  void pushSprite(int32_t x, int32_t y) {
    parent_->blit(x, y, w_, h_, px_.data(), [](uint16_t v) { return v; });
  }

 private:
  TFT_eSPI* parent_;
};
