// DMA2 Base Address in the system bus
#define DMA2_BASE       0x10000000
#define RAM2_BASE       0x20000000
#define RAM3_BASE       0x30000000
#define FLAG_ADDR       0x20000800

// Register Offsets for Set 1 (ARMv8-0)
#define DMA2_CH0_SRC    (DMA2_BASE + 0x00)
#define DMA2_CH0_DST    (DMA2_BASE + 0x04)
#define DMA2_CH0_SIZE   (DMA2_BASE + 0x08)
#define DMA2_CH0_CTRL   (DMA2_BASE + 0x0C)

// Register Offsets for Set 2 (ARMv8-1)
#define DMA2_CH1_SRC    (DMA2_BASE + 0x10)
#define DMA2_CH1_DST    (DMA2_BASE + 0x14)
#define DMA2_CH1_SIZE   (DMA2_BASE + 0x18)
#define DMA2_CH1_CTRL   (DMA2_BASE + 0x1C)
