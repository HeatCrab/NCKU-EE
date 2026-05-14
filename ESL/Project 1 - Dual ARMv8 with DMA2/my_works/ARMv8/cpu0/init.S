.arch armv8-a

// cpu0.elf is linked at 0x00000000 (RAM0). Both ARMv8 cores reset to PC=0x0
// in this Cortex-A35 Example template, so this image is the trampoline that
// routes the second core to its own image at 0x08000000.
//
// Putting _start in .vectors guarantees the linker places it at offset 0 of
// the section group (see linker.ld: .text { *(.vectors) ... }).

.section .vectors, "ax"
.global _start

_start:
    // Read MPIDR_EL1.Aff0 — 0 for ARMv8_0, 1 for ARMv8_1 in this cluster.
    mrs   x0, mpidr_el1
    and   x0, x0, #0xf
    cbnz  x0, _redirect_to_cpu1

    // ---- cpu0 path ----
    msr   daifset, #0xf            // mask all exceptions during init

    ldr   x0, =0x00100000          // 1 MB into RAM0
    mov   sp, x0

    ldr   x0, =vector_table
    msr   vbar_el3, x0

    msr   daifclr, #0x2            // unmask IRQ
    bl    main
1:  b     1b

_redirect_to_cpu1:
    ldr   x0, =0x08000000          // entry of cpu1.elf in RAM1
    br    x0


// Full 16-entry vector table. ARMv8 requires 2 KB alignment for VBAR_ELx
// and 16 entries (4 sections × 4 types). After reset SPSel.SP=1, so an IRQ
// taken at EL3 dispatches via "Current EL with SP_ELx" at offset 0x280 —
// not 0x080. A 4-entry table only covers "Current EL with SP_EL0" and the
// IRQ goes to garbage past 0x200, faulting silently.
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

    // Current EL with SP_ELx  (the one actually used after reset)
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

    bl    dma2_int1_handler

    ldp   x2, x3, [sp], #16
    ldp   x0, x1, [sp], #16
    eret
