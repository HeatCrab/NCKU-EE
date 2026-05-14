#include <stdint.h>

// Default UART base = UART_0 at 0x40000000 (Cortex-A35 Example template).
// Override per-CPU by `#define UART_BASE ...` BEFORE including this header.
// cpu0 -> 0x40000000 (UART_0); cpu1 -> 0x40001000 (UART_1).
#ifndef UART_BASE
#define UART_BASE 0x40000000
#endif

// PL011 register offsets — verified against dhrystone_aa64_cpu0.axf
// Setup_UART (1003570) and Setup_UART_Reg_Address (10035b0).
#define UART_DR     0x000  // Data register (TX/RX)
#define UART_FR     0x018  // Flag register (bit 5 = TXFF)
#define UART_IBRD   0x024
#define UART_FBRD   0x028
#define UART_LCR_H  0x02c
#define UART_CR     0x030  // bit 0 = UARTEN, bit 8 = TXE, bit 9 = RXE

// Mirror of dhrystone Setup_UART. Without UARTEN, DR writes are silently
// dropped — that was why our earlier prints produced no output.
static inline void uart_init(void) {
    *(volatile uint32_t *)(UART_BASE + UART_IBRD)  = 0x10;
    *(volatile uint32_t *)(UART_BASE + UART_FBRD)  = 0x10;
    *(volatile uint32_t *)(UART_BASE + UART_LCR_H) = 0x60;   // 8-bit, no FIFO
    *(volatile uint32_t *)(UART_BASE + UART_CR)    = 0x301;  // UARTEN|TXE|RXE
}

int _write(int fd, char *buf, int count) {
    for (int i = 0; i < count; i++) {
        // PL011 only does line-feed on '\n' — no implicit carriage return.
        // Without this, every line starts further right than the last in
        // a typical terminal, producing the staircase effect.
        if (buf[i] == '\n') {
            while (*(volatile uint32_t *)(UART_BASE + UART_FR) & (1 << 5));
            *(volatile uint32_t *)(UART_BASE + UART_DR) = '\r';
        }
        // Wait while TX holding register full (FR bit 5 = TXFF).
        while (*(volatile uint32_t *)(UART_BASE + UART_FR) & (1 << 5));
        *(volatile uint32_t *)(UART_BASE + UART_DR) = (uint8_t)buf[i];
    }
    return count;
}

// Print a NUL-terminated string.
static void print_str(const char *s) {
    int n = 0;
    while (s[n]) n++;
    _write(1, (char *)s, n);
}

// Print a 32-bit value as "0xXXXXXXXX\n".
static void print_hex32(uint32_t v) {
    char buf[12] = "0xXXXXXXXX\n";
    for (int i = 0; i < 8; i++) {
        int nib = (v >> (28 - i * 4)) & 0xf;
        buf[2 + i] = nib < 10 ? ('0' + nib) : ('A' + nib - 10);
    }
    _write(1, buf, 11);
}
