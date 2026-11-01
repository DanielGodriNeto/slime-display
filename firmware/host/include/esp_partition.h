// Mock da partição "photos" (flash): 8 vagas de 0x50000 bytes, carregadas de um .bin pelo harness.
#pragma once
#include <Arduino.h>

#include <algorithm>
#include <vector>

typedef int esp_err_t;
#define ESP_OK 0
#define ESP_ERR_INVALID_ARG (-1)

typedef uint8_t esp_partition_type_t;
typedef uint8_t esp_partition_subtype_t;
#define ESP_PARTITION_TYPE_DATA 1
enum esp_partition_mmap_memory_t { ESP_PARTITION_MMAP_DATA = 0 };
typedef uint32_t esp_partition_mmap_handle_t;

struct esp_partition_t {
  uint32_t address;
  uint32_t size;
  const char* label;
};

// Estado do harness: flash da partição (0xFF = apagada) e se a partição existe ("-" no harness = não existe).
inline bool g_photos_present = false;
inline std::vector<uint8_t> g_photo_flash;
inline const esp_partition_t g_photos_part = {0x170000, 0x280000, "photos"};
inline uint32_t g_next_mmap_handle = 1;

inline const esp_partition_t* esp_partition_find_first(esp_partition_type_t, esp_partition_subtype_t, const char* label) {
  if (!g_photos_present || strcmp(label, "photos") != 0) return nullptr;
  return &g_photos_part;
}

inline esp_err_t esp_partition_mmap(const esp_partition_t* part, uint32_t offset, uint32_t size,
                                    esp_partition_mmap_memory_t, const void** out, esp_partition_mmap_handle_t* handle) {
  if (static_cast<uint64_t>(offset) + size > part->size) return ESP_ERR_INVALID_ARG;
  *out = g_photo_flash.data() + offset;
  *handle = g_next_mmap_handle++;
  return ESP_OK;
}

inline void esp_partition_munmap(esp_partition_mmap_handle_t) {}

inline esp_err_t esp_partition_erase_range(const esp_partition_t* part, uint32_t offset, uint32_t size) {
  if (static_cast<uint64_t>(offset) + size > part->size) return ESP_ERR_INVALID_ARG;
  std::fill(g_photo_flash.begin() + offset, g_photo_flash.begin() + offset + size, uint8_t{0xFF});
  return ESP_OK;
}

inline esp_err_t esp_partition_write(const esp_partition_t* part, uint32_t offset, const void* src, size_t size) {
  if (static_cast<uint64_t>(offset) + size > part->size) return ESP_ERR_INVALID_ARG;
  memcpy(g_photo_flash.data() + offset, src, size);
  return ESP_OK;
}
