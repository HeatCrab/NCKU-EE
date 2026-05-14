.arch armv8-a

// cpu1.elf is linked at 0x08000000 (RAM1). cpu1 reaches this image by way of
// cpu0's MPIDR trampoline (`br x0` with x0=0x08000000), so _start MUST be at
// the very start of the section.

.section .vectors, "ax"
.global _start

_start:
    msr   daifset, #0xf            // mask all exceptions during init

    ldr   x0, =0x08100000          // 1 MB into RAM1
    mov   sp, x0

    ldr   x0, =vector_table
    msr   vbar_el3, x0

    msr   daifclr, #0x2            // unmask IRQ
    bl    main
1:  b     1b


// Full 16-entry vector table — see cpu0/init.S for why 4 entries is wrong.
.balign 2048
vector_table:
    // Current EL with SP_EL0
    .balign 128
    b     .                        // 0x000 Sync
    .balign 128
    b     irq_handler              // 0x080 IRQ
    .balign 128
    b     .                        // 0x100 FIQ
    .balign 128
    b     .                        // 0x180 SError

    // Current EL with SP_ELx  (used after reset)
    .balign 128
    b     .                        // 0x200 Sync
    .balign 128
    b     irq_handler              // 0x280 IRQ
    .balign 128
    b     .                        // 0x300 FIQ
    .balign 128
    b     .                        // 0x380 SError

    // Lower EL using AArch64
    .balign 128
    b     .                        // 0x400 Sync
    .balign 128
    b     irq_handler              // 0x480 IRQ
    .balign 128
    b     .                        // 0x500 FIQ
    .balign 128
    b     .                        // 0x580 SError

    // Lower EL using AArch32
    .balign 128
    b     .                        // 0x600 Sync
    .balign 128
    b     irq_handler              // 0x680 IRQ
    .balign 128
    b     .                        // 0x700 FIQ
    .balign 128
    b     .                        // 0x780 SError

irq_handler:
    stp   x0, x1, [sp, #-16]!
    stp   x2, x3, [sp, #-16]!

    bl    dma2_int2_handler

    ldp   x2, x3, [sp], #16
    ldp   x0, x1, [sp], #16
    eret
