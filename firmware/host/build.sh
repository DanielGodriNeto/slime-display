#!/usr/bin/env bash
# Compila o harness nativo (Windows, MinGW g++). Não modifica firmware/src.
# Uso: firmware/host/build.sh   (CXX=/caminho/g++ para trocar o compilador)
set -euo pipefail
cd "$(dirname "$0")/.."   # firmware/
CXX="${CXX:-g++}"
"$CXX" -std=c++17 -O1 -Wall -Wextra -Wno-unused-parameter -Wno-sign-compare \
  -I host/include -I src \
  host/main_host.cpp -o host/slime_host.exe
echo "build ok: $(pwd)/host/slime_host.exe"
