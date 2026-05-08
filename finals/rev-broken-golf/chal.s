BITS 64
org 0x400000

ehdr:
  db 0x7F, "ELF", 2

  ; The e_ident field is 16 bytes long. The first 5 bytes are the magic number and class.
  ; The remaining 11 bytes are unused and we use these 11 bytes to store the first part of our dispatcher.
dispatcher:
  cmp al, 32
  jne bis
  push byte 0x23
  push qword hole3

  dw 2          ; e_type
  dw 0x3e       ; e_machine

  ; e_version (4 bytes). Overlaps with 32-bit switch return path.
code64:
  db 0
  retfq
  ret

; --- 24 BYTE BOUNDARY ---
  dq main       ; e_entry
  dq 56         ; e_phoff
  dq 0          ; e_shoff
  dd 0          ; e_flags
  dw 64         ; e_ehsize
  dw 56         ; e_phentsize

phdr:
  dd 1          ; p_type
  dd 7          ; p_flags
  dq 0          ; p_offset
  dq 0x400000   ; p_vaddr
  dq 0x400000   ; p_paddr
  dq filesize   ; p_filesz
  dq filesize   ; p_memsz
  dq 0          ; p_align

hole3:
  [BITS 32]
  call bis
  jmp 0x33:code64+3
  [BITS 64]

bis:
    ; [ 64-bit mode ]
    ; 48 B8 00 00 00 00 EB 06 00 00 -> movabs rax, 0x000006eb00000000
    ; (The 48 REX.W prefix makes B8 take an 8-byte immediate. It consumes the jump!)
    ; Execution falls through to 'add ebx, 2'
    ; [ 32-bit mode ]
    ; 48                            -> dec eax
    ; B8 00 00 00 00                -> mov eax, 0
    ; EB 06                         -> jmp short +6 (Jumps over the 64-bit code)
    ; 00 00                         -> add [eax], al (Skipped)
    db 0x48, 0xB8
    dd 0x00000000
    db 0xEB, 0x06
    db 0x00, 0x00

    ; 64-bit code (executed only in 64-bit mode, skipped in 32-bit mode)
    add ebx, 2
    ret

mode32:
    ; 32-bit code (execution lands here after the jmp short +6)
    add ebx, ebx
    ret

main:
  pop rcx
  dec rcx
  pop rsi
  mov ebx, 1

.loop:
  test rcx, rcx
  jz .done

  pop rsi
  mov al, byte [rsi]
  cmp al, '3'
  je .do_32
  cmp al, '6'
  je .do_64
  jmp .next

.do_32:
  mov eax, 0x400800
  mov al, 32
  jmp .call_disp
.do_64:
  mov eax, 0x400800
  mov al, 64

.call_disp:
  mov rbp, rsp
  mov esp, 0x400800
  call dispatcher
  mov rsp, rbp

.next:
  dec rcx
  jmp .loop

.done:
  mov eax, 60
  mov edi, ebx
  syscall

filesize equ $ - ehdr
