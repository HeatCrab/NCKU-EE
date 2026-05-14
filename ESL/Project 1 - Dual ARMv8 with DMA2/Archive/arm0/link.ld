/* link.ld — ARMv8 bare-metal linker script
 * Program is loaded at 0x0 in local RAM (RAM0 for CPU0, RAM1 for CPU1).
 * Local RAM is 1MB (0x00000000 ~ 0x000FFFFF).
 */

ENTRY(_start)

MEMORY {
    RAM (rwx) : ORIGIN = 0x00000000, LENGTH = 1M
}

SECTIONS {
    . = ORIGIN(RAM);

    /* Exception vectors must come first so VBAR_EL1 = 0x0 works */
    .text : {
        *(.text.vectors)
        *(.text.startup)
        *(.text*)
        *(.rodata*)
    } > RAM

    .data : {
        *(.data*)
    } > RAM

    .bss : {
        _bss_start = .;
        *(.bss*)
        *(COMMON)
        . = ALIGN(8);
        _bss_end = .;
    } > RAM

    /* Stack grows down from top of RAM */
    _stack_top = ORIGIN(RAM) + LENGTH(RAM);
}
