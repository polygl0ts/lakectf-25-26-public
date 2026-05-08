#include <stdio.h>
#include <string.h>
#include <stdlib.h>

void check(char* password) {
  if (strcmp(password, "password") == 0) {
    printf("Access granted!\n");
  } else {
    throw -1;
  }
}

int main(int arc, char** argv) {
  try {
    if (arc != 2) {
      printf("Usage: %s <password>\n", argv[0]);
      return 1;
    }
    check(argv[1]);
  } catch (int e) {
    printf("Access denied!\n");
    return 0;
  }
  return 0;
}
