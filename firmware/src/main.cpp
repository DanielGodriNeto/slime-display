// Slime Display - CYD ESP32-3248S035C (480x320, ST7796 + GT911).
// Uma única tela (a da música) cujos elementos vêm do PC (ver pc/slime_display.py) e podem ficar em qualquer lugar.
//
// PC -> placa (linhas terminadas em LF):
//   S <n>                         slime escolhido (0..N_SLIMES-1)
//   N <play 0/1>|<pos s>|<dur s>|<titulo>|<artista>
//   V <0..10>                     volume
//   E <24 digitos 0-9>            barras do equalizador
//   T HH:MM                       relógio
//   L C                           começa um layout novo
//   K <cor texto> <cor destaque>  cores globais em RGB565 (0 = as do slime)
//   L A <tipo> x y w h a b <cor texto> <cor destaque> <desenho|-> [texto]  adiciona um elemento (tipos abaixo)
//       cores 0 = as da tela; desenho = 100 dígitos hex (20x20 bits) usado no botão de ação
//   L D                           fim: aplica o layout
//       s slime (a=escala 1-5)   t título (w, a=escala 1-3)   r artista (w, a=escala 1-2)
//       e equalizador (w,h)      p progresso (w)              c relógio (a=escala 1-3)
//       v volume (a=escala)      m botão de mídia (w,h, a=0 prev 1 play 2 next 3 vol)
//       a botão de ação (w,h, a=id devolvido no toque, b=slime do ícone, texto)        x texto fixo (a=escala, texto)
// placa -> PC:
//   HELLO                         no boot (PC reenvia o estado e o layout)
//   B prev|play|next|vol|a<n>     botão tocado (a<n> = campo a do botão de ação)
#include <Arduino.h>
#include <Preferences.h>
#include <TAMC_GT911.h>
#include <TFT_eSPI.h>

#include "sprites.h"

// ---- ajustes de toque (confira com as linhas "TOUCH x y" no monitor serial) ----
#define TOUCH_SDA 33
#define TOUCH_SCL 32
#define TOUCH_INT 21
#define TOUCH_RST 25
// Calibração medida nos 4 cantos desta placa: o painel entrega x/y trocados e fora de escala.
// tela_x vem do y cru (de 280 na esquerda a -125 na direita); tela_y vem do x cru (de 196 em cima a 444 embaixo).
#define TOUCH_X_LEFT 280
#define TOUCH_X_RIGHT -125
#define TOUCH_Y_TOP 196
#define TOUCH_Y_BOTTOM 444
#define TOUCH_DEBUG 1

enum { W = 480, H = 320, NB = 24 };
#define BAUD 921600

TFT_eSPI tft;
TFT_eSprite eqS(&tft), titS(&tft), slS(&tft);
TAMC_GT911 tp(TOUCH_SDA, TOUCH_SCL, TOUCH_INT, TOUCH_RST, W, H);
Preferences prefs;

const char* const IC_PREV[9] = {"#.......#", "#......##", "#.....###", "#....####", "#...#####",
                                "#....####", "#.....###", "#......##", "#.......#"};
const char* const IC_PLAY[7] = {"##......", "####....", "######..", "########", "######..", "####....", "##......"};
const char* const IC_PAUSE[7] = {"###..###", "###..###", "###..###", "###..###", "###..###", "###..###", "###..###"};
const char* const IC_VOL[9] = {"....#......", "...##..#...", "#####...#..", "#####.#.#..", "#####.#.#..",
                               "#####.#.#..", "#####...#..", "...##..#...", "....#......"};

// Fonte 5x7: 7 linhas de 5 bits por caractere.
const char FONT_CHARS[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-:.#,!?/'()&+";
const uint8_t FONT[][7] = {
    {14, 17, 17, 31, 17, 17, 17}, {30, 17, 17, 30, 17, 17, 30}, {14, 17, 16, 16, 16, 17, 14},
    {30, 17, 17, 17, 17, 17, 30}, {31, 16, 16, 30, 16, 16, 31}, {31, 16, 16, 30, 16, 16, 16},
    {14, 17, 16, 23, 17, 17, 15}, {17, 17, 17, 31, 17, 17, 17}, {14, 4, 4, 4, 4, 4, 14},
    {7, 2, 2, 2, 2, 18, 12},      {17, 18, 20, 24, 20, 18, 17}, {16, 16, 16, 16, 16, 16, 31},
    {17, 27, 21, 21, 17, 17, 17}, {17, 25, 21, 19, 17, 17, 17}, {14, 17, 17, 17, 17, 17, 14},
    {30, 17, 17, 30, 16, 16, 16}, {14, 17, 17, 17, 21, 18, 13}, {30, 17, 17, 30, 20, 18, 17},
    {15, 16, 16, 14, 1, 1, 30},   {31, 4, 4, 4, 4, 4, 4},       {17, 17, 17, 17, 17, 17, 14},
    {17, 17, 17, 17, 17, 10, 4},  {17, 17, 17, 21, 21, 27, 17}, {17, 17, 10, 4, 10, 17, 17},
    {17, 17, 10, 4, 4, 4, 4},     {31, 1, 2, 4, 8, 16, 31},     {14, 17, 19, 21, 25, 17, 14},
    {4, 12, 4, 4, 4, 4, 14},      {14, 17, 1, 2, 4, 8, 31},     {30, 1, 1, 14, 1, 1, 30},
    {2, 6, 10, 18, 31, 2, 2},     {31, 16, 30, 1, 1, 17, 14},   {6, 8, 16, 30, 17, 17, 14},
    {31, 1, 2, 4, 8, 8, 8},       {14, 17, 17, 14, 17, 17, 14}, {14, 17, 17, 15, 1, 2, 12},
    {0, 0, 0, 31, 0, 0, 0},       {0, 4, 0, 0, 0, 4, 0},        {0, 0, 0, 0, 0, 12, 12},
    {10, 10, 31, 10, 31, 10, 10}, {0, 0, 0, 0, 12, 4, 8},       {4, 4, 4, 4, 4, 0, 4},
    {14, 17, 1, 2, 4, 0, 4},      {1, 1, 2, 4, 8, 16, 16},      {4, 4, 8, 0, 0, 0, 0},
    {2, 4, 8, 8, 8, 4, 2},        {8, 4, 2, 2, 2, 4, 8},        {12, 18, 20, 8, 21, 18, 13},
    {0, 4, 4, 31, 4, 4, 0}};

// ---- estado ----
uint8_t slime = 0;
bool playing = false;
uint32_t pos = 0, dur = 0;
String title = "NOTHING PLAYING", artist = "";
uint8_t vol = 6;
char clockTxt[6] = "--:--";
uint8_t eqTarget[NB] = {}, eqShown[NB] = {};
uint32_t lastE = 0;
int pressed = -1;
uint32_t pressedAt = 0;
uint16_t K[4];  // bg, panel, accent, text do slime atual
uint16_t twinkleHue = 0;
uint16_t gMain = 0, gAcc = 0;  // cores globais do PC (0 = as do slime)

// ---- layout: lista de elementos enviada pelo PC ----
enum { MAXEL = 24, ICON = 20 };
struct El { char t; int16_t x, y, w, h; uint8_t a, b; uint16_t cm, ca; bool hasPix; uint8_t pix[50]; char label[25]; };
#define MAIN(e) ((e).cm ? (e).cm : K[3])  // cor própria do item, ou a da tela
#define ACC(e) ((e).ca ? (e).ca : K[2])
El els[MAXEL], pend[MAXEL];
int nEl = 0, nPend = 0;
bool eqOk = false, titOk = false, slOk = false;

bool dStatic = true, dClock = true, dProg = true, dBtns = true, dVol = true, dArtist = true, dTitle = true;

void dirtyAll() { dStatic = dClock = dProg = dBtns = dVol = dArtist = dTitle = true; }

// ---- cores ----
uint16_t rgb565(uint8_t r, uint8_t g, uint8_t b) { return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3); }

uint16_t mix(uint16_t a, uint16_t b, uint8_t t) {  // t=0 -> a, t=255 -> b
  int ar = (a >> 11) << 3, ag = ((a >> 5) & 63) << 2, ab = (a & 31) << 3;
  int br = (b >> 11) << 3, bg = ((b >> 5) & 63) << 2, bb = (b & 31) << 3;
  return rgb565(ar + (br - ar) * t / 255, ag + (bg - ag) * t / 255, ab + (bb - ab) * t / 255);
}

uint16_t hsl565(float h, float s, float l) {
  s /= 100; l /= 100;
  float c = (1 - fabsf(2 * l - 1)) * s, hp = fmodf(h, 360) / 60, x = c * (1 - fabsf(fmodf(hp, 2) - 1)), m = l - c / 2;
  float r = 0, g = 0, b = 0;
  if (hp < 1) { r = c; g = x; } else if (hp < 2) { r = x; g = c; } else if (hp < 3) { g = c; b = x; }
  else if (hp < 4) { g = x; b = c; } else if (hp < 5) { r = x; b = c; } else { r = c; b = x; }
  return rgb565((r + m) * 255, (g + m) * 255, (b + m) * 255);
}

void overlay() {
  if (gAcc) K[2] = gAcc;
  if (gMain) K[3] = gMain;
}

void applyTheme() {
  memcpy(K, THEMES[slime], sizeof(K));
  overlay();
  dirtyAll();
}

// ---- texto ----
String clean(String s) {
  s.toUpperCase();
  String o;
  for (uint16_t i = 0; i < s.length(); i++) if (s[i] == ' ' || strchr(FONT_CHARS, s[i])) o += s[i];
  return o;
}
int textW(const String& s, int sc) { return s.length() ? s.length() * 12 * sc - 2 * sc : 0; }

void txt(TFT_eSPI& g, const String& s, int x, int y, int sc, uint16_t col) {
  int d = 2 * sc;
  for (uint16_t n = 0; n < s.length(); n++) {
    const char* p = strchr(FONT_CHARS, s[n]);
    if (!p || s[n] == ' ') continue;
    const uint8_t* gl = FONT[p - FONT_CHARS];
    for (int r = 0; r < 7; r++)
      for (int c = 0; c < 5; c++)
        if (gl[r] >> (4 - c) & 1) g.fillRect(x + (n * 6 + c) * d, y + r * d, d, d, col);
  }
}

void icon(TFT_eSPI& g, const char* const* m, int rows, int cols, int cx, int cy, uint16_t col, bool mirror = false) {
  int x0 = ((cx - cols * 4 / 2) / 2) * 2, y0 = ((cy - rows * 4 / 2) / 2) * 2;
  for (int y = 0; y < rows; y++)
    for (int x = 0; x < cols; x++)
      if (m[y][mirror ? cols - 1 - x : x] == '#') g.fillRect(x0 + x * 4, y0 + y * 4, 4, 4, col);
}

El* find(char t) {
  for (int i = 0; i < nEl; i++) if (els[i].t == t) return &els[i];
  return nullptr;
}

// ---- desenho dos elementos ----
void drawStaticTexts() {
  for (int i = 0; i < nEl; i++)
    if (els[i].t == 'x') txt(tft, String(els[i].label), els[i].x, els[i].y, els[i].a, ACC(els[i]));
}

void drawClock() {
  for (int i = 0; i < nEl; i++)
    if (els[i].t == 'c') {
      int w = textW("00:00", els[i].a), h = 14 * els[i].a;
      TFT_eSprite s(&tft);
      if (s.createSprite(w, h)) {
        s.fillSprite(K[0]);
        txt(s, clockTxt, 0, 0, els[i].a, MAIN(els[i]));
        s.pushSprite(els[i].x, els[i].y);
        s.deleteSprite();
      } else {
        tft.fillRect(els[i].x, els[i].y, w, h, K[0]);
        txt(tft, clockTxt, els[i].x, els[i].y, els[i].a, MAIN(els[i]));
      }
    }
}

// figura do slime `n` (escala sc) com o canto em (ox, oy), num alvo qualquer
void drawSprite(TFT_eSPI& g, int n, int ox, int oy, int sc) {
  int w = SPR_W[n], h = SPR_H[n];
  const uint16_t* px = SPR[n];
  int dx = (ICON - w) * sc / 2, dy = (ICON - h) * sc;
  for (int y = 0; y < h; y++)
    for (int x = 0; x < w; x++) {
      uint16_t c = pgm_read_word(&px[y * w + x]);
      if (c != SPR_TRANSP) g.fillRect(ox + dx + x * sc, oy + dy + y * sc, sc, sc, c);
    }
}

void drawSlime() {
  El* e = find('s');
  if (!e || !slOk) return;
  slS.fillSprite(K[0]);
  drawSprite(slS, slime, 0, playing && (millis() / 250) % 2 ? 0 : 4, e->a);
  slS.pushSprite(e->x, e->y);
}

void drawTitle() {
  El* e = find('t');
  if (!e || !titOk) return;
  titS.fillSprite(K[0]);
  int tw = textW(title, e->a);
  int off = tw > e->w ? (millis() / 60) % (tw + 60) : 0;
  txt(titS, title, -off, 2, e->a, MAIN(*e));
  if (off) txt(titS, title, -off + tw + 60, 2, e->a, MAIN(*e));
  titS.pushSprite(e->x, e->y);
}

void drawArtist() {
  El* e = find('r');
  if (!e) return;
  tft.fillRect(e->x, e->y, e->w, 14 * e->a, K[0]);
  String a = artist.substring(0, max(0, (e->w + 2 * e->a) / (12 * e->a)));
  txt(tft, a, e->x, e->y, e->a, ACC(*e));
}

void drawEq() {
  El* e = find('e');
  if (!e || !eqOk) return;
  eqS.fillSprite(K[0]);
  int pitch = max(2, e->w / NB), bw = max(1, pitch * 3 / 4), top = e->h - 4;
  for (int j = 0; j < NB; j++) {
    int h = max(3, eqShown[j] * top / 9);
    uint16_t col = j % 2 ? ACC(*e) : MAIN(*e);
    eqS.fillRect(j * pitch, e->h - h, bw, h, col);
    eqS.fillRect(j * pitch, e->h - h, bw, 2, mix(col, 0xFFFF, 60));
  }
  eqS.pushSprite(e->x, e->y);
}

String mmss(uint32_t s) { char b[10]; snprintf(b, sizeof b, "%u:%02u", (unsigned)(s / 60), (unsigned)(s % 60)); return b; }

// monta a barra e os tempos fora da tela e envia de uma vez (sem piscar)
void drawProgOn(TFT_eSPI& g, int x, int y, int w) {
  g.fillRect(x, y, w, 8, ACC(*find('p')));
  g.fillRect(x + 2, y + 2, w - 4, 4, K[1]);
  El* e = find('p');
  if (dur) g.fillRect(x + 2, y + 2, ((int)((w - 4) * (uint64_t)min(pos, dur) / dur) / 2) * 2, 4, ACC(*e));
  g.fillRect(x, y + 14, w, 14, K[0]);
  txt(g, mmss(pos), x, y + 14, 1, MAIN(*e));
  String r = dur ? mmss(dur) : "";
  txt(g, r, x + w - textW(r, 1), y + 14, 1, MAIN(*e));
}

void drawProg() {
  El* e = find('p');
  if (!e) return;
  TFT_eSprite s(&tft);
  if (s.createSprite(e->w, 28)) {
    s.fillSprite(K[0]);
    drawProgOn(s, 0, 0, e->w);
    s.pushSprite(e->x, e->y);
    s.deleteSprite();
  } else {
    drawProgOn(tft, e->x, e->y, e->w);
  }
}

// desenha o botão i em `g` com o canto do botão em (ox, oy)
void drawBtnOn(TFT_eSPI& g, int i, int ox, int oy) {
  const El& b = els[i];
  bool press = pressed == i && millis() - pressedAt < 160;
  uint16_t A = ACC(b), M = MAIN(b);
  int y = oy + (press ? 4 : 0), x = ox, w = b.w, h = b.h - 8;  // 8 px reservados para sombra e afundar
  g.fillRect(x, oy, w, b.h, K[0]);
  g.fillRect(x, oy + h, w, 6, mix(K[0], 0, 120));
  g.fillRect(x + 4, y, w - 8, h, A);
  g.fillRect(x, y + 4, w, h - 8, A);
  g.fillRect(x + 6, y + 4, w - 12, h - 8, K[1]);
  g.fillRect(x + 4, y + 6, w - 8, h - 12, K[1]);
  g.fillRect(x + 8, y + 6, w - 16, 2, mix(K[1], 0xFFFF, 40));
  int cx = x + w / 2, cy = y + h / 2;
  if (b.t == 'a') {
    String lb = clean(b.label);
    lb = lb.substring(0, max(0, (w - 10) / 12));
    int sc = max(1, (h - 12 - (lb.length() ? 16 : 0)) / ICON);
    int sx = cx - ICON * sc / 2, sy = cy - (lb.length() ? 8 : 0) - ICON * sc / 2;
    if (b.hasPix) {
      for (int i = 0; i < ICON * ICON; i++)
        if (b.pix[i / 8] >> (i % 8) & 1) g.fillRect(sx + i % ICON * sc, sy + i / ICON * sc, sc, sc, A);
    } else drawSprite(g, min<int>(b.b, N_SLIMES - 1), sx, sy, sc);
    if (lb.length()) txt(g, lb, cx - textW(lb, 1) / 2, y + h - 18, 1, M);
  } else if (b.a == 0) icon(g, IC_PREV, 9, 9, cx, cy, A);
  else if (b.a == 2) icon(g, IC_PREV, 9, 9, cx, cy, A, true);
  else if (b.a == 1) { if (playing) icon(g, IC_PAUSE, 7, 8, cx, cy, A); else icon(g, IC_PLAY, 7, 8, cx, cy, A); }
  else icon(g, IC_VOL, 9, 11, cx, cy, A);
}

// monta o botão fora da tela e envia de uma vez, sem piscar
void drawBtn(int i) {
  const El& b = els[i];
  TFT_eSprite sp(&tft);
  if (sp.createSprite(b.w, b.h)) {
    drawBtnOn(sp, i, 0, 0);
    sp.pushSprite(b.x, b.y);
    sp.deleteSprite();
  } else drawBtnOn(tft, i, b.x, b.y);
}

void drawVol() {
  String v = "VOL ";
  for (int i = 0; i < 10; i++) v += i < vol ? '#' : '-';
  for (int i = 0; i < nEl; i++)
    if (els[i].t == 'v') {
      tft.fillRect(els[i].x, els[i].y, textW(v, els[i].a), 14 * els[i].a, K[0]);
      txt(tft, v, els[i].x, els[i].y, els[i].a, ACC(els[i]));
    }
}

void redraw() {
  if (dStatic) { tft.fillScreen(K[0]); drawStaticTexts(); dStatic = false; }
  if (dClock) { drawClock(); dClock = false; }
  if (dArtist) { drawArtist(); dArtist = false; }
  if (dTitle) { drawTitle(); dTitle = false; }
  if (dProg) { drawProg(); dProg = false; }
  if (dBtns) { for (int i = 0; i < nEl; i++) if (els[i].t == 'm' || els[i].t == 'a') drawBtn(i); dBtns = false; }
  if (dVol) { drawVol(); dVol = false; }
}

// ---- layout ----
void makeSprite(TFT_eSprite& s, bool& ok, bool wanted, int w, int h) {
  s.deleteSprite();
  ok = wanted && w > 0 && h > 0 && s.createSprite(w, h) != nullptr;
}

void applyLayout() {
  memcpy(els, pend, sizeof(El) * nPend);
  nEl = nPend;
  pressed = -1;
  El *e = find('e'), *t = find('t'), *s = find('s');
  makeSprite(eqS, eqOk, e, e ? e->w : 0, e ? e->h : 0);
  makeSprite(titS, titOk, t, t ? t->w : 0, t ? 14 * t->a + 4 : 0);
  makeSprite(slS, slOk, s, s ? ICON * s->a : 0, s ? ICON * s->a + 4 : 0);
  dirtyAll();
}

void addElement(const String& a) {  // "<tipo> x y w h a b corTexto corDestaque desenho|- [texto]"
  if (nPend >= MAXEL || a.length() < 3 || !strchr("strepcvmax", a[0])) return;
  El e = {};
  e.t = a[0];
  int v[8], p = 2;
  String pixHex;
  for (int i = 0; i < 9; i++) {
    int q = a.indexOf(' ', p);
    String tok = a.substring(p, q < 0 ? a.length() : q);
    if (i == 8) pixHex = tok; else v[i] = tok.toInt();
    if (q < 0) { if (i < 8) return; p = a.length(); } else p = q + 1;
  }
  e.cm = constrain(v[6], 0, 65535); e.ca = constrain(v[7], 0, 65535);
  if (pixHex.length() == ICON * ICON / 4)
    for (int i = 0; i < ICON * ICON / 4; i++) {
      int d = strtol(pixHex.substring(i, i + 1).c_str(), nullptr, 16);  // bit n do desenho = dígito n/4, bit 3-n%4
      for (int k = 0; k < 4; k++) {
        int n = i * 4 + k;
        if (d >> (3 - k) & 1) e.pix[n / 8] |= 1 << (n % 8);
      }
      e.hasPix = e.hasPix || d;
    }
  e.x = constrain(v[0], 0, W - 4); e.y = constrain(v[1], 0, H - 4);
  e.w = constrain(v[2], 4, W - e.x); e.h = constrain(v[3], 4, H - e.y);
  e.a = constrain(v[4], 0, 255); e.b = constrain(v[5], 0, 255);
  String label = clean(a.substring(min<int>(p, a.length())));
  label.substring(0, 24).toCharArray(e.label, sizeof e.label);
  switch (e.t) {
    case 's': e.a = constrain(e.a, 1, 5); break;
    case 't': case 'c': e.a = constrain(e.a, 1, 3); break;
    case 'r': case 'v': e.a = constrain(e.a, 1, 2); break;
    case 'x': e.a = constrain(e.a, 1, 3); break;
    case 'e': e.h = min<int>(e.h, 20000 / e.w); break;
    case 'm': e.a = min<int>(e.a, 3); e.h = max<int>(e.h, 20); break;
    case 'a': e.h = max<int>(e.h, 20); break;
  }
  if (e.t == 'e' || e.t == 't' || e.t == 's')  // um de cada (têm buffer próprio)
    for (int i = 0; i < nPend; i++) if (pend[i].t == e.t) return;
  pend[nPend++] = e;
}

void defaultLayout() {
  static const char* const L[] = {
      "s 14 30 0 0 3 0 0 0 -",     "t 106 40 360 30 2 0 0 0 -", "r 106 78 360 14 1 0 0 0 -", "e 22 125 440 45 0 0 0 0 -",
      "p 14 184 452 28 0 0 0 0 -", "x 12 10 0 0 1 0 0 0 - SLIME FM", "c 352 2 0 0 2 0 0 0 -",  "m 14 220 97 54 0 0 0 0 -",
      "m 119 220 136 54 1 0 0 0 -", "m 263 220 97 54 2 0 0 0 -", "m 368 220 97 54 3 0 0 0 -", "v 300 284 0 0 1 0 0 0 -"};
  nPend = 0;
  for (const char* l : L) addElement(l);
  applyLayout();
}

void handleLayout(const String& a) {
  if (a[0] == 'C') nPend = 0;
  else if (a[0] == 'A' && a.length() > 2) addElement(a.substring(2));
  else if (a[0] == 'D') applyLayout();
}

void setColors(const String& a) {  // "K corTexto corDestaque" (RGB565; 0 = do slime)
  int sp = a.indexOf(' ');
  if (sp < 0) return;
  gMain = constrain(a.substring(0, sp).toInt(), 0, 65535);
  gAcc = constrain(a.substring(sp + 1).toInt(), 0, 65535);
  applyTheme();
}

// ---- entrada ----
void setSlime(int n) {
  if (n < 0 || n >= N_SLIMES) return;
  if (n != slime) { slime = n; prefs.putUChar("slime", slime); }
  applyTheme();
}

void handleLine(String l) {
  l.trim();
  if (l.length() < 2) return;
  char cmd = l[0];
  String a = l.substring(2);
  if (cmd == 'L' && a.length()) handleLayout(a);
  else if (cmd == 'S') setSlime(a.toInt());
  else if (cmd == 'K') setColors(a);
  else if (cmd == 'V') { vol = constrain(a.toInt(), 0, 10); dVol = true; }
  else if (cmd == 'T') { a.toCharArray(clockTxt, sizeof clockTxt); dClock = true; }
  else if (cmd == 'E') {
    for (int j = 0; j < NB && j < (int)a.length(); j++) eqTarget[j] = constrain(a[j] - '0', 0, 9);
    lastE = millis();
  } else if (cmd == 'N') {
    int p1 = a.indexOf('|'), p2 = a.indexOf('|', p1 + 1), p3 = a.indexOf('|', p2 + 1), p4 = a.indexOf('|', p3 + 1);
    if (p4 < 0) return;
    bool np = a.substring(0, p1).toInt() != 0;
    String nt = clean(a.substring(p3 + 1, p4)), na = clean(a.substring(p4 + 1));
    if (nt.isEmpty()) nt = "NOTHING PLAYING";
    if (nt != title) { title = nt; dTitle = true; }
    if (na != artist) { artist = na; dArtist = true; }
    if (np != playing) { playing = np; dBtns = true; }
    pos = a.substring(p1 + 1, p2).toInt();
    dur = a.substring(p2 + 1, p3).toInt();
    dProg = true;
  }
}

void readSerial() {
  static String buf;
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') { handleLine(buf); buf = ""; }
    else if (buf.length() < 200) buf += c;
  }
}

void onTap(int x, int y) {
  for (int i = nEl - 1; i >= 0; i--) {
    const El& b = els[i];
    if ((b.t != 'm' && b.t != 'a') || x < b.x || x >= b.x + b.w || y < b.y || y >= b.y + b.h) continue;
    pressed = i; pressedAt = millis(); dBtns = true;
    if (b.t == 'a') Serial.printf("B a%d\n", b.a);
    else {
      if (b.a == 1) playing = !playing;  // otimista; o PC corrige no próximo N
      Serial.printf("B %s\n", b.a == 0 ? "prev" : b.a == 1 ? "play" : b.a == 2 ? "next" : "vol");
    }
    return;
  }
}

void readTouch() {
  static bool was = false;
  static uint32_t last = 0;
  if (millis() - last < 20) return;
  last = millis();
  tp.read();
  if (!tp.isTouched) { was = false; return; }
  int rawX = tp.points[0].x, rawY = (int16_t)tp.points[0].y;
  int x = constrain((rawY - TOUCH_X_LEFT) * W / (TOUCH_X_RIGHT - TOUCH_X_LEFT), 0, W - 1);
  int y = constrain((rawX - TOUCH_Y_TOP) * H / (TOUCH_Y_BOTTOM - TOUCH_Y_TOP), 0, H - 1);
  if (!was) {
#if TOUCH_DEBUG
    Serial.printf("TOUCH %d %d\n", x, y);
#endif
    onTap(x, y);
  }
  was = true;
}

void animate() {
  for (int j = 0; j < NB; j++) {
    int target = millis() - lastE > 800 ? 0 : eqTarget[j];
    if (eqShown[j] < target) eqShown[j] = min(target, eqShown[j] + 4);
    else if (eqShown[j] > target) eqShown[j]--;
  }
  drawEq();
  drawSlime();
  El* t = find('t');
  if (t && textW(title, t->a) > t->w) drawTitle();
  static uint8_t twFrame = 0;
  if (slime == TWINKLE_IDX && ++twFrame % 8 == 0) {  // troca de cor ~2x/s: cada troca repinta a tela toda
    twinkleHue = (twinkleHue + 12) % 360;
    K[0] = hsl565(twinkleHue, 40, 12); K[1] = hsl565(twinkleHue, 36, 22);
    K[2] = hsl565(twinkleHue, 85, 70); K[3] = hsl565(twinkleHue, 75, 94);
    overlay();
    dirtyAll();
  }
  if (pressed >= 0 && millis() - pressedAt >= 160) { int i = pressed; pressed = -1; drawBtn(i); }
}

void colorTest() {
  tft.fillRect(0, 0, 160, H, TFT_RED);
  tft.fillRect(160, 0, 160, H, TFT_GREEN);
  tft.fillRect(320, 0, 160, H, TFT_BLUE);
  delay(1200);
}

void setup() {
  Serial.setRxBufferSize(8192);
  Serial.begin(BAUD);
  prefs.begin("slime", false);
  slime = min<int>(prefs.getUChar("slime", 0), N_SLIMES - 1);
  tft.init();
  tft.setRotation(1);
  colorTest();
  tp.begin();
  tp.setRotation(ROTATION_NORMAL);
  eqS.setColorDepth(16); titS.setColorDepth(16); slS.setColorDepth(16);
  memcpy(K, THEMES[slime], sizeof(K));
  defaultLayout();
  Serial.println("HELLO");
}

void loop() {
  static uint32_t lastAnim = 0, lastSec = 0;
  readSerial();
  readTouch();
  uint32_t now = millis();
  if (now - lastSec >= 1000) {
    lastSec = now;
    if (playing && dur && pos < dur) { pos++; dProg = true; }
  }
  if (now - lastAnim >= 60) { lastAnim = now; animate(); }
  redraw();
}
