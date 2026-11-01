// Mock do Preferences (NVS) em memória. No harness começa vazio a cada execução.
#pragma once
#include <Arduino.h>

#include <map>
#include <string>

class Preferences {
 public:
  bool begin(const char*, bool) { return true; }
  uint8_t getUChar(const char* key, uint8_t def) const {
    auto it = store_.find(key);
    return it == store_.end() ? def : it->second;
  }
  size_t putUChar(const char* key, uint8_t value) {
    store_[key] = value;
    return 1;
  }

 private:
  std::map<std::string, uint8_t> store_;
};
