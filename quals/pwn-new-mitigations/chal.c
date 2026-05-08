#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void init() {
  setvbuf(stdin, 0, 2, 0);
  setvbuf(stdout, 0, 2, 0);
  setvbuf(stderr, 0, 2, 0);
}

void menu() {
  puts("1. Allocate chunk");
  puts("2. View chunk");
  puts("3. Free chunk");
  puts("4. Edit chunk");
  puts("5. Exit");
  printf("> ");
}

#define NCHUNKS (2)

char* chunks[NCHUNKS];
size_t sizes[NCHUNKS];
int nops = 9;

uint32_t get_index() {
  uint32_t idx = 0;

  printf("idx?: ");
  scanf("%d", &idx);
  assert(0 <= idx && idx < NCHUNKS);
  return idx;
}

void allocate() {
  uint32_t idx = get_index();
  size_t size = 0;
  printf("size?: ");
  scanf("%zd", &size);

  chunks[idx] = malloc(size);
  sizes[idx] = size;

  printf("data?: ");
  read(0, chunks[idx], size);
}

void view() {
  uint32_t idx = get_index();
  printf("meow: ");
  write(1, chunks[idx], sizes[idx]);
}

void edit() {
  uint32_t idx = get_index();

  printf("new data?: ");
  read(0, chunks[idx], sizes[idx]);
}

void del() {
  uint32_t idx = get_index();
  free(chunks[idx]);
}

int main() {
  init();

  puts("I know you've been delaying checking out the new patch notes.");

  int option;

  while (1) {
    menu();
    scanf("%d", &option);

    assert(nops > 0 && "Did you forget to massage it first?");

    switch (option) {
    case 1:
      allocate();
      break;
    case 2:
      view();
      break;
    case 3:
      del();
      break;
    case 4:
      edit();
      break;
    case 5:
    default:
      exit(1);
    }
    nops--;
  }
}
