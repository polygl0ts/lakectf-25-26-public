CC := gcc
CFLAGS := -Wall -Wextra -O2 -s
LDFLAGS :=
TARGET := chal
SRC := main.c

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) $(SRC) -o $@ $(LDFLAGS)

clean:
	rm -f $(TARGET)
