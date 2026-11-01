// Mock do TAMC_GT911: o painel nunca é tocado no harness.
#pragma once
#include <Arduino.h>

#define ROTATION_NORMAL 0

class TAMC_GT911 {
 public:
  struct Point {
    int16_t x, y;
  };

  TAMC_GT911(int, int, int, int, int, int) {}
  void begin() {}
  void setRotation(uint8_t) {}
  void read() {}

  bool isTouched = false;
  Point points[5] = {};
};
