global encrypt

section .text

; preserve r8 as jump indicator


; Encrypt plaintext inplace
; 
; Args
; rdi - plaintext
; rsi - length of plaintext
; rdx - key
; rcx - length of key
encrypt:

; kdf
    enter 0, 0  ; create new stack

    push r12    ; save r12
    push r13    ; save r13
    push r14    ; save r14

    sub rsp, 256    ; allocate 256 bytes for buffer

    test rsi, rsi   ; check if rcx is zero
    jz .ret_ok      ; return on zero

    mov rax, rsi    ; rax = rsi
    test rax, 7     ; rax &= 7
    jz .main        ; jump to main section if rax is multiply of 8

    ; alignment error if rax is not multiply of 8 (plaintext should align to 8)
    mov rax, 1  ; return 1
    jmp .ret    ; goto return block

.main:
    ; initialize block
    xor rax, rax    ; reset rax as counter
.loop_blkasg:
    mov [rsp + rax], al ; assign counter value to block

    add al, 1           ; al += 1
    jnc .loop_blkasg    ; continue on size not reached

.blkrot:
    test rcx, rcx       ; check if rcx is zero
    jz .blkrot_outer    ; break on password is empty

    ; rotate block
    xor rax, rax    ; reset rax as key counter
    xor r14, r14    ; reset r14 as sum
    xor r9, r9      ; reset r9 as block counter
.loop_blkrot:
    add r14b, [rdx + rax]    ; add key[rax] to sum

    ; exchange block
    mov r10b, [rsp + r14]   ; r10b = block[r14]
    xchg r10b, [rsp + r9]   ; r10b, block[r9] = block[r9], r10b
    mov [rsp + r14], r10b   ; block[r14] = r10b

    add r9b, 1          ; r9b += 1
    jnc .loop_blkrot    ; continue on size not reached

    inc rax         ; rax += 1
    cmp rax, rcx    ; if size reached
    jl .loop_blkrot ; continue on not reached

.blkrot_outer:

; TEA encrypt
    xor r14, r14    ; reset r14 as counter
.loop_enc:
    mov al, 32          ; assign 32 to al as tea counter
    mov r9d, 0x9e3779b9 ; initialize r9d as sum

    mov r10d, [rdi]     ; assign (rdi as u32*).* (v0) to r10d
    mov r11d, [rdi + 4] ; assign ((rdi + 4) as u32*).* (v1) to r11d
.loop_tea:
    mov r12d, r11d              ; assign v1 to r12d
    shl r12d, 4                 ; v1 << 4
    add r12d, [rsp + r14]       ; (v1 << 4) + ((rsp + r14) as u32*).* (k0)
    mov r13d, r11d              ; assign v1 to r13d
    add r13d, r9d               ; v1 + sum
    xor r12d, r13d              ; ((v1 << 4) + k0) ^ (v1 + sum)
    mov r13d, r11d              ; assign v1 to r13d
    shr r13d, 5                 ; v1 >> 5
    add r13d, [rsp + r14 + 4]   ; (v1 >> 5) + ((rsp + r14 + 4) as u32*).* (k1)
    xor r12d, r13d              ; ((v1 << 4) + k0) ^ (v1 + sum) ^ ((v1 >> 5) + k1)
    add r10d, r12d              ; v0 += ((v1 << 4) + k0) ^ (v1 + sum) ^ ((v1 >> 5) + k1)

    mov r12d, r10d              ; assign v0 to r12d
    shl r12d, 4                 ; v0 << 4
    add r12d, [rsp + r14 + 8]   ; (v0 << 4) + ((rsp + r14 + 8) as u32*).* (k2)
    mov r13d, r10d              ; assign v0 to r13d
    add r13d, r9d               ; v0 + sum
    xor r12d, r13d              ; ((v0 << 4) + k2) ^ (v0 + sum)
    mov r13d, r10d              ; assign v0 to r13d
    shr r13d, 5                 ; v0 >> 5
    add r13d, [rsp + r14 + 12]  ; (v0 >> 5) + ((rsp + r14 + 12) as u32*).* (k2)
    xor r12d, r13d              ; ((v0 << 4) + k2) ^ (v0 + sum) ^ ((v0 >> 5) + k3)
    add r11d, r12d              ; v1 += ((v0 << 4) + k2) ^ (v0 + sum) ^ ((v0 >> 5) + k3)

    add r9d, 0x9e3779b9 ; add delta to sum

    sub al, 1       ; al -= 1
    jnz .loop_tea   ; continue on count not reached

    mov [rdi], r10d     ; assign v0 back to memory
    mov [rdi + 4], r11d ; assign v1 back to memory

    add rdi, 8  ; rdi += 8
    sub rsi, 8  ; rsi -= 8
    jz .ret_ok  ; return on plaintext end reached

    add r14b, 16    ; r14b += 16
    jc .blkrot      ; jump back to rotation on key end reached
    jmp .loop_enc   ; continue on not reached

.ret_ok:
    mov rax, 0  ; return 0

.ret:
    add rsp, 256    ; deallocate buffer

    pop r14     ; recover r14
    pop r13     ; recover r13
    pop r12     ; recover r12

    leave   ; recover the original stack
    ret     ; return to caller
