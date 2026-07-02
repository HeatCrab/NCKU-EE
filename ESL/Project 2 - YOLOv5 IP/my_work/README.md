# Project 2 — Lab bundle (my_work)

Files carried into the SoC Lab. Regenerate with `../pack_my_work.sh`; the
authoritative, Mac-tested sources live in `../TaskC/`.

## Contents

```
SystemC/         imported into Virtualizer, built by FastBuild
  YOLOv5_HW.h/.cpp        the co-processor IP (SRC/DST/START + RST/INT,
                          morphed from DMA2, masters the bus itself)
  YOLOv5Detector.h/.cpp   OpenCV-free C++ core: preprocess() + detect()
  DMA2.h/.cpp             Project 1 DMA, available if a separate DMA is used
ARMv8/common/
  DMA2_regs.h             register-map reference for the bare-metal side
model/
  best.onnx               trained YOLOv5l (opset 12, 1x3x640x640)
ort/
  ort_1270.csh            source this before building (sets ORT include/lib)
  README_ORT_1270.md      server ONNX Runtime notes
testdata/
  container_*.bin         the three demo images for RAM1 (002071, 003379,
                          005872; each 1242x375)
```

## Image container format (host -> RAM1)

Little-endian, 16-byte header then raw RGB pixels. The header carries the size,
which is why the IP needs no SIZE control register.

```
offset 0  : uint32 magic = 0x4D493559  ('Y','5','I','M')
offset 4  : uint32 width
offset 8  : uint32 height
offset 12 : uint32 channels (3)
offset 16 : width * height * 3 bytes, RGB, HWC, row-major, uint8
```

## Result format (IP -> RAM1 at DST)

```
offset 0  : uint32 count
then count records of 24 bytes:
  int32 class_id, float score, float x, float y, float w, float h
```
Coordinates are in the 640x640 model space (origin x/y + width/length).

## Build / import at the lab

1. `source ort/ort_1270.csh` so the include/lib paths are set.
2. Import `SystemC/YOLOv5_HW.*` into a fresh R52 platform (see Project 1 import
   flow); add `YOLOv5Detector.*` to the build, link ONNX Runtime.
3. Map the control registers (SRC 0x0 / DST 0x4 / START 0x8) and wire INT to
   the R52 nIRQ via the SpecFlow Interrupt Table.

## Still to add (Task D)

- `ARMv8/common/YOLOv5_HW_regs.h` and the Cortex-R52 trigger program: write
  SRC/DST/START, handle the INT in an ISR, read back `[count][boxes]` from DST.
  Absolute addresses come from the memory map fixed in Virtualizer at the lab.
