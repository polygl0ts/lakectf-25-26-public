#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>

#include "stackception.h"

#define MAX_LABELS       256
#define MAX_LABEL_LEN    64
#define MAX_INSTRUCTIONS PROGRAM_LENGTH

typedef struct {
    char   name[MAX_LABEL_LEN];
    size_t address;
} label_s;

static label_s labels[MAX_LABELS] = {0};
static size_t  num_labels = 0;

static void add_label(const char* name, size_t address) {
    if (num_labels >= MAX_LABELS) {
        fprintf(stderr, "Error: Too many labels\n");
        exit(EXIT_FAILURE);
    }
    strncpy(labels[num_labels].name, name, MAX_LABEL_LEN - 1);
    labels[num_labels].name[MAX_LABEL_LEN - 1] = '\0';
    labels[num_labels].address                 = address;
    num_labels++;
}

static int find_label(const char* name, size_t* address) {
    for (size_t i = 0; i < num_labels; i++) {
        if (strcmp(labels[i].name, name) == 0) {
            *address = labels[i].address;
            return 1;
        }
    }
    return 0;
}

static char* trim(char* str) {
    while (isspace((unsigned char)*str)) str++;
    if (*str == 0) {
        return str;
    }
    char* end = str + strlen(str) - 1;
    while (end > str && isspace((unsigned char)*end)) end--;
    end[1] = '\0';
    return str;
}

static uint32_t parse_immediate(const char* str) {
    if (str[0] == '"') {
        /* String literal */
        size_t len = strlen(str);
        if (len < 2 || str[len - 1] != '"') {
            fprintf(stderr, "Error: Malformed string literal: %s\n", str);
            exit(EXIT_FAILURE);
        }
        const char* start   = str + 1;
        size_t      str_len = len - 2;
        uint32_t    val     = 0;
        for (size_t i = 0; i < str_len && i < 4; i++) {
            val |= ((uint32_t)(unsigned char)start[i]) << (i * 8);
        }
        return val;
    } else if (str[0] == '0' && (str[1] == 'x' || str[1] == 'X')) {
        /* Hex number */
        return (uint32_t)strtoul(str, NULL, 16);
    } else {
        /* Decimal number */
        return (uint32_t)strtoul(str, NULL, 10);
    }
}

static insns_e parse_opcode(const char* str) {
    if (strcasecmp(str, "add") == 0) {
        return ADD;
    }
    if (strcasecmp(str, "mul") == 0) {
        return MUL;
    }
    if (strcasecmp(str, "push") == 0) {
        return PUSH;
    }
    if (strcasecmp(str, "pop") == 0) {
        return POP;
    }
    if (strcasecmp(str, "dup") == 0) {
        return DUP;
    }
    if (strcasecmp(str, "jmp") == 0) {
        return JMP;
    }
    if (strcasecmp(str, "call") == 0) {
        return CALL;
    }
    if (strcasecmp(str, "ret") == 0) {
        return RET;
    }
    if (strcasecmp(str, "read") == 0) {
        return READ;
    }
    if (strcasecmp(str, "write") == 0) {
        return WRITE;
    }
    if (strcasecmp(str, "exit") == 0) {
        return EXIT;
    }

    fprintf(stderr, "Error: Unknown opcode: %s\n", str);
    exit(EXIT_FAILURE);
}

int main(int argc, char* argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <input.asm> <output.bin>\n", argv[0]);
        return EXIT_FAILURE;
    }

    FILE* input = fopen(argv[1], "r");
    if (!input) {
        fprintf(stderr, "Error: Cannot open input file %s\n", argv[1]);
        return EXIT_FAILURE;
    }

    instruction_s program[MAX_INSTRUCTIONS] = {0};
    size_t        num_instructions          = 0;

    char   line[256]                        = {0};
    size_t line_num                         = 0;

    /* First pass: collect labels */
    while (fgets(line, sizeof(line), input)) {
        line_num++;
        char* trimmed = trim(line);
        if (trimmed[0] == '\0' || trimmed[0] == '#' || trimmed[0] == ';') {
            continue;
        }

        size_t len = strlen(trimmed);
        if (trimmed[len - 1] == ':') {
            trimmed[len - 1] = '\0';
            add_label(trimmed, num_instructions);
        } else {
            char opcode_str[32] = {0};
            char arg_str[256]   = {0};
            sscanf(trimmed, "%31s %255[^\n]", opcode_str, arg_str);
            insns_e opcode = parse_opcode(opcode_str);
            num_instructions++;
            if ((opcode == CALL || opcode == JMP) && arg_str[0] != '\0') {
                num_instructions++;
            }
        }
    }

    /* Reset for second pass */
    rewind(input);
    num_instructions = 0;
    line_num         = 0;

    /* Second pass: assemble instructions */
    while (fgets(line, sizeof(line), input)) {
        line_num++;
        char* trimmed = trim(line);
        if (trimmed[0] == '\0' || trimmed[0] == '#' || trimmed[0] == ';') {
            continue;
        }

        size_t len = strlen(trimmed);
        if (trimmed[len - 1] == ':') {
            /* Label */
            continue;
        }

        if (num_instructions >= MAX_INSTRUCTIONS) {
            fprintf(stderr, "Error: Too many instructions\n");
            fclose(input);
            return EXIT_FAILURE;
        }

        char opcode_str[32] = {0};
        char arg_str[256]   = {0};

        sscanf(trimmed, "%31s %255[^\n]", opcode_str, arg_str);

        instruction_s insn = {0};
        insn.opcode        = parse_opcode(opcode_str);
        insn.imm_arg       = 0;

        if (insn.opcode == PUSH) {
            if (arg_str[0] == '\0') {
                fprintf(stderr,
                        "Error: PUSH requires an argument at line %zu\n",
                        line_num);
                fclose(input);
                return EXIT_FAILURE;
            }
            char* arg = trim(arg_str);
            /* Check if it's a label reference */
            size_t label_addr;
            if (find_label(arg, &label_addr)) {
                insn.imm_arg = label_addr;
            } else {
                insn.imm_arg = parse_immediate(arg);
            }
        } else if (insn.opcode == CALL || insn.opcode == JMP) {
            if (arg_str[0] != '\0') {
                char* arg = trim(arg_str);
                size_t label_addr;
                if (!find_label(arg, &label_addr)) {
                    fprintf(stderr, "Error: Undefined label '%s' at line %zu\n",
                            arg, line_num);
                    fclose(input);
                    return EXIT_FAILURE;
                }
                instruction_s push_insn = {0};
                push_insn.opcode = PUSH;
                push_insn.imm_arg = label_addr;
                program[num_instructions++] = push_insn;
            }
        }

        program[num_instructions++] = insn;
    }

    fclose(input);

    /* Write binary output */
    FILE* output = fopen(argv[2], "wb");
    if (!output) {
        fprintf(stderr, "Error: Cannot open output file %s\n", argv[2]);
        return EXIT_FAILURE;
    }

    for (size_t i = 0; i < num_instructions; i++) {
        if (fwrite(&program[i], sizeof(instruction_s), 1, output) != 1) {
            fprintf(stderr, "Error: Failed to write instruction %zu\n", i);
            fclose(output);
            return EXIT_FAILURE;
        }
    }

    fclose(output);
    return EXIT_SUCCESS;
}
