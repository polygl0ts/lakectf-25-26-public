main:
    push 0x30
    dup
    push 0x01
    call print_sum
    dup
    push 0x03
    call print_sum
    dup
    push 0x03
    call print_sum
    dup
    push 0x07
    call print_sum
    push 0
    push 10
    push print_sum
    call
    push 0
    exit

print_sum:
    add
    write
    ret

