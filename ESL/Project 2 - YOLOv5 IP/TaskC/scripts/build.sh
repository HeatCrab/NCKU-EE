#!/usr/bin/env bash
# Build the Task C detector validation driver.
#
# Unlike Task B, this needs only ONNX Runtime: YOLOv5Detector consumes an
# already-preprocessed tensor, so there is no OpenCV dependency, the same
# situation as the SoC server, where only ONNX Runtime is installed. On the
# server, point ORT at the teacher-provided install instead of the Homebrew one.
set -euo pipefail

ORT=/opt/homebrew/opt/onnxruntime

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

mkdir -p bin

clang++ -std=c++17 -O2 tests/detect_test.cpp src/YOLOv5Detector.cpp \
  -o bin/detect_test \
  -Isrc \
  -I"$ORT/include/onnxruntime" \
  -L"$ORT/lib" -lonnxruntime \
  -Wl,-rpath,"$ORT/lib"

echo "built detect_test"

# preprocess_test exercises the OpenCV-free resize the IP performs in hardware
# (YOLOv5Detector::preprocess), driven by the raw image container.
clang++ -std=c++17 -O2 tests/preprocess_test.cpp src/YOLOv5Detector.cpp \
  -o bin/preprocess_test \
  -Isrc \
  -I"$ORT/include/onnxruntime" \
  -L"$ORT/lib" -lonnxruntime \
  -Wl,-rpath,"$ORT/lib"

echo "built preprocess_test"
