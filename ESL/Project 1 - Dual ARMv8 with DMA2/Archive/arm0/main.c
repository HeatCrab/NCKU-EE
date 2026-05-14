#include <stdint.h>
#include <stdio.h>

/*
 * DMA2 register map (base 0x100000)
 * Channel 0 registers: used by ARMv8_0
 */
#define DMA2_BASE       0x100000UL
#define DMA2_SRC_0      (*(volatile uint32_t *)(DMA2_BASE + 0x00))
#define DMA2_DST_0      (*(volatile uint32_t *)(DMA2_BASE + 0x04))
#define DMA2_SIZE_0     (*(volatile uint32_t *)(DMA2_BASE + 0x08))
#define DMA2_START_0    (*(volatile uint32_t *)(DMA2_BASE + 0x0C))

/* Shared synchronisation flag, lives in RAM2 */
#define SHARED_FLAG     (*(volatile uint32_t *)0x200800UL)

/*
 * GIC-400 base addresses.
 * Verify these against the VDK Creator platform configuration;
 * the values below are common for ARM reference platforms.
 */
#define GICD_BASE           0x08000000UL
#define GICC_BASE           0x08010000UL

#define GICD_CTLR           (*(volatile uint32_t *)(GICD_BASE + 0x000))
#define GICD_ISENABLER(n)   (*(volatile uint32_t *)(GICD_BASE + 0x100 + 4*(n)))
#define GICC_CTLR           (*(volatile uint32_t *)(GICC_BASE + 0x000))
#define GICC_PMR            (*(volatile uint32_t *)(GICC_BASE + 0x004))
#define GICC_IAR            (*(volatile uint32_t *)(GICC_BASE + 0x00C))
#define GICC_EOIR           (*(volatile uint32_t *)(GICC_BASE + 0x010))

/*
 * IRQ line number for DMA2 INT1.
 * Set this to match the line number assigned when connecting
 * DMA2 INT1 -> ARMv8_0 IRQ input in VDK Creator.
 */
#define IRQ_DMA_INT1    32

#define TRANSFER_SIZE   1024

static volatile int dma0_done = 0;

/* ── GIC initialisation ── */
static void gic_init(void)
{
    GICD_CTLR = 1;
    GICD_ISENABLER(IRQ_DMA_INT1 / 32) = 1u << (IRQ_DMA_INT1 % 32);
    GICC_PMR  = 0xFF;
    GICC_CTLR = 1;
}

/* ── ISR: called from _irq_entry in startup.S when INT1 fires ── */
void irq_handler(void)
{
    uint32_t iar = GICC_IAR;
    uint32_t irq = iar & 0x3FFu;

    if (irq == IRQ_DMA_INT1) {
        DMA2_START_0 = 0;       /* clear START_CLEAR_0 — deasserts INT1 */
        dma0_done = 1;
        printf("[ARMv8_0] ISR: DMA ch0 complete\n");
    }

    GICC_EOIR = iar;
}

int main(void)
{
    gic_init();

    /* (A) Write 1KB "0123456789ABCDEF..." pattern to 0x200400~0x2007FF */
    const char pattern[] = "0123456789ABCDEF";
    volatile uint8_t *buf = (volatile uint8_t *)0x200400UL;
    for (int i = 0; i < TRANSFER_SIZE; i++)
        buf[i] = (uint8_t)pattern[i % 16];
    printf("[ARMv8_0] Init: 1KB pattern written to 0x200400\n");

    for (int round = 0; round < 3; round++) {
        /* (C) Wait for flag = 0x0 */
        printf("[ARMv8_0] Round %d: waiting for flag = 0x0\n", round + 1);
        while (SHARED_FLAG != 0x0)
            ;

        /* Program DMA2 ch0: copy 1KB from 0x200400 (RAM2) to 0x300000 (RAM3) */
        printf("[ARMv8_0] Round %d: starting DMA ch0\n", round + 1);
        dma0_done = 0;
        DMA2_SRC_0   = 0x200400;
        DMA2_DST_0   = 0x300000;
        DMA2_SIZE_0  = TRANSFER_SIZE;
        DMA2_START_0 = 1;

        /* Wait for INT1 ISR to signal completion */
        while (!dma0_done)
            asm volatile("wfi");

        /* (D) Signal ARMv8_1 */
        SHARED_FLAG = 0x1;
        printf("[ARMv8_0] Round %d: DMA done, flag -> 0x1\n", round + 1);
    }

    printf("[ARMv8_0] All 3 rounds complete.\n");
    for (;;)
        asm volatile("wfi");
}
