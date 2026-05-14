/* Linker script for ARMv8_1 (cpu1).
 * cpu1's local memory (RAM1) starts at 0x08000000 per Project 1 v3 spec.
 * cpu0 uses common/linker.ld which keeps . = 0x00000000 for RAM0.
 */

ENTRY(_start)

SECTIONS
{
    . = 0x08000000;

    .text : {
        *(.vectors)
        *(.text*)
    }

    .rodata : {
        *(.rodata*)
    }

    .data : {
        *(.data*)
    }

    .bss : {
        *(.bss*)
        *(COMMON)
    }
}
