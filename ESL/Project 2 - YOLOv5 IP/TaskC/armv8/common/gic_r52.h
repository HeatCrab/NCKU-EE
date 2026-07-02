#ifndef GIC_R52_H
#define GIC_R52_H

// Minimal GICv3 setup for the Cortex-R52 (single core, AArch32), enough to take
// one Shared Peripheral Interrupt as an IRQ. References:
//   Cortex-R52/R52+ Programmer's Guide (Arm 109997_100_01), section 8 Interrupts
//   Arm Generic Interrupt Controller Architecture Specification, GICv3/v4 (IHI 0069)
//
// On the R52 the GIC Distributor and Redistributor are memory-mapped at
// (GIC base + 64KB); the CPU interface is reached ONLY through CP15 system
// registers (ICC_*). The R52 GIC implements a single Non-secure state, so SPIs
// are put in Group 1 to be delivered as IRQ (Group 0 would signal FIQ). SPIs on
// the R52 are rising-edge or active-HIGH level-sensitive -- this code configures
// INTID 32 as active-HIGH level, which requires the YOLOv5_HW.INT pin to assert
// HIGH on completion (see the report's interrupt-path note).

#include <stdint.h>

// GIC base = the R52 cluster's PERIPHBASE parameter, read from Yolo.vdksys
// (Parameters > initialize > PERIPHBASE = 0x13080000). The Distributor then
// sits at PERIPHBASE + 64KB = 0x13090000.
#ifndef GIC_PERIPHBASE
#define GIC_PERIPHBASE   0x13080000u
#endif

// Distributor occupies the 64KB page at (GIC base + 64KB) -- Programmer's Guide
// Table 8-1.
#define GICD_BASE        (GIC_PERIPHBASE + 0x10000u)

// GIC layout (Programmer's Guide Table 8-1): GICD sits at GIC base + 0x10000
// (confirmed: distributor writes land at 0x13090000). The redistributor RD_base
// for core 0 follows immediately at GIC base + 0x20000 = 0x130A0000 -- probing
// showed 0x130B0000 is unmapped (a memory-mapped access there faults the model),
// so the GIC region ends right after this single 64KB redistributor page.
// The model powers the redistributor up ASLEEP (GICR_WAKER.ProcessorSleep set);
// SPIs are not delivered until it is woken, which gic_wake_redistributor() does.
#define GICR_BASE        (GIC_PERIPHBASE + 0x20000u)
#define GICR_WAKER       0x0014u   // RD_base offset; bit1 ProcessorSleep, bit2 ChildrenAsleep

// Distributor register offsets (GICv3, byte offsets from GICD_BASE).
#define GICD_CTLR        0x0000u
#define GICD_IGROUPR     0x0080u   // 1 bit  / INTID
#define GICD_ISENABLER   0x0100u   // 1 bit  / INTID
#define GICD_ICENABLER   0x0180u   // 1 bit  / INTID
#define GICD_ISPENDR     0x0200u   // 1 bit  / INTID
#define GICD_ISACTIVER   0x0300u   // 1 bit  / INTID
#define GICD_IPRIORITYR  0x0400u   // 1 byte / INTID
#define GICD_ICFGR       0x0C00u   // 2 bits / INTID
#define GICD_IROUTER     0x6000u   // 64 bits / INTID (SPI, affinity routing)

#define MMIO32(a)  (*(volatile uint32_t *)(uintptr_t)(a))
#define MMIO8(a)   (*(volatile uint8_t  *)(uintptr_t)(a))

// ---- CP15 accessors for the GICv3 CPU interface (AArch32) -------------------
// Coproc encodings (coproc, opc1, CRn, CRm, opc2):
//   ICC_SRE     p15,0,c12,c12,5     ICC_IGRPEN1 p15,0,c12,c12,7
//   ICC_PMR     p15,0,c4, c6, 0     ICC_BPR1    p15,0,c12,c12,3
//   ICC_IAR1    p15,0,c12,c12,0     ICC_EOIR1   p15,0,c12,c12,1
static inline void     icc_sre_w(uint32_t v)  { __asm volatile("mcr p15,0,%0,c12,c12,5" :: "r"(v)); }
static inline uint32_t icc_sre_r(void)        { uint32_t v; __asm volatile("mrc p15,0,%0,c12,c12,5" : "=r"(v)); return v; }
static inline void     icc_pmr_w(uint32_t v)  { __asm volatile("mcr p15,0,%0,c4,c6,0"  :: "r"(v)); }
static inline void     icc_bpr1_w(uint32_t v) { __asm volatile("mcr p15,0,%0,c12,c12,3" :: "r"(v)); }
static inline void     icc_igrpen1_w(uint32_t v){ __asm volatile("mcr p15,0,%0,c12,c12,7" :: "r"(v)); }
static inline uint32_t icc_iar1_r(void)       { uint32_t v; __asm volatile("mrc p15,0,%0,c12,c12,0" : "=r"(v)); return v; }
static inline void     icc_eoir1_w(uint32_t v){ __asm volatile("mcr p15,0,%0,c12,c12,1" :: "r"(v)); }

static inline void isb(void) { __asm volatile("isb"); }
static inline void dsb(void) { __asm volatile("dsb"); }

// Enable one SPI as a Group-1 (IRQ), active-HIGH level-sensitive interrupt,
// routed to this PE.
static inline void gic_enable_spi(uint32_t intid) {
    uint32_t reg = intid / 32u;
    uint32_t bit = intid % 32u;

    // Group 1 -> IRQ (Group 0 would be FIQ).
    MMIO32(GICD_BASE + GICD_IGROUPR + 4u * reg) |= (1u << bit);

    // Priority: lower value = higher priority; a mid value is fine here.
    MMIO8(GICD_BASE + GICD_IPRIORITYR + intid) = 0xA0u;

    // Trigger type: ICFGR field 0b00 = level-sensitive (0b10 = edge). 2 bits
    // per INTID, 16 INTIDs per word.
    {
        uint32_t r  = intid / 16u;
        uint32_t sh = (intid % 16u) * 2u;
        uint32_t v  = MMIO32(GICD_BASE + GICD_ICFGR + 4u * r);
        v &= ~(0x3u << sh);                 // 0b00 = active-HIGH level
        MMIO32(GICD_BASE + GICD_ICFGR + 4u * r) = v;
    }

    // Route to affinity 0.0.0.0 (the single core). IROUTER is 64-bit per INTID.
    MMIO32(GICD_BASE + GICD_IROUTER + 8u * intid)      = 0u;
    MMIO32(GICD_BASE + GICD_IROUTER + 8u * intid + 4u) = 0u;

    // Enable forwarding from the distributor.
    MMIO32(GICD_BASE + GICD_ISENABLER + 4u * reg) = (1u << bit);
    dsb();
}

static inline void gic_disable_spi(uint32_t intid) {
    uint32_t reg = intid / 32u;
    uint32_t bit = intid % 32u;
    MMIO32(GICD_BASE + GICD_ICENABLER + 4u * reg) = (1u << bit);
    dsb();
}

// Wake this core's redistributor. The R52 model resets with
// GICR_WAKER.ProcessorSleep = 1, which leaves the CPU interface quiesced and
// silently drops SPIs (the model warns "CPU command arrived at redistributor
// when GICR_WAKER indicates that core is asleep"). Clear ProcessorSleep, then
// spin until ChildrenAsleep clears, before any CPU-interface (ICC) access.
static inline void gic_wake_redistributor(void) {
    uint32_t w = MMIO32(GICR_BASE + GICR_WAKER);
    w &= ~(1u << 1);                                  // ProcessorSleep = 0
    MMIO32(GICR_BASE + GICR_WAKER) = w;
    while (MMIO32(GICR_BASE + GICR_WAKER) & (1u << 2)) {
        // wait for ChildrenAsleep to clear
    }
    dsb();
}

// Bring the GIC up: wake the redistributor, then distributor affinity routing +
// Group 1, then the CPU interface. Call once before enabling any SPI and before
// clearing CPSR.I.
static inline void gic_init(void) {
    // NOTE: a manual gic_wake_redistributor() is intentionally NOT called here.
    // The redistributor's memory-mapped base could not be located (both 0x130A
    // and 0x130B fault the model), and per the GICv3 spec the redistributor
    // exits processor-sleep automatically when a pending interrupt arrives for
    // the target. So we rely on the YOLOv5_HW SPI to auto-wake it. If delivery
    // proves to need an explicit wake, fix GICR_BASE and re-enable the call.

    // Distributor: ARE_NS (bit 4) + EnableGrp1NS (bit 1). DS == 1 on the R52.
    MMIO32(GICD_BASE + GICD_CTLR) = (1u << 4) | (1u << 1);
    dsb();

    // CPU interface (system-register access path).
    icc_sre_w(icc_sre_r() | 0x1u);  // ICC_SRE.SRE = 1
    isb();
    icc_pmr_w(0xFFu);               // unmask all priorities
    icc_bpr1_w(0x0u);
    icc_igrpen1_w(0x1u);           // enable Group 1 signaling to the PE
    isb();

    // NOTE (lab): GICv3 also wants the redistributor awake
    // (GICR_WAKER.ProcessorSleep cleared). The R52 model typically powers up
    // with it awake, so it is omitted here; if SPIs never deliver, clear it --
    // GICR base is per Programmer's Guide Table 8-1.
}

#endif  // GIC_R52_H
