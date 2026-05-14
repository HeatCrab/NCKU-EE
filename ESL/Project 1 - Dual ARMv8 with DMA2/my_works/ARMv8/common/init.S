.arch armv8-a

.section .vectors, "ax"
.balign 2048

vector_table:
    .balign 128
    b .                    // Synchronous

    .balign 128
    b irq_handler          // IRQ

    .balign 128
    b .                    // FIQ

    .balign 128
    b .                    // SError


.section .text
.global _start

_start:
    // Disable interrupts
    msr daifset, #0x2

    // Setup stack
    ldr x0, =0x100000
    mov sp, x0

    // Set vector base
    ldr x0, =vector_table
    msr vbar_el3, x0

    // Enable interrupts
    msr daifclr, #0x2

    // Jump to C
    bl main

hang:
    b hang


irq_handler:
    // Save context
    stp x0, x1, [sp, #-16]!
    stp x2, x3, [sp, #-16]!

    bl dma2_int1_handler

    // Restore
    ldp x2, x3, [sp], #16
    ldp x0, x1, [sp], #16

    eret
