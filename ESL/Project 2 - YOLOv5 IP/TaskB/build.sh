#!/usr/bin/env bash
# Build the Task B testbench.
#
# ONNX Runtime comes from Homebrew; the OpenCV C++ SDK lives inside the conda
# env named "opencv" (the libopencv package). The rpath entries let the produced
# binary find both sets of dylibs at run time.
set -euo pipefail

ENV="$(conda info --base)/envs/opencv"
ORT=/opt/homebrew/opt/onnxruntime
export PKG_CONFIG_PATH="$ENV/lib/pkgconfig"

cd "$(dirname "$0")"

clang++ -std=c++17 -O2 verify_onnx.cpp -o verify_onnx \
  -I"$ORT/include" $(pkg-config --cflags opencv4) \
  -L"$ORT/lib" -lonnxruntime $(pkg-config --libs opencv4) \
  -Wl,-rpath,"$ORT/lib" -Wl,-rpath,"$ENV/lib"

echo "built verify_onnx"
