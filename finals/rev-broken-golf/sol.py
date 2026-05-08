#!/usr/bin/env python3

import subprocess, base64
last_bytes = open("./chall_missing_24_bytes", "rb").read()

source = """
;    typedef struct {                       
;      unsigned char     e_ident[EI_NIDENT];
;      uint16_t          e_type;     
;      uint16_t          e_machine;  
;      uint32_t          e_version;  
;      Elf64_Addr        e_entry;    
;      Elf64_Off         e_phoff;    
;      Elf64_Off         e_shoff;    
;      uint32_t          e_flags;    
;      uint16_t          e_ehsize;   
;      uint16_t          e_phentsize;
;      uint16_t          e_phnum;    
;      uint16_t          e_shentsize;
;      uint16_t          e_shnum;
;      uint16_t          e_shstrndx;
;    } Elf64_Ehdr;

;00: 7f45 4c46 **** **** **** **** **** ****  .ELF............
;10: 0200 3e00 **** **** 0100 0000 pppp pp00  ..>.............
;20: 1800 0000 0000 0000 1800 0000 pppp pp00  ................
;30: **** **** **** 3800 0100 qqqq qqqq qq00  ......8.........
;40: 0100 qqqq qqqq qq00 **** **** **** ****  ................

; e_ident is 16 bytes
db 0x7f, "ELF", 0x02
times 11 db 0x00

; e_type 
db 0x02, 0x00

; e_machine
db 0x3e, 0x00

times 4 db 0x00
"""

with open("/tmp/sol.s", "w") as f:
    f.write(source)

subprocess.run(["nasm", "-f", "bin", "/tmp/sol.s", "-o", "/tmp/sol"])

print("ok")

with open("/tmp/sol", "rb") as f:
    data = f.read()

with open("/tmp/final", "wb") as f:
    f.write(data+last_bytes)

