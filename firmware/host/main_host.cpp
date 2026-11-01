// Harness nativo: compila firmware/src/main.cpp sem alterá-lo, com os mocks de firmware/host/include.
// Uso: slime_host.exe <photos.bin|-> <script.txt> <saida.ppm>
//   script: uma linha = um comando serial da placa (S, N, V, E, T, K, L ...); "@wait <ms>" avança o relógio
//   falso (loop() a cada 10 ms); linhas com # no início e linhas vazias são ignoradas.
#include "../src/main.cpp"

#include <cstring>
#include <fstream>
#include <iterator>
#include <string>
#include <vector>

namespace {

constexpr uint32_t kTickMs = 10;

bool loadPhotos(const char* path) {
  std::ifstream f(path, std::ios::binary);
  if (!f) {
    fprintf(stderr, "nao consegui abrir %s\n", path);
    return false;
  }
  std::vector<uint8_t> data((std::istreambuf_iterator<char>(f)), std::istreambuf_iterator<char>());
  if (data.size() > g_photos_part.size) {
    fprintf(stderr, "%s maior que a particao photos (%u bytes)\n", path, g_photos_part.size);
    return false;
  }
  data.resize(g_photos_part.size, 0xFF);  // resto da flash apagada
  g_photo_flash = std::move(data);
  g_photos_present = true;
  return true;
}

void advanceClock(uint32_t ms) {
  while (ms > 0) {
    uint32_t step = min<uint32_t>(ms, kTickMs);
    g_fake_ms += step;
    loop();
    ms -= step;
  }
}

// Devolve false se a linha não for um comando válido.
bool runLine(const std::string& line) {
  const std::string wait = "@wait ";
  if (line.compare(0, wait.size(), wait) == 0) {
    char* end = nullptr;
    unsigned long ms = strtoul(line.c_str() + wait.size(), &end, 10);
    if (end == line.c_str() + wait.size() || *end != '\0') return false;
    advanceClock(static_cast<uint32_t>(ms));
    return true;
  }
  if (line[0] == '@') return false;
  Serial.feed(line + "\n");  // o que o PC mandaria pela serial
  loop();                    // a placa lê a linha e redesenha
  return true;
}

// PPM P6 com RGB888 a partir da cor RGB565 lógica (expansão com replicação dos bits altos).
bool writePpm(const char* path) {
  FILE* f = fopen(path, "wb");
  if (!f) return false;
  fprintf(f, "P6\n%d %d\n255\n", W, H);
  const uint16_t* fb = tft.framebuffer();
  std::vector<uint8_t> rgb(static_cast<size_t>(W) * H * 3);
  for (size_t i = 0; i < static_cast<size_t>(W) * H; ++i) {
    uint16_t c = fb[i];
    uint8_t r = (c >> 11) & 0x1F, g = (c >> 5) & 0x3F, b = c & 0x1F;
    rgb[i * 3 + 0] = static_cast<uint8_t>((r << 3) | (r >> 2));
    rgb[i * 3 + 1] = static_cast<uint8_t>((g << 2) | (g >> 4));
    rgb[i * 3 + 2] = static_cast<uint8_t>((b << 3) | (b >> 2));
  }
  bool ok = fwrite(rgb.data(), 1, rgb.size(), f) == rgb.size();
  return fclose(f) == 0 && ok;
}

}  // namespace

int main(int argc, char** argv) {
  if (argc != 4) {
    fprintf(stderr, "uso: %s <photos.bin|-> <script.txt> <saida.ppm>\n", argv[0]);
    return 2;
  }
  if (std::strcmp(argv[1], "-") != 0 && !loadPhotos(argv[1])) return 1;

  std::ifstream script(argv[2]);
  if (!script) {
    fprintf(stderr, "nao consegui abrir o script %s\n", argv[2]);
    return 1;
  }

  setup();
  std::string line;
  int lineNo = 0;
  while (std::getline(script, line)) {
    ++lineNo;
    if (!line.empty() && line.back() == '\r') line.pop_back();
    if (line.empty() || line[0] == '#') continue;
    if (!runLine(line)) {
      fprintf(stderr, "linha %d invalida: %s\n", lineNo, line.c_str());
      return 1;
    }
  }
  for (int i = 0; i < 5; ++i) loop();  // estabiliza: o último redraw completo

  if (!writePpm(argv[3])) {
    fprintf(stderr, "nao consegui gravar %s\n", argv[3]);
    return 1;
  }
  fprintf(stderr, "ok: %s (backlight duty=%u, tela %s)\n", argv[3], g_backlight_duty,
          screenOff() ? "apagada pelo timeout (o framebuffer foi renderizado mesmo assim)" : "acesa");
  return 0;
}
