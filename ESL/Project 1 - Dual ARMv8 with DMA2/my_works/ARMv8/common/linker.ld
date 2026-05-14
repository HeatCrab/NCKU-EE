ENTRY(_start)

SECTIONS
{
    . = 0x00000000;

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
