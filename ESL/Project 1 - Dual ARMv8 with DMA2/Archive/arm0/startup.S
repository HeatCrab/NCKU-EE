/* startup.S — ARMv8 AArch64 bare-metal startup
 * Provides: exception vector table, _start, _irq_entry
 */

.global _start
.extern irq_handler         /* defined in main.c */

/* ──────────────────────────────────────────────────────────────
 * Exception vector table (pointed to by VBAR_EL1)
 * ARMv8 AArch64: 4 groups × 4 entries, each entry 0x80 bytes.
 * We only wire up EL1/SPx IRQ; everything else spins.
 * ────────────────────────────────────────────────────────────── */
.section ".text.vectors"
.balign 0x800

_vectors:
    /* EL1 with SP_EL0 */
    .balign 0x80;  b .              /* Sync   */
    .balign 0x80;  b .              /* IRQ    */
    .balign 0x80;  b .              /* FIQ    */
    .balign 0x80;  b .              /* SError */

    /* EL1 with SP_EL1 */
    .balign 0x80;  b .              /* Sync   */
    .balign 0x80;  b _irq_entry     /* IRQ    */
    .balign 0x80;  b .              /* FIQ    */
    .balign 0x80;  b .              /* SError */

    /* Lower EL, AArch64 */
    .balign 0x80;  b .
    .balign 0x80;  b .
    .balign 0x80;  b .
    .balign 0x80;  b .

    /* Lower EL, AArch32 */
    .balign 0x80;  b .
    .balign 0x80;  b .
    .balign 0x80;  b .
    .balign 0x80;  b .

/* ──────────────────────────────────────────────────────────────
 * Reset entry / _start
 * ────────────────────────────────────────────────────────────── */
.section ".text.startup"
.balign 4

_start:
    /* Set stack pointer to top of local RAM */
    ldr     x0, =_stack_top
    mov     sp, x0

    /* Install exception vector table */
    ldr     x0, =_vectors
    msr     vbar_el1, x0
    isb

    /* Switch to SP_EL1 (required to reach EL1/SPx vector) */
    mrs     x0, spsel
    orr     x0, x0, #1
    msr     spsel, x0

    /* Enable IRQ: clear I bit in DAIF */
    msr     daifclr, #2
    isb

    /* Zero BSS */
    ldr     x0, =_bss_start
    ldr     x1, =_bss_end
.zero_bss:
    cmp     x0, x1
    b.ge    .bss_done
    str     xzr, [x0], #8
    b       .zero_bss
.bss_done:

    bl      main

    /* Halt if main returns */
.halt:
    wfi
    b       .halt

/* ──────────────────────────────────────────────────────────────
 * IRQ entry stub
 * Save caller-saved registers, call irq_handler(), then eret.
 * ────────────────────────────────────────────────────────────── */
_irq_entry:
    sub     sp,  sp,  #(8 * 18)
    stp     x0,  x1,  [sp, #(8 *  0)]
    stp     x2,  x3,  [sp, #(8 *  2)]
    stp     x4,  x5,  [sp, #(8 *  4)]
    stp     x6,  x7,  [sp, #(8 *  6)]
    stp     x8,  x9,  [sp, #(8 *  8)]
    stp     x10, x11, [sp, #(8 * 10)]
    stp     x12, x13, [sp, #(8 * 12)]
    stp     x14, x15, [sp, #(8 * 14)]
    stp     x16, x17, [sp, #(8 * 16)]

    bl      irq_handler

    ldp     x0,  x1,  [sp, #(8 *  0)]
    ldp     x2,  x3,  [sp, #(8 *  2)]
    ldp     x4,  x5,  [sp, #(8 *  4)]
    ldp     x6,  x7,  [sp, #(8 *  6)]
    ldp     x8,  x9,  [sp, #(8 *  8)]
    ldp     x10, x11, [sp, #(8 * 10)]
    ldp     x12, x13, [sp, #(8 * 12)]
    ldp     x14, x15, [sp, #(8 * 14)]
    ldp     x16, x17, [sp, #(8 * 16)]
    add     sp,  sp,  #(8 * 18)

    eret
