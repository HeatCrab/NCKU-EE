#ifndef UART_PL011_H
#define UART_PL011_H

// Self-contained PL011 UART output for the Cortex-R52 bare-metal program. The
// PL011 register layout is CPU-agnostic, so this mirrors Project 1's verified
// A35 `write.h`; only the surrounding program changed from AArch64 to AArch32.
// No newlib: the helpers below are all that the YOLOv5 demo needs to print.
//
// Override UART_BASE by `#define UART_BASE ...` BEFORE including this header.
// On the R52 platform UART_0 sits at 0x4000_0000 (template default).

#include <stdint.h>

#ifndef UART_BASE
#define UART_BASE 0x40000000u
#endif

// PL011 register offsets.
#define UART_DR     0x000u  // Data register (TX/RX)
#define UART_FR     0x018u  // Flag register (bit 5 = TXFF)
#define UART_IBRD   0x024u
#define UART_FBRD   0x028u
#define UART_LCR_H  0x02cu
#define UART_CR     0x030u  // bit 0 = UARTEN, bit 8 = TXE, bit 9 = RXE

// Mirror of the example's Setup_UART. Without UARTEN, DR writes are silently
// dropped. VERIFY AT LAB: if no output appears, match these divisor values to
// the R52 example's own UART init (the values are baud-rate dependent).
static inline void uart_init(void) {
    *(volatile uint32_t *)(UART_BASE + UART_IBRD)  = 0x10u;
    *(volatile uint32_t *)(UART_BASE + UART_FBRD)  = 0x10u;
    *(volatile uint32_t *)(UART_BASE + UART_LCR_H) = 0x60u;   // 8-bit, no FIFO
    *(volatile uint32_t *)(UART_BASE + UART_CR)    = 0x301u;  // UARTEN|TXE|RXE
}

static inline void uart_putc(char c) {
    // PL011 does not auto-insert a carriage return; emit one before '\n' so a
    // terminal does not produce the staircase effect.
    if (c == '\n') {
        while (*(volatile uint32_t *)(UART_BASE + UART_FR) & (1u << 5)) { }
        *(volatile uint32_t *)(UART_BASE + UART_DR) = '\r';
    }
    while (*(volatile uint32_t *)(UART_BASE + UART_FR) & (1u << 5)) { }
    *(volatile uint32_t *)(UART_BASE + UART_DR) = (uint8_t)c;
}

static inline void print_str(const char *s) {
    while (*s) uart_putc(*s++);
}

// Print a signed decimal integer.
static inline void print_dec(int32_t v) {
    char buf[12];
    int  i = 0;
    uint32_t u;
    if (v < 0) { uart_putc('-'); u = (uint32_t)(-(int64_t)v); }
    else       { u = (uint32_t)v; }
    if (u == 0) { uart_putc('0'); return; }
    while (u) { buf[i++] = (char)('0' + u % 10u); u /= 10u; }
    while (i) uart_putc(buf[--i]);
}

// Print a 32-bit value as "0xXXXXXXXX".
static inline void print_hex32(uint32_t v) {
    print_str("0x");
    for (int i = 0; i < 8; i++) {
        uint32_t nib = (v >> (28 - i * 4)) & 0xfu;
        uart_putc(nib < 10 ? (char)('0' + nib) : (char)('A' + nib - 10));
    }
}

#endif  // UART_PL011_H
