global encrypt
section .text
encrypt:
    xor r8, r8
    jmp .obfuscated_dispatch
.obfuscated_39:
    shr r13d, 5

    mov r8, 40
    jmp .obfuscated_dispatch
.obfuscated_23:
    mov [rsp + r14], r10b

    mov r8, 24
    jmp .obfuscated_dispatch
.obfuscated_37:
    xor r12d, r13d

    mov r8, 38
    jmp .obfuscated_dispatch
.obfuscated_33:
    shl r12d, 4

    mov r8, 34
    jmp .obfuscated_dispatch
.obfuscated_45:
    add r12d, [rsp + r14 + 8]

    mov r8, 46
    jmp .obfuscated_dispatch
.obfuscated_42:
    add r10d, r12d

    mov r8, 43
    jmp .obfuscated_dispatch
.obfuscated_30:
    mov r10d, [rdi]

    mov r8, 31
    jmp .obfuscated_dispatch
.obfuscated_62:
    add rsp, 256

    mov r8, 63
    jmp .obfuscated_dispatch
.obfuscated_63:
    pop r14

    mov r8, 64
    jmp .obfuscated_dispatch
.obfuscated_13:
    add al, 1
    jnc .obfuscated_12

    mov r8, 14
    jmp .obfuscated_dispatch
.obfuscated_4:
    sub rsp, 256

    mov r8, 5
    jmp .obfuscated_dispatch
.obfuscated_60:
    add r14b, 16
    jc .obfuscated_14
    jmp .obfuscated_28

    mov r8, 61
    jmp .obfuscated_dispatch
.obfuscated_16:
    xor rax, rax

    mov r8, 17
    jmp .obfuscated_dispatch
.obfuscated_53:
    add r11d, r12d

    mov r8, 54
    jmp .obfuscated_dispatch
.obfuscated_5:
    test rsi, rsi
    jz .obfuscated_61

    mov r8, 6
    jmp .obfuscated_dispatch
.obfuscated_8:

    mov r8, 9
    jmp .obfuscated_dispatch
.obfuscated_36:
    add r13d, r9d

    mov r8, 37
    jmp .obfuscated_dispatch
.obfuscated_32:
    mov r12d, r11d

    mov r8, 33
    jmp .obfuscated_dispatch
.obfuscated_21:
    mov r10b, [rsp + r14]

    mov r8, 22
    jmp .obfuscated_dispatch
.obfuscated_9:
    mov rax, 1
    jmp .obfuscated_62

    mov r8, 10
    jmp .obfuscated_dispatch
.obfuscated_51:
    add r13d, [rsp + r14 + 12]

    mov r8, 52
    jmp .obfuscated_dispatch
.obfuscated_54:
    add r9d, 0x9e3779b9

    mov r8, 55
    jmp .obfuscated_dispatch
.obfuscated_6:
    mov rax, rsi

    mov r8, 7
    jmp .obfuscated_dispatch
.obfuscated_44:
    shl r12d, 4

    mov r8, 45
    jmp .obfuscated_dispatch
.obfuscated_59:
    sub rsi, 8
    jz .obfuscated_61

    mov r8, 60
    jmp .obfuscated_dispatch
.obfuscated_29:
    mov r9d, 0x9e3779b9

    mov r8, 30
    jmp .obfuscated_dispatch
.obfuscated_10:

    mov r8, 11
    jmp .obfuscated_dispatch
.obfuscated_57:
    mov [rdi + 4], r11d

    mov r8, 58
    jmp .obfuscated_dispatch
.obfuscated_28:
    mov al, 32

    mov r8, 29
    jmp .obfuscated_dispatch
.obfuscated_50:
    shr r13d, 5

    mov r8, 51
    jmp .obfuscated_dispatch
.obfuscated_3:
    push r14

    mov r8, 4
    jmp .obfuscated_dispatch
.obfuscated_18:
    xor r9, r9

    mov r8, 19
    jmp .obfuscated_dispatch
.obfuscated_34:
    add r12d, [rsp + r14]

    mov r8, 35
    jmp .obfuscated_dispatch
.obfuscated_20:

    mov r8, 21
    jmp .obfuscated_dispatch
.obfuscated_35:
    mov r13d, r11d

    mov r8, 36
    jmp .obfuscated_dispatch
.obfuscated_64:
    pop r13

    mov r8, 65
    jmp .obfuscated_dispatch
.obfuscated_43:
    mov r12d, r10d

    mov r8, 44
    jmp .obfuscated_dispatch
.obfuscated_12:
    mov [rsp + rax], al

    mov r8, 13
    jmp .obfuscated_dispatch
.obfuscated_25:
    inc rax

    mov r8, 26
    jmp .obfuscated_dispatch
.obfuscated_24:
    add r9b, 1
    jnc .obfuscated_19

    mov r8, 25
    jmp .obfuscated_dispatch
.obfuscated_49:
    mov r13d, r10d

    mov r8, 50
    jmp .obfuscated_dispatch
.obfuscated_55:
    sub al, 1
    jnz .obfuscated_32

    mov r8, 56
    jmp .obfuscated_dispatch
.obfuscated_48:
    xor r12d, r13d

    mov r8, 49
    jmp .obfuscated_dispatch
.obfuscated_61:
    mov rax, 0

    mov r8, 62
    jmp .obfuscated_dispatch
.obfuscated_14:
    test rcx, rcx
    jz .obfuscated_27

    mov r8, 15
    jmp .obfuscated_dispatch
.obfuscated_56:
    mov [rdi], r10d

    mov r8, 57
    jmp .obfuscated_dispatch
.obfuscated_26:
    cmp rax, rcx
    jl .obfuscated_19

    mov r8, 27
    jmp .obfuscated_dispatch
.obfuscated_46:
    mov r13d, r10d

    mov r8, 47
    jmp .obfuscated_dispatch
.obfuscated_17:
    xor r14, r14

    mov r8, 18
    jmp .obfuscated_dispatch
.obfuscated_67:
    ret

    mov r8, 68
    jmp .obfuscated_dispatch
.obfuscated_40:
    add r13d, [rsp + r14 + 4]

    mov r8, 41
    jmp .obfuscated_dispatch
.obfuscated_0:
    enter 0, 0

    mov r8, 1
    jmp .obfuscated_dispatch
.obfuscated_38:
    mov r13d, r11d

    mov r8, 39
    jmp .obfuscated_dispatch
.obfuscated_41:
    xor r12d, r13d

    mov r8, 42
    jmp .obfuscated_dispatch
.obfuscated_66:
    leave

    mov r8, 67
    jmp .obfuscated_dispatch
.obfuscated_27:
    xor r14, r14

    mov r8, 28
    jmp .obfuscated_dispatch
.obfuscated_11:
    xor rax, rax

    mov r8, 12
    jmp .obfuscated_dispatch
.obfuscated_7:
    test rax, 7
    jz .obfuscated_10

    mov r8, 8
    jmp .obfuscated_dispatch
.obfuscated_1:
    push r12

    mov r8, 2
    jmp .obfuscated_dispatch
.obfuscated_2:
    push r13

    mov r8, 3
    jmp .obfuscated_dispatch
.obfuscated_47:
    add r13d, r9d

    mov r8, 48
    jmp .obfuscated_dispatch
.obfuscated_52:
    xor r12d, r13d

    mov r8, 53
    jmp .obfuscated_dispatch
.obfuscated_58:
    add rdi, 8

    mov r8, 59
    jmp .obfuscated_dispatch
.obfuscated_31:
    mov r11d, [rdi + 4]

    mov r8, 32
    jmp .obfuscated_dispatch
.obfuscated_19:
    add r14b, [rdx + rax]

    mov r8, 20
    jmp .obfuscated_dispatch
.obfuscated_22:
    xchg r10b, [rsp + r9]

    mov r8, 23
    jmp .obfuscated_dispatch
.obfuscated_65:
    pop r12

    mov r8, 66
    jmp .obfuscated_dispatch
.obfuscated_15:

    mov r8, 16
    jmp .obfuscated_dispatch
.obfuscated_dispatch:
    cmp r8, 0
    je .obfuscated_0
    cmp r8, 1
    je .obfuscated_1
    cmp r8, 2
    je .obfuscated_2
    cmp r8, 3
    je .obfuscated_3
    cmp r8, 4
    je .obfuscated_4
    cmp r8, 5
    je .obfuscated_5
    cmp r8, 6
    je .obfuscated_6
    cmp r8, 7
    je .obfuscated_7
    cmp r8, 8
    je .obfuscated_8
    cmp r8, 9
    je .obfuscated_9
    cmp r8, 10
    je .obfuscated_10
    cmp r8, 11
    je .obfuscated_11
    cmp r8, 12
    je .obfuscated_12
    cmp r8, 13
    je .obfuscated_13
    cmp r8, 14
    je .obfuscated_14
    cmp r8, 15
    je .obfuscated_15
    cmp r8, 16
    je .obfuscated_16
    cmp r8, 17
    je .obfuscated_17
    cmp r8, 18
    je .obfuscated_18
    cmp r8, 19
    je .obfuscated_19
    cmp r8, 20
    je .obfuscated_20
    cmp r8, 21
    je .obfuscated_21
    cmp r8, 22
    je .obfuscated_22
    cmp r8, 23
    je .obfuscated_23
    cmp r8, 24
    je .obfuscated_24
    cmp r8, 25
    je .obfuscated_25
    cmp r8, 26
    je .obfuscated_26
    cmp r8, 27
    je .obfuscated_27
    cmp r8, 28
    je .obfuscated_28
    cmp r8, 29
    je .obfuscated_29
    cmp r8, 30
    je .obfuscated_30
    cmp r8, 31
    je .obfuscated_31
    cmp r8, 32
    je .obfuscated_32
    cmp r8, 33
    je .obfuscated_33
    cmp r8, 34
    je .obfuscated_34
    cmp r8, 35
    je .obfuscated_35
    cmp r8, 36
    je .obfuscated_36
    cmp r8, 37
    je .obfuscated_37
    cmp r8, 38
    je .obfuscated_38
    cmp r8, 39
    je .obfuscated_39
    cmp r8, 40
    je .obfuscated_40
    cmp r8, 41
    je .obfuscated_41
    cmp r8, 42
    je .obfuscated_42
    cmp r8, 43
    je .obfuscated_43
    cmp r8, 44
    je .obfuscated_44
    cmp r8, 45
    je .obfuscated_45
    cmp r8, 46
    je .obfuscated_46
    cmp r8, 47
    je .obfuscated_47
    cmp r8, 48
    je .obfuscated_48
    cmp r8, 49
    je .obfuscated_49
    cmp r8, 50
    je .obfuscated_50
    cmp r8, 51
    je .obfuscated_51
    cmp r8, 52
    je .obfuscated_52
    cmp r8, 53
    je .obfuscated_53
    cmp r8, 54
    je .obfuscated_54
    cmp r8, 55
    je .obfuscated_55
    cmp r8, 56
    je .obfuscated_56
    cmp r8, 57
    je .obfuscated_57
    cmp r8, 58
    je .obfuscated_58
    cmp r8, 59
    je .obfuscated_59
    cmp r8, 60
    je .obfuscated_60
    cmp r8, 61
    je .obfuscated_61
    cmp r8, 62
    je .obfuscated_62
    cmp r8, 63
    je .obfuscated_63
    cmp r8, 64
    je .obfuscated_64
    cmp r8, 65
    je .obfuscated_65
    cmp r8, 66
    je .obfuscated_66
    cmp r8, 67
    je .obfuscated_67
