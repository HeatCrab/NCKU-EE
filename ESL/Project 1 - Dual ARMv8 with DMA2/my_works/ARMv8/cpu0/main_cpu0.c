#define UART_BASE 0x40000000  // UART_0 (cpu0)
#include "../common/DMA2_regs.h"
#include "../common/write.h"

#define ROUNDS 3

// Linked into init.S's irq_handler stub. Synchronization is done via polling
// (DMA2_CH0_SIZE goes to 0 + memory flag at FLAG_ADDR), not interrupts —
// the A35 Fast Model never delivered nIRQ to the cluster in our setup despite
// the documented active-LOW pin wiring, see the report for the investigation.
// Defensive content: if the IRQ ever does fire (e.g. on a different model
// build), clearing CTRL=0 deasserts INT0 and writing FLAG=1 is idempotent
// with the main-line polling code, so there is no race.
void dma2_int1_handler() {
    *(volatile uint32_t *)DMA2_CH0_CTRL = 0;
    *(volatile uint32_t *)FLAG_ADDR     = 1;
}

static void fill_ram2_source(void) {
    // Step A: 1KB of "0123456789ABCDEF" repeated, at RAM2[0x400..0x7FF].
    // This is the source region for DMA channel 0 (RAM2 -> RAM3).
    char *src = (char *)(RAM2_BASE + 0x400);
    for (int i = 0; i < 1024; i++) src[i] = "0123456789ABCDEF"[i % 16];
}

static void dma_ch0_transfer_1kb(void) {
    // Program DMA channel 0: copy 1KB from RAM2[0x400..] to RAM3[0..].
    // block0 was cleared in DMA2.cpp's dma_process0 else-branch the last
    // time we wrote CTRL=0, so SRC/DST/SIZE writes accept.
    *(volatile uint32_t *)DMA2_CH0_SRC  = RAM2_BASE + 0x400;
    *(volatile uint32_t *)DMA2_CH0_DST  = RAM3_BASE;
    *(volatile uint32_t *)DMA2_CH0_SIZE = 1024;
    *(volatile uint32_t *)DMA2_CH0_CTRL = 1;

    // Poll DMA's SIZE register: dma_process0 decrements SIZE0 by 4 each
    // beat and stops at 0. Reading SIZE0 == 0 means DMA finished.
    while (*(volatile uint32_t *)DMA2_CH0_SIZE != 0) { }

    // Clear START so block0 releases for the next round's register writes.
    *(volatile uint32_t *)DMA2_CH0_CTRL = 0;
}

static void print_round(int r) {
    char c = '0' + r;
    print_str("ARMv8-0: round ");
    _write(1, &c, 1);
    print_str("\n");
}

void main() {
    uart_init();
    print_str("ARMv8-0 boot OK\n");

    // Step A — initialization data into RAM2[0x400..0x7FF].
    fill_ram2_source();
    print_str("ARMv8-0: RAM2 filled with \"0123456789ABCDEF\" repeated\n");

    // Steps C-D, repeated three times per spec step G.
    for (int round = 0; round < ROUNDS; round++) {
        print_round(round);

        // Step C: wait for flag == 0. Initial value is 0 (RAM2 reset state),
        // and from round 2 onwards cpu1 resets it to 0 in step F.
        print_str("ARMv8-0: waiting flag == 0\n");
        while (*(volatile uint32_t *)FLAG_ADDR != 0) { }

        // Step C: kick the DMA and wait for completion via polling.
        print_str("ARMv8-0: DMA ch0 RAM2 -> RAM3 start\n");
        dma_ch0_transfer_1kb();
        print_str("ARMv8-0: DMA ch0 done\n");

        // Step D: hand off to cpu1.
        *(volatile uint32_t *)FLAG_ADDR = 1;
        print_str("ARMv8-0: flag <- 1\n");

        char msg[] = "ARMv8-0: Transfer complete once\n";
        _write(1, msg, sizeof(msg));
    }

    print_str("ARMv8-0: all rounds done, halting\n");
    while (1) { }
}
