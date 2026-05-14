#include <stdint.h>
#include <stdio.h>

/*
 * DMA2 register map (base 0x100000)
 * Channel 1 registers: used by ARMv8_1
 */
#define DMA2_BASE       0x100000UL
#define DMA2_SRC_1      (*(volatile uint32_t *)(DMA2_BASE + 0x10))
#define DMA2_DST_1      (*(volatile uint32_t *)(DMA2_BASE + 0x14))
#define DMA2_SIZE_1     (*(volatile uint32_t *)(DMA2_BASE + 0x18))
#define DMA2_START_1    (*(volatile uint32_t *)(DMA2_BASE + 0x1C))

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
 * IRQ line number for DMA2 INT2.
 * Set this to match the line number assigned when connecting
 * DMA2 INT2 -> ARMv8_1 IRQ input in VDK Creator.
 */
#define IRQ_DMA_INT2    33

#define TRANSFER_SIZE   1024

static volatile int dma1_done = 0;

/* ── GIC initialisation ── */
static void gic_init(void)
{
    GICD_CTLR = 1;
    GICD_ISENABLER(IRQ_DMA_INT2 / 32) = 1u << (IRQ_DMA_INT2 % 32);
    GICC_PMR  = 0xFF;
    GICC_CTLR = 1;
}

/* ── ISR: called from _irq_entry in startup.S when INT2 fires ── */
void irq_handler(void)
{
    uint32_t iar = GICC_IAR;
    uint32_t irq = iar & 0x3FFu;

    if (irq == IRQ_DMA_INT2) {
        DMA2_START_1 = 0;       /* clear START_CLEAR_1 — deasserts INT2 */
        dma1_done = 1;
        printf("[ARMv8_1] ISR: DMA ch1 complete\n");
    }

    GICC_EOIR = iar;
}

int main(void)
{
    gic_init();

    /* (B) Write 1KB "FEDCBA9876543210..." pattern to 0x300400~0x3007FF */
    const char pattern[] = "FEDCBA9876543210";
    volatile uint8_t *buf = (volatile uint8_t *)0x300400UL;
    for (int i = 0; i < TRANSFER_SIZE; i++)
        buf[i] = (uint8_t)pattern[i % 16];
    printf("[ARMv8_1] Init: 1KB pattern written to 0x300400\n");

    for (int round = 0; round < 3; round++) {
        /* (E) Wait for flag = 0x1 */
        printf("[ARMv8_1] Round %d: waiting for flag = 0x1\n", round + 1);
        while (SHARED_FLAG != 0x1)
            ;

        /* Program DMA2 ch1: move 1KB from 0x300400 (RAM3) to 0x200000 (RAM2) */
        printf("[ARMv8_1] Round %d: starting DMA ch1\n", round + 1);
        dma1_done = 0;
        DMA2_SRC_1   = 0x300400;
        DMA2_DST_1   = 0x200000;
        DMA2_SIZE_1  = TRANSFER_SIZE;
        DMA2_START_1 = 1;

        /* Wait for INT2 ISR to signal completion */
        while (!dma1_done)
            asm volatile("wfi");

        /* (F) Signal ARMv8_0 */
        SHARED_FLAG = 0x0;
        printf("[ARMv8_1] Round %d: DMA done, flag -> 0x0\n", round + 1);
    }

    printf("[ARMv8_1] All 3 rounds complete.\n");
    for (;;)
        asm volatile("wfi");
}
