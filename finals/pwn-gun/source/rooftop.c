#include <fcntl.h>
#include <stdint.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h>
#include "ascii_art.h"

#define SEND_MSG(MSG)                                                          \
  if (write(1, MSG, sizeof(MSG) - 1) == -1) {                                  \
    exit(1);                                                                   \
  }

#define NORMAL_COLOR "\033[0m"
#define LIGHT_BLUE_COLOR "\033[94m"

#define PROMPT(MSG) SEND_MSG(LIGHT_BLUE_COLOR MSG NORMAL_COLOR)

#define NARRATE(MSG)                                                           \
  SEND_MSG(MSG ">") {                                                          \
    char a;                                                                    \
    if (read(0, &a, 1) != 1) {                                                 \
      exit(1);                                                                 \
    }                                                                          \
  }

#define ERR(MSG) SEND_MSG("\033[38;5;196m" MSG NORMAL_COLOR)

#define SEND_ART(art_arr, art_caption)                                         \
  if (write(1, art_arr, sizeof(art_arr)) == -1) {                              \
    exit(1);                                                                   \
  }                                                                            \
  NARRATE(art_caption)

uint64_t hex_string_to_int(char* buffer, int len) {
  uint64_t num = 0;
  int idx = 0;

  if (buffer[len - 1] == '\n') {
    len--;
  }
  if (buffer[0] == '0' && (buffer[1] == 'x' || buffer[1] == 'X')) {
    idx = 2;
  }

  while (idx < len) {
    if (buffer[idx] >= '0' && buffer[idx] <= '9') {
      num = num * 0x10 + (buffer[idx] - '0');
    } else if (buffer[idx] >= 'A' && buffer[idx] <= 'F') {
      num = num * 0x10 + (buffer[idx] - 'A' + 10);
    } else if (buffer[idx] >= 'a' && buffer[idx] <= 'f') {
      num = num * 0x10 + (buffer[idx] - 'a' + 10);
    } else {
      ERR("You fumble with your rifle for far too long. They arrive.");
      exit(1);
    }

    idx++;
  }

  return num;
}

uint64_t take_coord(int len) {
  char buffer[0x40] = {};
  int am = read(0, buffer, len);
  if (am <= 0) {
    ERR("You fumble with your rifle for far too long. They arrive.");
    exit(1);
  }
  return hex_string_to_int(buffer, am);
}

int main() {
  NARRATE("** They keep following me. I cannot get away no matter how far I run. ** ");
  NARRATE("Their car is parked in front of the building.");
  SEND_ART(rooftop_ascii, "                              |  THE ROOFTOP  |                                                       \n");
  NARRATE("It is windy outside.");
  NARRATE("You take your position on the rooftop and set up your sniper rifle "
          "on the roofs edge.");
  NARRATE("You take a deep sigh and look through the scope.");
  SEND_ART(scope_ascii, "                                                                      |  TAKE AIM  |                                          \n")

  int fd = open("/tmp/libc.so.6", O_RDWR);
  if (fd < 0) {
    ERR("You dropped your rifle from the rooftop.")
    exit(1);
  }
  uint8_t* libc_mapping =
      mmap(0, 0x200000, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
  if (libc_mapping == 0) {
    ERR("You forgot your scope at home.");
    exit(1);
  }

  PROMPT("X coordinate: ");
  uint64_t offset = take_coord(9);

  PROMPT("Y coordinate: ");
  uint8_t bitidx = take_coord(4);

  NARRATE("      SHOOT?     \n");

  if (offset >= 0x200000) {
    ERR("You miss completely.");
    exit(1);
  }

  // shoot
  *(libc_mapping + offset) = (*(libc_mapping + offset)) ^ (1 << bitidx);

  // flush changes to disk
  if (munmap(libc_mapping, 0x200000) == -1) {
    ERR("They duck last second.");
    exit(1);
  }
  close(fd);

  NARRATE("\nThe gun shoots with ungodly force. Your whole body feels shaken, "
          "your ears ringing.\n"
          "The gas tank of the car is pierced - the car explodes.\n"
          "You felt a slight crack in reality.");
  NARRATE("Four more cars immediately arrive to the ground floor of the "
          "building.\n"
          "Men in black exit the vehicles and start rushing inside.");
  NARRATE("...");
  NARRATE("You run for the stairs. If they block your only exit you are done "
          "for.\n"
          "           \\\\  ENTERING THE STAIRWELL  \\\\\n");

  execve("./stairwell", NULL, NULL);
}
