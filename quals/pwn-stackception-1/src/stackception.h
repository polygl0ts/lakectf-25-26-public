#ifndef STACKCEPTION_H
#define STACKCEPTION_H

#include <stddef.h>
#include <stdint.h>

#define PROGRAM_LENGTH  1024
#define STACK_DEPTH     512

#define unused          __attribute__((unused))
#define NUM_ELEMENTS(x) ((int)(sizeof(x) / sizeof((x)[0])))

typedef enum : uint32_t {
    /* Arithmetic */
    ADD,
    MUL,
    /* Load/Store */
    PUSH,
    POP, /* There's no registers, so a pop just discards the top of the stack */
    DUP,
    /* Control flow */
    JMP,
    CALL,
    RET,
    /* "syscalls" */
    READ,
    WRITE,
    EXIT,
#if defined(LEVEL) && LEVEL == 1
    WIN,
#endif
} insns_e;

typedef struct __attribute__((packed)) {
    insns_e  opcode;
    uint32_t imm_arg;
} instruction_s;

#endif /* STACKCEPTION_H */
