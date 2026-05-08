#include "snalloc.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

// clang-format off
#define check_eq(a,b)  do {if((a)!=(b)) printf("[FAILED] %s: " #a " == " #b ", a is %#zx, b is %#zx\n", __func__, (size_t)a, (size_t)b);} while(0);
#define check_neq(a,b) do {if((a)==(b)) printf("[FAILED] %s: " #a " != " #b ", a is %#zx, b is %#zx\n", __func__, (size_t)a, (size_t)b);} while(0);
#define check_leq(a,b) do {if((a) >(b)) printf("[FAILED] %s: " #a " <= " #b ", a is %#zx, b is %#zx\n", __func__, (size_t)a, (size_t)b);} while(0);
#define check_geq(a,b) do {if((a) <(b)) printf("[FAILED] %s: " #a " >= " #b ", a is %#zx, b is %#zx\n", __func__, (size_t)a, (size_t)b);} while(0);
#define check_lt(a,b)  do {if((a)>=(b)) printf("[FAILED] %s: " #a "  < " #b" , a is %#zx, b is %#zx\n", __func__, (size_t)a, (size_t)b);} while(0);
#define check_gt(a,b)  do {if((a)<=(b)) printf("[FAILED] %s: " #a "  > " #b" , a is %#zx, b is %#zx\n", __func__, (size_t)a, (size_t)b);} while(0);
// clang-format on

void test_types_and_macros() {
  check_eq(PAGE, 0x1000);
  check_eq(SNAB_EXTEND, 2);
  check_eq(SNAB_AUTO, 1);
  check_eq(SNAB_MAX_ORDER, 3);
  check_eq(SNAB_CHUNKS, 0x40);
  check_leq(sizeof(snab_t), 0x1000);
  check_eq(sizeof(bitmap_t) * 8, 0x40);
  check_eq(ORDER_2_SNAB_SZ(0), 0x2000);
  check_eq(ORDER_2_CHUNK_SZ(0), 0x40);
  check_eq(ORDER_2_SNAB_SZ(SNAB_MAX_ORDER), 0x5000);
  check_eq(ORDER_2_CHUNK_SZ(SNAB_MAX_ORDER), 0x100);
  check_eq(SNAB_MAGIC(0x13371337000), 0x13371337);
}

void test_clip_chunk_sizes() {
  uint64_t min_ck = 0;
  uint64_t max_ck = 0;
  check_eq(CHUNK_SZ_2_ORDER(0), 0);
  for (order_t order = 0; order <= SNAB_MAX_ORDER + 1; ++order) {
    min_ck = max_ck + 1;
    max_ck = ORDER_2_CHUNK_SZ(order);
    for (size_t ck = min_ck; ck <= max_ck; ++ck) {
      check_eq(CHUNK_SZ_2_ORDER(ck), order);
    }
  }
}

void test_fields_snab() {
  snab_t *snab = snab_alloc(2, 0, NULL);
  check_eq(((size_t)snab) & (PAGE - 1), 0);
  check_eq(snab->magic, ((size_t)snab >> 12));
  check_eq(snab->flags, 0);
  check_eq(snab->order, 2);
  check_eq(snab->bitmap, 0);
  check_eq(snab->prev, NULL);
  check_eq(snab->next, NULL);
}

void test_snalloc_snfree() {
  char *chunks[SNAB_CHUNKS + 1] = {NULL};
  char *chunks2[SNAB_CHUNKS + 1] = {NULL};
  snab_t *snab = NULL;
  snab_t *snab_next = NULL;
  size_t size = 0x78;
  for (size_t i = 0; i < SNAB_CHUNKS; ++i) {
    chunks[i] = snalloc(size);
  }
  snab = get_snab_from_chunk(chunks[0]);
  check_eq(snab_chunk_idx_get(snab, chunks[0]), 0);
  for (size_t i = 1; i < SNAB_CHUNKS; ++i) {
    check_eq(get_snab_from_chunk(chunks[i]), snab);
    check_eq(snab_chunk_idx_get(snab, chunks[i]), i);
  }
  check_eq(((size_t)snab) & (PAGE - 1), 0);
  check_eq(snab->magic, ((size_t)snab >> 12));
  check_eq(snab->flags, SNAB_EXTEND);
  check_eq(snab->order, 1);
  check_eq(snab->bitmap, -1ULL);
  check_eq((size_t)snab + PAGE, (size_t)chunks[0]);
  snfree(chunks[3]);
  snfree(chunks[0x3f]);
  snfree(chunks[0x20]);
  check_eq(snab->bitmap,
           0b0111111111111111111111111111111011111111111111111111111111110111);
  chunks2[0] = snalloc(size);
  chunks2[1] = snalloc(size);
  chunks2[2] = snalloc(size);
  check_eq(chunks2[0], chunks[3]);
  check_eq(chunks2[1], chunks[0x20]);
  check_eq(chunks2[2], chunks[0x3f]);
  chunks[SNAB_CHUNKS] = snalloc(size);
  snab_next = get_snab_from_chunk(chunks[SNAB_CHUNKS]);
  check_eq(snab->prev, NULL);
  check_eq(snab->next, snab_next);
  check_eq(snab_next->prev, snab);
  check_eq(snab_next->next, NULL);
  check_eq(snab_next->bitmap, 0b1);
  snfree(chunks[SNAB_CHUNKS]);
  check_eq(snab->prev, NULL);
  check_eq(snab->next, NULL);
}

int main(int argc, char **argv) {
  test_types_and_macros();
  test_fields_snab();
  test_clip_chunk_sizes();
  test_fields_snab();
  test_snalloc_snfree();
  return 0;
}
