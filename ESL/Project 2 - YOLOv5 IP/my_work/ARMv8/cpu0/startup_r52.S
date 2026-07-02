// Cortex-R52 (ARMv8-R, AArch32) reset + exception vectors + IRQ handler for the
// YOLOv5_HW bare-metal driver (Project 2, Task D). Because the VDK example ships
// only prebuilt .axf blobs with no reusable startup, this program owns its whole
// image: reset sets the per-mode stacks and VBAR, then branches to main(); the
// IRQ slot routes to a handler that calls the C service routine yolov5_isr().
//
// Modelled on Project 1's AArch64 init.S but rewritten for AArch32: classic
// IRQ-mode banked stack and the 0x18 IRQ vector instead of A35's VBAR_EL3 + eret.

    .syntax unified
    .arm

    .equ MODE_HYP, 0x1A          // Cortex-R52 resets into this mode (EL2)
    .equ MODE_FIQ, 0x11
    .equ MODE_IRQ, 0x12
    .equ MODE_SVC, 0x13
    .equ MODE_ABT, 0x17
    .equ MODE_UND, 0x1B
    .equ I_BIT,    0x80          // CPSR IRQ mask
    .equ F_BIT,    0x40          // CPSR FIQ mask

    .extern main
    .extern yolov5_isr
    .extern exception_report
    .global _start

// ---- Exception vector table (VBAR target, 32-byte aligned) -------------------
//   0x00 Reset  0x04 Undef  0x08 SVC  0x0C Prefetch  0x10 Data
//   0x14 Reserved  0x18 IRQ  0x1C FIQ
    .section .vectors, "ax"
    .balign 32
    .global vector_table
vector_table:
    b   _start            // 0x00 Reset
    b   undef_handler     // 0x04 Undefined
    b   svc_handler       // 0x08 Supervisor Call
    b   prefetch_handler  // 0x0C Prefetch Abort
    b   data_handler      // 0x10 Data Abort
    nop                   // 0x14 Reserved
    b   irq_handler       // 0x18 IRQ
    b   fiq_handler       // 0x1C FIQ

// ---- Reset / startup --------------------------------------------------------
    .section .text
_start:
    // The R52 resets into Hyp mode (EL2). A CPS that tries to leave Hyp is
    // UNPREDICTABLE and the model takes it as an UNDEFINED exception, so we must
    // drop to SVC (EL1) with an exception return instead. First enable the bits
    // EL1 needs, then ERET into SVC; if we somehow start below Hyp, skip ahead.
    mrs     r0, cpsr
    and     r1, r0, #0x1F
    cmp     r1, #MODE_HYP
    bne     in_svc

    // Let EL1 use the GICv3 system-register (ICC_*) interface; otherwise the
    // EL1 ICC_SRE write in gic_init() traps back to EL2. ICC_HSRE = p15,4,c12,c9,5;
    // set Enable (bit 3) | SRE (bit 0).
    mrc     p15, 4, r1, c12, c9, 5
    orr     r1, r1, #0x9
    mcr     p15, 4, r1, c12, c9, 5
    isb

    // Exception-return into SVC mode with IRQ + FIQ masked.
    bic     r0, r0, #0x1F
    orr     r0, r0, #MODE_SVC
    orr     r0, r0, #(I_BIT | F_BIT)
    msr     spsr_cxsf, r0            // SPSR_hyp (current mode is Hyp)
    ldr     r0, =in_svc
    msr     elr_hyp, r0
    eret

in_svc:
    // Now in SVC (EL1) with IRQ + FIQ masked while we set things up.
    cpsid if, #MODE_SVC

    // Point VBAR at our vector table (AArch32: MCR p15,0,Rt,c12,c0,0).
    ldr     r0, =vector_table
    mcr     p15, 0, r0, c12, c0, 0
    isb

    // IRQ-mode banked stack (used while servicing interrupts).
    cps     #MODE_IRQ
    ldr     sp, =__irq_stack_top

    // Exception-mode stacks used by the diagnostic exception reporters.
    cps     #MODE_ABT
    ldr     sp, =__abt_stack_top
    cps     #MODE_UND
    ldr     sp, =__und_stack_top
    cps     #MODE_FIQ
    ldr     sp, =__fiq_stack_top

    // Back to SVC mode for main(); give it its own stack.
    cps     #MODE_SVC
    ldr     sp, =__svc_stack_top

    bl      main
hang:
    wfi
    b       hang

// ---- IRQ handler ------------------------------------------------------------
// On entry lr_irq points one instruction past the interrupted one; fix it by 4
// before saving. The C handler reads ICC_IAR1, services the request, writes
// ICC_EOIR1. Pushing 6 registers (24 bytes) keeps the stack 8-byte aligned for
// the AAPCS call.
    .global irq_handler
irq_handler:
    sub     lr, lr, #4
    push    {r0-r3, r12, lr}
    bl      yolov5_isr
    pop     {r0-r3, r12, lr}
    movs    pc, lr                // return, restoring CPSR from SPSR_irq

// ---- Diagnostic exception handlers -----------------------------------------
// Codes: 1=undef, 2=svc, 3=prefetch abort, 4=data abort, 5=fiq.
// These handlers are for lab bring-up only: print once and stop instead of
// silently looping at the vector slot.
undef_handler:
    mov     r0, #1
    b       exception_common

svc_handler:
    mov     r0, #2
    b       exception_common

prefetch_handler:
    mov     r0, #3
    b       exception_common

data_handler:
    mov     r0, #4
    b       exception_common

fiq_handler:
    mov     r0, #5
    b       exception_common

exception_common:
    push    {r1-r3, r12, lr}
    mrs     r1, spsr
    mov     r2, lr
    bl      exception_report
1:
    wfi
    b       1b
