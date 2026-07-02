#ifndef YOLOV5_HW_REGS_H
#define YOLOV5_HW_REGS_H

// Register map and data formats for the YOLOv5_HW co-processor, as fixed in the
// Virtualizer platform (Yolo.vdksys). All addresses are absolute on the
// Cortex-R52 system bus; the report's memory-map section is derived from here.
//
//   RAM0  0x0000_0000  local: R52 code + test image containers
//   RAM1  0x0800_0000  shared: image under test + inference result
//   YOLO  0x1000_0000  control registers (SRC/DST/START)
//   UART  0x4000_0000  PL011 (template default)

#include <stdint.h>

// ---- YOLOv5_HW control registers (Ssocket, base 0x1000_0000) ----------------
// Three 32-bit registers, word access only. There is deliberately no SIZE
// register: the image container's 16-byte header carries width/height, so the
// IP derives the byte count itself (the spec's "like a DMA, minus SIZE").
#define YOLO_BASE        0x10000000u
#define YOLO_SRC         (YOLO_BASE + 0x0u)  // input container address (in RAM1)
#define YOLO_DST         (YOLO_BASE + 0x4u)  // result address (in RAM1)
#define YOLO_START       (YOLO_BASE + 0x8u)  // write 1 to launch, 0 to re-arm

// ---- Memory regions ---------------------------------------------------------
#define RAM0_BASE        0x00000000u
#define RAM1_BASE        0x08000000u

// ---- Interrupt --------------------------------------------------------------
// YOLOv5_HW.INT -> R52 GIC SPI line 0 -> INTID 32 (SPIs start at 32).
#define YOLO_INTID       32u

// ---- Image container layout (host -> RAM1), little-endian -------------------
// offset 0   uint32 magic = 0x4D493559 ('Y','5','I','M')
// offset 4   uint32 width
// offset 8   uint32 height
// offset 12  uint32 channels (3)
// offset 16  width*height*3 bytes, RGB, HWC, row-major, uint8
#define YOLO_IMG_MAGIC   0x4D493559u
#define YOLO_HDR_BYTES   16u

// ---- Result layout (IP -> RAM1 at DST) --------------------------------------
// offset 0   uint32 count
// then `count` records of 24 bytes each:
//   int32 class_id, float score, float x, float y, float w, float h
// Coordinates are in 640x640 model space (origin x/y + width/length).
#define YOLO_REC_BYTES   24u
#define YOLO_REC_OFF_CLASS  0u
#define YOLO_REC_OFF_SCORE  4u
#define YOLO_REC_OFF_X      8u
#define YOLO_REC_OFF_Y      12u
#define YOLO_REC_OFF_W      16u
#define YOLO_REC_OFF_H      20u

#endif  // YOLOV5_HW_REGS_H
