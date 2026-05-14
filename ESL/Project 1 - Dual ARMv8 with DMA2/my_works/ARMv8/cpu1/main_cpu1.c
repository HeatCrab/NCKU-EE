#define UART_BASE 0x40001000  // UART_1 (cpu1)
#include "../common/DMA2_regs.h"
#include "../common/write.h"

#define ROUNDS 3

// Linked into init.S's irq_handler stub. Same polling rationale as cpu0 —
// see main_cpu0.c. Defensive content for the unlikely case where nIRQ does
// fire: clear CTRL=0 to deassert INT1, then write FLAG=0 to mirror what the
// main-line polling code does at the end of each round.
void dma2_int2_handler() {
    *(volatile uint32_t *)DMA2_CH1_CTRL = 0;
    *(volatile uint32_t *)FLAG_ADDR     = 0;
}

static void fill_ram3_source(void) {
    // Step B: 1KB of "FEDCBA9876543210" repeated, at RAM3[0x400..0x7FF].
    // This is the source region for DMA channel 1 (RAM3 -> RAM2).
    char *src = (char *)(RAM3_BASE + 0x400);
    for (int i = 0; i < 1024; i++) src[i] = "FEDCBA9876543210"[i % 16];
}

static void dma_ch1_transfer_1kb(void) {
    // Program DMA channel 1: copy 1KB from RAM3[0x400..] to RAM2[0..].
    *(volatile uint32_t *)DMA2_CH1_SRC  = RAM3_BASE + 0x400;
    *(volatile uint32_t *)DMA2_CH1_DST  = RAM2_BASE;
    *(volatile uint32_t *)DMA2_CH1_SIZE = 1024;
    *(volatile uint32_t *)DMA2_CH1_CTRL = 1;

    while (*(volatile uint32_t *)DMA2_CH1_SIZE != 0) { }

    *(volatile uint32_t *)DMA2_CH1_CTRL = 0;
}

static void print_round(int r) {
    char c = '0' + r;
    print_str("ARMv8-1: round ");
    _write(1, &c, 1);
    print_str("\n");
}

void main() {
    uart_init();
    print_str("ARMv8-1 boot OK\n");

    // Step B — initialization data into RAM3[0x400..0x7FF].
    fill_ram3_source();
    print_str("ARMv8-1: RAM3 filled with \"FEDCBA9876543210\" repeated\n");

    // Steps E-F, repeated three times per spec step G.
    for (int round = 0; round < ROUNDS; round++) {
        print_round(round);

        // Step E: wait for flag == 1, set by cpu0 in step D.
        print_str("ARMv8-1: waiting flag == 1\n");
        while (*(volatile uint32_t *)FLAG_ADDR != 1) { }

        // Step E: kick DMA channel 1 and poll for completion.
        print_str("ARMv8-1: DMA ch1 RAM3 -> RAM2 start\n");
        dma_ch1_transfer_1kb();
        print_str("ARMv8-1: DMA ch1 done\n");

        // Step F: hand off back to cpu0.
        *(volatile uint32_t *)FLAG_ADDR = 0;
        print_str("ARMv8-1: flag <- 0\n");

        char msg[] = "ARMv8-1: Transfer complete once\n";
        _write(1, msg, sizeof(msg));
    }

    print_str("ARMv8-1: all rounds done, halting\n");
    while (1) { }
}
