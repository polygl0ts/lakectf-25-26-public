#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>

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
      ERR("You fumble with your handgun for far too long.");
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
    ERR("You fumble with your handgun for far too long.");
    exit(1);
  }
  return hex_string_to_int(buffer, am);
}

void shoot() {
  PROMPT("X coordinate: ");
  uint8_t* addr = (uint8_t*)take_coord(15);

  PROMPT("Y coordinate: ");
  uint8_t bitidx = take_coord(4);

  // shoot
  *addr = (*addr) ^ (1 << bitidx);
}

void leak() {
  uint64_t libc = (uint64_t)&read;
  uint64_t ld = *(uint64_t*)(libc - 0xfd340 + 0x1d9f88);
  write(1, &libc, 8);
  write(1, "\n", 1);
  write(1, &ld, 8);
  write(1, "\n", 1);
}

int main() {
  NARRATE("You run down the stairs. The sniper rifle was too heavy to carry "
          "with you.\n"
          "You hold your Colt 1911 in your hands. Eight bullets in the "
          "magazine and one\n"
          "in the firing chamber.")
  NARRATE("You haven't encountered anyone yet, but you know it's inevitable.")
  NARRATE("On your way down the stairs, you pass next to cameras and wiring "
          "in the walls.\n"
          "You feel the call of The Wired.\n"
          "Your head starts hurting.\n"
          "You start seeing weird symbols.")

  leak();

  NARRATE("They are not in any human language, but you know what they mean.")
  NARRATE("*footsteps* ")
  NARRATE("Agents start flooding your vision, you instinctively point the gun "
          "and start pulling the trigger.")

  shoot();
  SEND_MSG("One.");
  shoot();
  SEND_MSG("Two.");
  shoot();
  SEND_MSG("Three.");
  shoot();
  SEND_MSG("Four.");
  shoot();
  SEND_MSG("Five.");
  shoot();
  SEND_MSG("Six.");
  shoot();
  SEND_MSG("Seven.");
  shoot();
  SEND_MSG("Eight.");
  shoot();
  SEND_MSG("Nine.");

  SEND_MSG("\nYou exit the building ");
  exit(42);
}
