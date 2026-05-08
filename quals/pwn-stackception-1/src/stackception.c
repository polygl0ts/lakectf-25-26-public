#include "stackception.h"

#include <stdio.h>
#include <stdlib.h>

#ifndef LEVEL
#error "LEVEL not defined"
#endif

int main(int argc, char* argv[]) {
    static_assert(sizeof(instruction_s) == 8,
                  "instruction_s size is not 8 bytes");

    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);

    if (argc < 2) {
        fprintf(stderr, "Usage: %s <bytecode_file>\n", argv[0]);
        return EXIT_FAILURE;
    }

    instruction_s program[PROGRAM_LENGTH] = {0};
    int           pc                      = 0;
    uint32_t      stack[STACK_DEPTH]      = {0};
    int           sp                      = 0;
    uint32_t      call_stack[STACK_DEPTH] = {0};
    int           csp                     = 0;

    /* Read in program */
    FILE* program_file                    = fopen(argv[1], "rb");
    if (!program_file) {
        fprintf(stderr, "[ERROR] Failed to open file: %s\n", argv[1]);
        return EXIT_FAILURE;
    }

    for (size_t i = 0; i < NUM_ELEMENTS(program); i++) {
        if (fread(&program[i], sizeof(instruction_s), 1, program_file) != 1) {
#ifndef NDEBUG
            fprintf(stderr, "[DEBUG] Read in %zu instructions\n", i);
#endif
            break;
        }
    }
    fclose(program_file);

    /* Execute program */
    while (1) {
        if (pc >= NUM_ELEMENTS(program)) {
            fprintf(stderr, "[ERROR] Program counter out of bounds: %d\n", pc);
            return EXIT_FAILURE;
        }
#ifndef NDEBUG
        fprintf(stderr, "[DEBUG] Fetching insn@%p\n", (void*)(program + pc));
#endif
        instruction_s* insn = &program[pc++];
#ifndef NDEBUG
        fprintf(stderr, "[DEBUG] pc=%d sp=%d opcode=%u imm_arg=0x%08x\n",
                pc - 1, sp, insn->opcode, insn->imm_arg);
#endif
        switch (insn->opcode) {
            /* Arithmetic */
            case ADD: {
                if (sp < 2) {
                    fprintf(stderr, "[ERROR] Stack underflow on ADD\n");
                    return EXIT_FAILURE;
                }
                uint32_t a  = stack[--sp];
                uint32_t b  = stack[--sp];
                stack[sp++] = a + b;
#ifndef NDEBUG
                fprintf(stderr, "[DEBUG] ADD: %u + %u = %u\n", b, a, a + b);
#endif
                break;
            }
            case MUL: {
                if (sp < 2) {
                    fprintf(stderr, "[ERROR] Stack underflow on MUL\n");
                    return EXIT_FAILURE;
                }
                uint32_t a  = stack[--sp];
                uint32_t b  = stack[--sp];
                stack[sp++] = a * b;
#ifndef NDEBUG
                fprintf(stderr, "[DEBUG] MUL: %u * %u = %u\n", b, a, a * b);
#endif
                break;
            }
            /* Load/Store */
            case PUSH: {
                /* Bug: stack overflow check is missing
                 * if (sp >= NUM_ELEMENTS(stack)) {
                 *     fprintf(stderr, "[ERROR] Stack overflow on PUSH\n");
                 *     return EXIT_FAILURE;
                 * }
                 */
                stack[sp++] = insn->imm_arg;
#ifndef NDEBUG
                fprintf(stderr, "[DEBUG] PUSH: 0x%08x\n", insn->imm_arg);
#endif
                break;
            }
            case POP: {
                /* Bug: stack underflow check is missing
                 * if (sp < 1) {
                 *     fprintf(stderr, "[ERROR] Stack underflow on POP\n");
                 *     return EXIT_FAILURE;
                 * }
                 */
#ifndef NDEBUG
                fprintf(stderr, "[DEBUG] POP: 0x%08x\n", stack[sp - 1]);
#endif
                sp--;
                break;
            }
            case DUP: {
                if (sp < 1) {
                    fprintf(stderr, "[ERROR] Stack underflow on DUP\n");
                    return EXIT_FAILURE;
                }
                if (sp >= NUM_ELEMENTS(stack)) {
                    fprintf(stderr, "[ERROR] Stack overflow on DUP\n");
                    return EXIT_FAILURE;
                }
                uint32_t val = stack[sp - 1];
                stack[sp++]  = val;
#ifndef NDEBUG
                fprintf(stderr, "[DEBUG] DUP: 0x%08x\n", val);
#endif
                break;
            }
            /* Control flow */
            case JMP: {
                /* Bug: jmp target not verified */
                uint32_t target = stack[--sp];
#ifndef NDEBUG
                fprintf(stderr, "[DEBUG] JMP: to %u\n", target);
#endif
                pc = target;
                break;
            }
            case CALL: {
                if (csp >= NUM_ELEMENTS(call_stack)) {
                    fprintf(stderr, "[ERROR] Call stack overflow on CALL\n");
                    return EXIT_FAILURE;
                }
                /* Bug: call target not verified */
                uint32_t target = stack[--sp];
#ifndef NDEBUG
                fprintf(stderr, "[DEBUG] CALL: to %u, return address %d\n",
                        target, pc);
#endif
                call_stack[csp++] = pc;
                pc                = target;
                break;
            }
            case RET: {
                if (csp < 1) {
                    fprintf(stderr, "[ERROR] Call stack underflow on RET\n");
                    return EXIT_FAILURE;
                }
                pc = call_stack[--csp];
#ifndef NDEBUG
                fprintf(stderr, "[DEBUG] RET: to %d\n", pc);
#endif
                break;
            }
            /* "syscalls" */
            case READ: {
                /* Bug: stack overflow check is missing
                 * if (sp >= NUM_ELEMENTS(stack)) {
                 *     fprintf(stderr, "[ERROR] Stack overflow on READ\n");
                 *     return EXIT_FAILURE;
                 * }
                 */
                uint32_t val = 0;
                if (fread(&val, sizeof(val), 1, stdin) != 1) {
                    fprintf(stderr,
                            "[ERROR] Failed to read from stdin on READ\n");
                    return EXIT_FAILURE;
                }
                stack[sp++] = val;
#ifndef NDEBUG
                fprintf(stderr, "[DEBUG] READ: 0x%08x\n", val);
#endif
                break;
            }
            case WRITE: {
                /* Bug: underflow check is unsigned */
                if ((unsigned int)sp < 1) {
                    fprintf(stderr, "[ERROR] Stack underflow on WRITE\n");
                    return EXIT_FAILURE;
                }
                uint32_t val = stack[--sp];
#ifndef NDEBUG
                fprintf(stderr, "[DEBUG] WRITE: 0x%08x\n", val);
#endif
                if (fwrite(&val, sizeof(uint32_t), 1, stdout) != 1) {
                    fprintf(stderr,
                            "[ERROR] Failed to write to stdout on WRITE\n");
                    return EXIT_FAILURE;
                }
                break;
            }
            case EXIT: {
                uint32_t retval = stack[--sp];
#ifndef NDEBUG
                fprintf(stderr, "[DEBUG] EXIT: %u\n", retval);
#endif
                return retval;
            }
#if LEVEL == 1
            case WIN: {
                FILE* flag_file = fopen("/app/flag.txt", "rb");
                if (!flag_file) {
                    fprintf(stderr, "[ERROR] Failed to open flag.txt\n");
                    return EXIT_FAILURE;
                }

                char   flag[128] = {0};
                size_t n         = fread(flag, 1, sizeof(flag) - 1, flag_file);
                flag[n]          = 0;
                fclose(flag_file);
                printf("Flag: %s\n", flag);
                return EXIT_SUCCESS;
            }
#endif
            default: {
                break;
            }
        }
    }

    return EXIT_SUCCESS;
}
