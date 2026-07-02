/* Cortex-R52 bare-metal link map for the YOLOv5_HW driver (Project 2, Task D).
 * Everything lives in RAM0 (local memory at 0x0, 32MB). The test image
 * containers and the inference results live in RAM1 (0x08000000) and are
 * reached at run time through the YOLOv5_HW registers, so they are not part of
 * this image. Stacks sit high in RAM0, well clear of the small code/data at the
 * bottom. Virtualizer loads the ELF and starts execution at ENTRY (_start). */

ENTRY(_start)

MEMORY
{
    RAM0 (rwx) : ORIGIN = 0x00000000, LENGTH = 32M
}

/* Banked stacks (grow down). The three baked test images (~4.2 MB total) now
 * live in RAM0 .rodata, so the stacks are placed high in the 32 MB RAM0, well
 * clear of code + image data at the bottom. */
__svc_stack_top = 0x01000000;   /* 16 MB */
__irq_stack_top = 0x00F00000;   /* 15 MB */
__abt_stack_top = 0x00E00000;   /* 14 MB */
__und_stack_top = 0x00D00000;   /* 13 MB */
__fiq_stack_top = 0x00C00000;   /* 12 MB */

SECTIONS
{
    . = 0x00000000;

    .vectors : { KEEP(*(.vectors)) } > RAM0

    .text : {
        *(.text*)
        *(.glue_7) *(.glue_7t)
    } > RAM0

    .rodata : { *(.rodata*) } > RAM0

    .data : { *(.data*) } > RAM0

    .bss : {
        __bss_start = .;
        *(.bss*)
        *(COMMON)
        __bss_end = .;
    } > RAM0

    /DISCARD/ : { *(.ARM.exidx*) *(.comment) *(.note*) }
}
