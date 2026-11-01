// Mock do Arduino core para compilar firmware/src/main.cpp no PC (harness de teste visual).
// Cobre só a API que o sketch usa. Detalhes e limites: firmware/host/NOTAS.md.
#pragma once
#include <ctype.h>
#include <math.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <deque>
#include <string>
#include <type_traits>
#include <utility>

#define PROGMEM
#define pgm_read_word(addr) (*(const uint16_t*)(addr))

// Como no core: min/max/constrain tipados. O sketch chama min<int>(...) e constrain(x, lo, hi) com tipos mistos.
template <typename T>
constexpr T min(T a, T b) { return b < a ? b : a; }
template <typename T>
constexpr T max(T a, T b) { return a < b ? b : a; }
template <typename T, typename L, typename H>
constexpr auto constrain(T v, L lo, H hi) {
  using C = std::common_type_t<T, L, H>;
  if (static_cast<C>(v) < static_cast<C>(lo)) return static_cast<C>(lo);
  if (static_cast<C>(v) > static_cast<C>(hi)) return static_cast<C>(hi);
  return static_cast<C>(v);
}

// String do Arduino sobre std::string. Índice fora da faixa: operator[] devolve 0; substring segue o core.
class String {
 public:
  static constexpr unsigned int npos = ~0u;

  String() = default;
  String(const char* s) : s_(s ? s : "") {}
  explicit String(std::string s) : s_(std::move(s)) {}

  unsigned int length() const { return static_cast<unsigned int>(s_.size()); }
  bool isEmpty() const { return s_.empty(); }
  char operator[](unsigned int i) const { return i < s_.size() ? s_[i] : '\0'; }
  const char* c_str() const { return s_.c_str(); }

  int indexOf(char c, unsigned int from = 0) const {
    if (from >= s_.size()) return -1;
    size_t p = s_.find(c, from);
    return p == std::string::npos ? -1 : static_cast<int>(p);
  }

  String substring(unsigned int left, unsigned int right = npos) const {
    if (left > right) std::swap(left, right);
    if (left > length()) return String();
    if (right > length()) right = length();
    return String(s_.substr(left, right - left));
  }

  long toInt() const { return atol(s_.c_str()); }
  void toUpperCase() {
    for (char& c : s_) c = static_cast<char>(toupper(static_cast<unsigned char>(c)));
  }
  void trim() {
    size_t b = s_.find_first_not_of(" \t\r\n");
    if (b == std::string::npos) { s_.clear(); return; }
    size_t e = s_.find_last_not_of(" \t\r\n");
    s_ = s_.substr(b, e - b + 1);
  }
  void toCharArray(char* buf, unsigned int size) const {
    if (!buf || size == 0) return;
    size_t n = s_.size() < size - 1 ? s_.size() : size - 1;
    memcpy(buf, s_.data(), n);
    buf[n] = '\0';
  }

  String& operator+=(char c) { s_ += c; return *this; }
  String& operator+=(const char* c) { s_ += c; return *this; }
  String& operator+=(const String& o) { s_ += o.s_; return *this; }
  friend bool operator==(const String& a, const String& b) { return a.s_ == b.s_; }
  friend bool operator!=(const String& a, const String& b) { return !(a == b); }
  friend String operator+(const char* a, const String& b) { return String(std::string(a) + b.s_); }

 private:
  std::string s_;
};

// Serial: a entrada é alimentada pelo harness (bytes que o PC mandaria); a saída vai para stdout.
class HardwareSerial {
 public:
  void setRxBufferSize(size_t) {}
  void begin(unsigned long) {}
  int available() const { return static_cast<int>(rx_.size()); }
  int read() {
    if (rx_.empty()) return -1;
    int c = rx_.front();
    rx_.pop_front();
    return c;
  }
  size_t readBytes(uint8_t* buf, size_t n) {
    size_t k = 0;
    while (k < n && !rx_.empty()) {
      buf[k++] = rx_.front();
      rx_.pop_front();
    }
    return k;
  }
  void println(const char* s) { printf("%s\n", s); }
  void printf(const char* fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    vprintf(fmt, ap);
    va_end(ap);
  }
  void feed(const std::string& bytes) { rx_.insert(rx_.end(), bytes.begin(), bytes.end()); }

 private:
  std::deque<uint8_t> rx_;
};
inline HardwareSerial Serial;

// Relógio falso: começa em 5000 ms e só anda com delay() ou com o harness (@wait).
inline uint32_t g_fake_ms = 5000;
inline uint32_t millis() { return g_fake_ms; }
inline void delay(uint32_t ms) { g_fake_ms += ms; }

// PWM da luz de fundo: só guarda o último duty para o harness reportar.
inline uint32_t g_backlight_duty = 0;
inline bool ledcAttach(uint8_t, uint32_t, uint8_t) { return true; }
inline void ledcWrite(uint8_t, uint32_t duty) { g_backlight_duty = duty; }

// Valores fixos: o harness não modela heap real (ver NOTAS.md).
struct EspClass {
  uint32_t getFreeHeap() const { return 200000; }
  uint32_t getMaxAllocHeap() const { return 100000; }
};
inline EspClass ESP;
