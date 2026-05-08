#!/usr/bin/env python3
import os
import random
import sys
import subprocess
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


# ============================================================
# 1. KILLER SUDOKU DATA
# ============================================================

sudoku_grid = [
    1, 2, 3, 3, 3, 4, 5, 6, 6, 2, 2, 7, 8, 8, 4, 9, 9, 10,
    11,12,7, 13,13,13,14,14,10, 11,12,7, 7, 15,15,16,17,17,
    11,18,19,20,20,16,16,23,23, 18,18,19,20,21,21,22,22,22,
    24,24,25,26,27,27,28,29,22, 30,30,25,26,27,28,28,29,34,
    31,31,32,32,32,28,33,33,34
]

sudoku_sums = [
    6, 18, 10, 11, 7, 10, 21, 14, 6, 8, 10, 11, 13, 14, 8, 18, 10,
    16, 6, 16, 11, 16, 14, 7, 15, 15, 12, 15, 12, 7, 15, 8, 8, 17
]

SUDOKU_SOLVE_STR = "683254791915687243427913865598162437132479586764538912256891374349726158871345629"
assert len(SUDOKU_SOLVE_STR) == 81
sudoku_solve_bytes = [ord(c) for c in SUDOKU_SOLVE_STR]

flag = b"EPFL{v4ult_unl0ck3d_n0w_r3v3rs3_th3_m4tr1x_4_43s!}"


# ============================================================
# 2. AES MATERIAL FOR FINAL STAGE
# ============================================================

def ror8(val, shift):
    return ((val >> shift) | (val << (8 - shift))) & 0xFF

aes_key = os.urandom(32)
aes_iv = os.urandom(16)
cipher = AES.new(aes_key, AES.MODE_CBC, aes_iv)
ciphertext = cipher.encrypt(pad(flag, 16))
full_payload = aes_iv + ciphertext

def derive_stage3_material(key_bytes):
    acc = [(0x31 + 11 * i) & 0xFF for i in range(32)]
    for i, b in enumerate(key_bytes):
        a = i % 32
        c = (i * 7 + 3) % 32
        d = (i * 13 + 11) % 32

        acc[a] ^= b
        acc[a] = (acc[a] + ((17 * i) ^ b)) & 0xFF

        acc[c] = ((acc[c] << 1) | (acc[c] >> 7)) & 0xFF
        acc[c] ^= (b + i) & 0xFF

        rot = i & 7
        mixed = b if rot == 0 else (((b << rot) | (b >> (8 - rot))) & 0xFF)
        acc[d] = (acc[d] + mixed) & 0xFF

    return acc

stage3_material = derive_stage3_material(sudoku_solve_bytes)
secret_matrix = []
for i in range(32):
    secret_matrix.append(aes_key[i] ^ stage3_material[i])

c_matrix = ", ".join(f"0x{b:02x}" for b in secret_matrix)
c_payload = ", ".join(f"0x{b:02x}" for b in full_payload)
STAGE3_FRAGMENT_COUNT = 4
STAGE3_FRAGMENT_ORDER = list(range(STAGE3_FRAGMENT_COUNT))
random.SystemRandom().shuffle(STAGE3_FRAGMENT_ORDER)


# ============================================================
# 3. POLYMORPHIC VM BYTECODE BUILDER
# ============================================================

bytecode = bytearray()

def emit(thread_key, op, *args):
    bytecode.append(op ^ thread_key)
    bytecode.extend(args)

# --- opcodes ---
OP_LOAD_IMM = 0x01   # [op][dst][hi][lo]
OP_LOAD_INP = 0x02   # [op][dst][idx]
OP_MOV      = 0x03   # [op][dst][src]
OP_ADD      = 0x04   # [op][dst][src]
OP_SUB      = 0x05   # [op][dst][src]
OP_XOR      = 0x06   # [op][dst][src]
OP_AND      = 0x07   # [op][dst][src]
OP_OR       = 0x0B   # [op][dst][src]
OP_SHL      = 0x0C   # [op][dst][src]
OP_ROR      = 0x0D   # [op][dst][src]    # rotate right 32-bit
OP_CMP      = 0x0E   # [op][a][b]
OP_JZ       = 0x10   # [op][rel8]
OP_HALT_OK  = 0x14   # [op]
OP_HALT_F   = 0x15   # [op]
OP_SPAWN    = 0x16   # [op][addr_hi][addr_lo][thread_key]
OP_JOIN     = 0x17   # [op]
OP_XOR_IMM  = 0x1D   # [op][addr_hi][addr_lo][imm] -> bytecode[addr] ^= imm

KEY_MAIN   = 0
KEY_CAGES  = 1
KEY_ROWS   = 2
KEY_COLS   = 3
KEY_BLOCKS = 4

# --- main thread ---
spawn_fixups = []

def emit_spawn_placeholder(thread_key, child_key):
    pos = len(bytecode)
    emit(thread_key, OP_SPAWN, 0, 0, child_key)
    spawn_fixups.append((pos + 1, child_key))

emit_spawn_placeholder(KEY_MAIN, KEY_CAGES)
emit_spawn_placeholder(KEY_MAIN, KEY_ROWS)
emit_spawn_placeholder(KEY_MAIN, KEY_COLS)
emit_spawn_placeholder(KEY_MAIN, KEY_BLOCKS)
emit(KEY_MAIN, OP_JOIN)
emit(KEY_MAIN, OP_HALT_OK)


# ------------------------------------------------------------
# CAGES THREAD
# Self-modifying: target immediates are stored masked and
# patched right before use with OP_XOR_IMM.
# ------------------------------------------------------------

addr_cages = len(bytecode)

CAGE_MASK_HI = 0xA5
CAGE_MASK_LO = 0x5A

for cage_id in range(1, 35):
    cells = [i for i, c in enumerate(sudoku_grid) if c == cage_id]
    target = sudoku_sums[cage_id - 1]

    masked_hi = ((target >> 8) & 0xFF) ^ CAGE_MASK_HI
    masked_lo = (target & 0xFF) ^ CAGE_MASK_LO

    emit(KEY_CAGES, OP_LOAD_IMM, 0, 0, 0)

    for cell in cells:
        emit(KEY_CAGES, OP_LOAD_INP, 1, cell)

        emit(KEY_CAGES, OP_MOV, 2, 1)

        emit(KEY_CAGES, OP_LOAD_IMM, 3, 0, 0)

        emit(KEY_CAGES, OP_XOR, 2, 3)

        emit(KEY_CAGES, OP_LOAD_IMM, 4, 0, 0xFF)
        emit(KEY_CAGES, OP_AND, 2, 4)

        emit(KEY_CAGES, OP_ADD, 0, 2)

    load_pos = len(bytecode) + 8

    emit(
        KEY_CAGES, OP_XOR_IMM,
        ((load_pos + 2) >> 8) & 0xFF,
        (load_pos + 2) & 0xFF,
        CAGE_MASK_HI
    )
    emit(
        KEY_CAGES, OP_XOR_IMM,
        ((load_pos + 3) >> 8) & 0xFF,
        (load_pos + 3) & 0xFF,
        CAGE_MASK_LO
    )

    emit(KEY_CAGES, OP_LOAD_IMM, 1, masked_hi, masked_lo)

    emit(KEY_CAGES, OP_CMP, 0, 1)
    emit(KEY_CAGES, OP_JZ, 1)
    emit(KEY_CAGES, OP_HALT_F)

emit(KEY_CAGES, OP_HALT_OK)


# ------------------------------------------------------------
# ROWS THREAD
# Use some real extra ops so it is less template-obvious.
# Valid set mask must equal 0x03FE for digits 1..9.
# ------------------------------------------------------------

addr_rows = len(bytecode)

for row in range(9):
    emit(KEY_ROWS, OP_LOAD_IMM, 0, 0, 0)  # R0 = mask

    for col in range(9):
        idx = row * 9 + col

        emit(KEY_ROWS, OP_LOAD_INP, 1, idx)      # R1 = digit
        emit(KEY_ROWS, OP_MOV, 2, 1)             # R2 = digit
        emit(KEY_ROWS, OP_LOAD_IMM, 3, 0, 1)     # R3 = 1

        # R4 = 0, then R2 ^= R4 (no-op but real emitted op)
        emit(KEY_ROWS, OP_LOAD_IMM, 4, 0, 0)
        emit(KEY_ROWS, OP_XOR, 2, 4)

        emit(KEY_ROWS, OP_SHL, 3, 2)             # R3 <<= digit
        emit(KEY_ROWS, OP_OR, 0, 3)              # mask |= bit

    emit(KEY_ROWS, OP_LOAD_IMM, 1, 0x03, 0xFE)
    emit(KEY_ROWS, OP_CMP, 0, 1)
    emit(KEY_ROWS, OP_JZ, 1)
    emit(KEY_ROWS, OP_HALT_F)

emit(KEY_ROWS, OP_HALT_OK)


# ------------------------------------------------------------
# COLS THREAD
# Same semantics, slightly different emitted sequence.
# ------------------------------------------------------------

addr_cols = len(bytecode)

for col in range(9):
    emit(KEY_COLS, OP_LOAD_IMM, 0, 0, 0)  # R0 = mask

    for row in range(9):
        idx = row * 9 + col

        emit(KEY_COLS, OP_LOAD_INP, 1, idx)      # R1 = digit
        emit(KEY_COLS, OP_LOAD_IMM, 2, 0, 1)     # R2 = 1
        emit(KEY_COLS, OP_MOV, 3, 1)             # R3 = digit

        # Emit real extra ops
        emit(KEY_COLS, OP_LOAD_IMM, 4, 0, 0)
        emit(KEY_COLS, OP_SUB, 3, 4)             # still digit
        emit(KEY_COLS, OP_SHL, 2, 3)             # 1 << digit
        emit(KEY_COLS, OP_OR, 0, 2)

    emit(KEY_COLS, OP_LOAD_IMM, 1, 0x03, 0xFE)
    emit(KEY_COLS, OP_CMP, 0, 1)
    emit(KEY_COLS, OP_JZ, 1)
    emit(KEY_COLS, OP_HALT_F)

emit(KEY_COLS, OP_HALT_OK)


# ------------------------------------------------------------
# BLOCKS THREAD (3x3)
# ------------------------------------------------------------

addr_blocks = len(bytecode)

for br in range(3):
    for bc in range(3):
        emit(KEY_BLOCKS, OP_LOAD_IMM, 0, 0, 0)  # R0 = mask

        for r in range(3):
            for c in range(3):
                idx = (br * 3 + r) * 9 + (bc * 3 + c)

                emit(KEY_BLOCKS, OP_LOAD_INP, 1, idx)   # R1 = digit
                emit(KEY_BLOCKS, OP_MOV, 2, 1)          # R2 = digit
                emit(KEY_BLOCKS, OP_LOAD_IMM, 3, 0, 1)  # R3 = 1

                # Real extra ops
                emit(KEY_BLOCKS, OP_LOAD_IMM, 4, 0, 0xFF)
                emit(KEY_BLOCKS, OP_AND, 2, 4)
                emit(KEY_BLOCKS, OP_SHL, 3, 2)
                emit(KEY_BLOCKS, OP_OR, 0, 3)

        emit(KEY_BLOCKS, OP_LOAD_IMM, 1, 0x03, 0xFE)
        emit(KEY_BLOCKS, OP_CMP, 0, 1)
        emit(KEY_BLOCKS, OP_JZ, 1)
        emit(KEY_BLOCKS, OP_HALT_F)

emit(KEY_BLOCKS, OP_HALT_OK)


# ------------------------------------------------------------
# Fix SPAWN addresses
# ------------------------------------------------------------

child_addrs = {
    KEY_CAGES: addr_cages,
    KEY_ROWS: addr_rows,
    KEY_COLS: addr_cols,
    KEY_BLOCKS: addr_blocks,
}

for pos, child_key in spawn_fixups:
    addr = child_addrs[child_key]
    bytecode[pos] = (addr >> 8) & 0xFF
    bytecode[pos + 1] = addr & 0xFF


# ------------------------------------------------------------
# Outer bytecode scrambling: 3 worker threads decrypt stripes
# ------------------------------------------------------------

KEYS = [0x7A, 0x3B, 0x9C]
scrambled = bytearray(len(bytecode))

for i in range(len(bytecode)):
    scrambled[i] = bytecode[i] ^ KEYS[i % 3]

c_bytecode_array = ", ".join(f"0x{b:02x}" for b in scrambled)


def build_fragments(raw_code, key_bytes, fragment_count, order):
    assert fragment_count >= 2
    base = len(raw_code) // fragment_count
    rem = len(raw_code) % fragment_count

    logical_frags = []
    off = 0
    for i in range(fragment_count):
        frag_len = base + (1 if i < rem else 0)
        logical_frags.append(raw_code[off:off + frag_len])
        off += frag_len

    packed = bytearray()
    for logical_idx in order:
        packed.extend(rc4(logical_frags[logical_idx], key_bytes))
    return bytes(packed)


def build_c_code():
    c_frag_order = ", ".join(str(x) for x in STAGE3_FRAGMENT_ORDER)
    fragment_defs = f"""
static const uint8_t stage3_frag_order[{STAGE3_FRAGMENT_COUNT}] = {{{c_frag_order}}};

void restore_stage3_fragments(uint8_t *dst, size_t total_len, uint8_t *key, int key_len) {{
    uint8_t *scratch = (uint8_t*)malloc(total_len);
    size_t logical_offsets[{STAGE3_FRAGMENT_COUNT}];
    size_t frag_sizes[{STAGE3_FRAGMENT_COUNT}];
    size_t base = total_len / {STAGE3_FRAGMENT_COUNT};
    size_t rem = total_len % {STAGE3_FRAGMENT_COUNT};
    size_t off = 0;
    size_t src_off = 0;

    if (scratch == NULL) {{
        perror("malloc");
        exit(1);
    }}

    for (int i = 0; i < {STAGE3_FRAGMENT_COUNT}; i++) {{
        frag_sizes[i] = base + (i < (int)rem ? 1 : 0);
        logical_offsets[i] = off;
        off += frag_sizes[i];
    }}

    for (int i = 0; i < {STAGE3_FRAGMENT_COUNT}; i++) {{
        uint8_t logical_idx = stage3_frag_order[i];
        size_t frag_len = frag_sizes[logical_idx];
        memcpy(scratch + logical_offsets[logical_idx], dst + src_off, frag_len);
        rc4_crypt(scratch + logical_offsets[logical_idx], (int)frag_len, key, key_len);
        src_off += frag_len;
    }}

    memcpy(dst, scratch, total_len);
    free(scratch);
}}

void derive_stage3_material(const char *user_key, uint8_t out[32]) {{
    for (int i = 0; i < 32; i++) {{
        out[i] = (uint8_t)(0x31 + 11 * i);
    }}

    for (int i = 0; i < 81; i++) {{
        uint8_t b = (uint8_t)user_key[i];
        int a = i % 32;
        int c = (i * 7 + 3) % 32;
        int d = (i * 13 + 11) % 32;

        out[a] ^= b;
        out[a] = (uint8_t)(out[a] + (((17 * i) ^ b) & 0xFF));

        out[c] = (uint8_t)((out[c] << 1) | (out[c] >> 7));
        out[c] ^= (uint8_t)(b + i);

        uint8_t mixed;
        int rot = i & 7;
        if (rot == 0) {{
            mixed = b;
        }} else {{
            mixed = (uint8_t)((b << rot) | (b >> (8 - rot)));
        }}
        out[d] = (uint8_t)(out[d] + mixed);
    }}
}}
"""
    stage3_restore = """
    restore_stage3_fragments(__start_stage3, (size_t)(end - start), (uint8_t*)input, 81);
"""

    return f"""
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <stdint.h>
#include <sys/mman.h>
#include <sys/ptrace.h>
#include <unistd.h>

extern uint8_t __start_stage3[];
extern uint8_t __stop_stage3[];

#define SEC_FLAG __attribute__((section("stage3"), noinline))

uint8_t bytecode[{len(scrambled)}] = {{{c_bytecode_array}}};
char input[100];
int anti_debug_flag = 0;

void* decrypt_bytecode_chunk(void* arg) {{
    int tid = (int)(long)arg;
    uint8_t key;

    if (tid == 0) {{
        key = 0x7A + anti_debug_flag;
    }} else if (tid == 1) {{
        key = 0x3B;
    }} else {{
        key = 0x9C;
    }}

    for (int i = tid; i < (int)sizeof(bytecode); i += 3) {{
        bytecode[i] ^= key;
    }}
    return NULL;
}}

typedef struct {{
    uint16_t start_ip;
    int success;
    uint8_t thread_key;
}} vm_context;

static inline uint32_t ror32(uint32_t x, uint32_t n) {{
    n &= 31;
    return (x >> n) | (x << ((32 - n) & 31));
}}

void* run_vm(void* arg) {{
    vm_context* ctx = (vm_context*)arg;
    ctx->success = 1;

    int32_t R[16] = {{0}};
    uint8_t ZF = 0;
    uint16_t IP = ctx->start_ip;

    pthread_t child_threads[8];
    vm_context child_ctxs[8];
    int num_children = 0;

    while (IP < sizeof(bytecode)) {{
        uint8_t op = bytecode[IP] ^ ctx->thread_key;

        switch (op) {{
            case 0x01: // LOAD_IMM
                R[bytecode[IP+1]] = (bytecode[IP+2] << 8) | bytecode[IP+3];
                IP += 4;
                break;

            case 0x02: // LOAD_INP
                R[bytecode[IP+1]] = input[bytecode[IP+2]] - '0';
                IP += 3;
                break;

            case 0x03: // MOV
                R[bytecode[IP+1]] = R[bytecode[IP+2]];
                IP += 3;
                break;

            case 0x04: // ADD
                R[bytecode[IP+1]] += R[bytecode[IP+2]];
                IP += 3;
                break;

            case 0x05: // SUB
                R[bytecode[IP+1]] -= R[bytecode[IP+2]];
                IP += 3;
                break;

            case 0x06: // XOR
                R[bytecode[IP+1]] ^= R[bytecode[IP+2]];
                IP += 3;
                break;

            case 0x07: // AND
                R[bytecode[IP+1]] &= R[bytecode[IP+2]];
                IP += 3;
                break;

            case 0x0B: // OR
                R[bytecode[IP+1]] |= R[bytecode[IP+2]];
                IP += 3;
                break;

            case 0x0C: // SHL
                R[bytecode[IP+1]] <<= (R[bytecode[IP+2]] & 31);
                IP += 3;
                break;

            case 0x0D: // ROR
                R[bytecode[IP+1]] = (int32_t)ror32((uint32_t)R[bytecode[IP+1]], (uint32_t)R[bytecode[IP+2]]);
                IP += 3;
                break;

            case 0x0E: // CMP
                ZF = (R[bytecode[IP+1]] == R[bytecode[IP+2]]) ? 1 : 0;
                IP += 3;
                break;

            case 0x10: // JZ
                if (ZF) IP += (int8_t)bytecode[IP+1] + 2;
                else    IP += 2;
                break;

            case 0x14: // HALT_OK
                return NULL;

            case 0x15: // HALT_F
                ctx->success = 0;
                return NULL;

            case 0x16: // SPAWN
                child_ctxs[num_children].start_ip = (bytecode[IP+1] << 8) | bytecode[IP+2];
                child_ctxs[num_children].thread_key = bytecode[IP+3];
                child_ctxs[num_children].success = 1;
                pthread_create(&child_threads[num_children], NULL, run_vm, &child_ctxs[num_children]);
                num_children++;
                IP += 4;
                break;

            case 0x17: // JOIN
                for (int i = 0; i < num_children; i++) {{
                    pthread_join(child_threads[i], NULL);
                    if (child_ctxs[i].success == 0) {{
                        ctx->success = 0;
                    }}
                }}
                if (ctx->success == 0) return NULL;
                IP += 1;
                break;

            case 0x1D: {{ // XOR_IMM
                uint16_t target = (bytecode[IP+1] << 8) | bytecode[IP+2];
                uint8_t imm = bytecode[IP+3];
                if (target < sizeof(bytecode)) {{
                    bytecode[target] ^= imm;
                }}
                IP += 4;
                break;
            }}

            default:
                ctx->success = 0;
                return NULL;
        }}
    }}

    return NULL;
}}

void rc4_crypt(uint8_t *data, int data_len, uint8_t *key, int key_len) {{
    uint8_t s[256], temp;
    int i, j = 0;

    for (i = 0; i < 256; i++) s[i] = i;

    for (i = 0; i < 256; i++) {{
        j = (j + s[i] + key[i % key_len]) % 256;
        temp = s[i];
        s[i] = s[j];
        s[j] = temp;
    }}

    i = j = 0;
    for (int k = 0; k < data_len; k++) {{
        i = (i + 1) % 256;
        j = (j + s[i]) % 256;
        temp = s[i];
        s[i] = s[j];
        s[j] = temp;
        data[k] ^= s[(s[i] + s[j]) % 256];
    }}
}}

{fragment_defs}

SEC_FLAG void reveal_flag(char* user_key) {{
    uint8_t secret_matrix[32] = {{{c_matrix}}};
    uint8_t aes_payload[{len(full_payload)}] = {{{c_payload}}};

    volatile uint8_t derived_key[32];
    uint8_t stage3_material[32];

    derive_stage3_material(user_key, stage3_material);

    for (int i = 0; i < 32; i++) {{
        derived_key[i] = stage3_material[i] ^ secret_matrix[i];
    }}

    printf("\\nGood job! Here is the flag: ");
    for (int i = 0; i < 16; i++) printf("%02x", aes_payload[i]);
    printf(":");
    for (int i = 16; i < {len(full_payload)}; i++) printf("%02x", aes_payload[i]);
    printf("\\n");
}}

int main() {{
    anti_debug_flag = ptrace(PTRACE_TRACEME, 0, 1, 0);

    printf("Give me your key quickly or bad things will happen to you:\\n> ");
    if (fgets(input, sizeof(input), stdin) == NULL) return 1;
    input[strcspn(input, "\\n")] = 0;

    if (strlen(input) != 81) return 1;

    for (int i = 0; i < 81; i++) {{
        if (input[i] < '1' || input[i] > '9') {{
            return 1;
        }}
    }}

    pthread_t dec_threads[3];
    for (long i = 0; i < 3; i++) {{
        pthread_create(&dec_threads[i], NULL, decrypt_bytecode_chunk, (void*)i);
    }}
    for (int i = 0; i < 3; i++) {{
        pthread_join(dec_threads[i], NULL);
    }}

    vm_context main_ctx = {{0, 0, 0}};
    run_vm(&main_ctx);

    if (!main_ctx.success) {{
        printf("Validation Failed.\\n");
        return 1;
    }}

    uintptr_t start = (uintptr_t)__start_stage3;
    uintptr_t end = (uintptr_t)__stop_stage3;
    long pagesz = sysconf(_SC_PAGESIZE);
    uintptr_t page_start = start & ~(uintptr_t)(pagesz - 1);
    size_t span = (size_t)(end - page_start);

    if (mprotect((void*)page_start, span, PROT_READ | PROT_WRITE | PROT_EXEC) != 0) {{
        perror("mprotect");
        return 1;
    }}

{stage3_restore}

#if defined(__GNUC__)
    __builtin___clear_cache((char*)__start_stage3, (char*)__stop_stage3);
#endif

    reveal_flag(input);
    return 0;
}}
"""

def rc4(data, key):
    S = list(range(256))
    j = 0
    out = bytearray()

    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]

    i = 0
    j = 0
    for char in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        out.append(char ^ S[(S[i] + S[j]) % 256])

    return out


print(f"[*] VM bytecode compiled. Total bytes: {len(bytecode)}")

print("[1] Compiling final-layout builder binary...")
with open("challenge_vm.c", "w") as f:
    f.write(build_c_code())

res = subprocess.run([
    "gcc",
    "challenge_vm.c",
    "-o", "sudoku_vm_temp",
    "-pthread",
    "-no-pie",
    "-fno-pie",
    "-O2",
    "-static"
])
if res.returncode != 0:
    sys.exit(1)

print("[2] Extracting plaintext stage3 machine code...")
res = subprocess.run([
    "objcopy",
    "-O", "binary",
    "-j", "stage3",
    "sudoku_vm_temp",
    "stage3.bin"
])
if res.returncode != 0:
    sys.exit(1)

with open("stage3.bin", "rb") as f:
    raw_code = f.read()

print(f"[3] Fragmenting stage3 into {STAGE3_FRAGMENT_COUNT} encrypted chunks...")
packed_stage3 = build_fragments(
    raw_code,
    sudoku_solve_bytes,
    STAGE3_FRAGMENT_COUNT,
    STAGE3_FRAGMENT_ORDER,
)

with open("stage3_enc.bin", "wb") as f:
    f.write(packed_stage3)

print("[4] Injecting fragmented encrypted stage3 back into binary...")
res = subprocess.run([
    "objcopy",
    "--update-section", "stage3=stage3_enc.bin",
    "sudoku_vm_temp",
    "challenge"
])
if res.returncode != 0:
    sys.exit(1)

print("[5] Stripping binary...")
subprocess.run(["strip", "challenge"])

for tmp in ["stage3.bin", "stage3_enc.bin"]:
    if os.path.exists(tmp):
        os.remove(tmp)

print("\\n[+] SUCCESS! Challenge is ready as './challenge'")
