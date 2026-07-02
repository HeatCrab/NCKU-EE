#!/usr/bin/env bash
# Assemble my_work/, the curated set of files carried into the SoC Lab on a USB
# stick. The authoritative sources live in TaskC/ (built and tested on the Mac);
# this script copies the lab-bound subset into the layout the Project 1 import
# flow used (SystemC/ + ARMv8/common/), so my_work/ can always be regenerated
# instead of hand-synced. Run it again after editing any TaskC source.
set -euo pipefail

cd "$(dirname "$0")"
SRC=TaskC
OUT=my_work

rm -rf "$OUT"
mkdir -p "$OUT/SystemC" "$OUT/ARMv8/common" "$OUT/ARMv8/cpu0" "$OUT/model" \
         "$OUT/ort" "$OUT/testdata"

# SystemC sources imported into Virtualizer and built by FastBuild.
cp "$SRC/src/YOLOv5_HW.h" "$SRC/src/YOLOv5_HW.cpp" \
   "$SRC/src/YOLOv5Detector.h" "$SRC/src/YOLOv5Detector.cpp" \
   "$SRC/src/DMA2.h" "$SRC/src/DMA2.cpp" "$OUT/SystemC/"

# Bare-metal side (Task D). Shared headers + linker script in common/, the
# Cortex-R52 program in cpu0/, the Makefile at the ARMv8 root (run `make` there
# on the server, the same flow as Project 1). DMA2_regs.h is kept as the
# Project 1 register-map reference.
cp "$SRC/armv8/common/DMA2_regs.h" "$SRC/armv8/common/YOLOv5_HW_regs.h" \
   "$SRC/armv8/common/uart_pl011.h" "$SRC/armv8/common/gic_r52.h" \
   "$SRC/armv8/common/linker_r52.ld" "$OUT/ARMv8/common/"
cp "$SRC/armv8/cpu0/main.c" "$SRC/armv8/cpu0/startup_r52.S" "$OUT/ARMv8/cpu0/"
cp "$SRC/armv8/Makefile" "$OUT/ARMv8/"
if [[ -f "$SRC/armv8/cpu0/yolo_cpu0.elf" ]]; then
  cp "$SRC/armv8/cpu0/yolo_cpu0.elf" "$OUT/ARMv8/cpu0/"
fi

# Trained model the detector loads.
cp onnx/best.onnx "$OUT/model/"

# ONNX Runtime setup copied verbatim from the lab server (source the csh before
# building so the FastBuild picks up the include/lib paths).
cp "$SRC/scripts/ort_1270.csh" "$SRC/docs/README_ORT_1270.md" "$OUT/ort/"

# The three demo image containers, ready to load into RAM1.
cp "$SRC"/data/container_*.bin "$OUT/testdata/"

cp my_work_README.md "$OUT/README.md"

echo "packed $OUT/:"
find "$OUT" -type f | sort | sed 's/^/  /'
du -sh "$OUT" | sed 's/^/total /'
