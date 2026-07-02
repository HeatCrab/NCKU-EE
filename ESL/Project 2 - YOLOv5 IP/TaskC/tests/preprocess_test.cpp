// Host validation of YOLOv5Detector::preprocess() (the OpenCV-free resize the
// IP performs in hardware). It reads the raw image container that
// make_container.py wrote, runs preprocess(), and checks two things:
//
//   1. the produced [1,3,640,640] tensor matches preprocess_ref.bin, the NumPy
//      bilinear resize that mirrors the same arithmetic; and
//   2. preprocess() + detect() together reproduce the Python detections in
//      detections_container_ref.txt.
//
// A PASS means the whole in-RAM-image -> tensor -> boxes path the SystemC
// module will drive is correct on the host, where it can still be debugged.
//
// Run from TaskC/ (build.sh does):
//   python scripts/make_container.py   # -> data/container.bin + refs
//   scripts/build.sh                   # -> bin/preprocess_test
//   bin/preprocess_test                # -> tensor diff, boxes, PASS / FAIL

#include "YOLOv5Detector.h"

#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

namespace {

const std::string kModel = "../onnx/best.onnx";
const std::string kContainer = "data/container.bin";
const std::string kPreprocessRef = "data/preprocess_ref.bin";
const std::string kRefDetections = "data/detections_container_ref.txt";

const char* kClassNames[] = {"Car", "Pedestrian", "Cyclist"};

constexpr float kTensorTolerance = 1e-4f;  // same algorithm, float noise only
constexpr float kScoreTolerance = 1e-3f;
constexpr float kCoordTolerance = 0.5f;  // pixels in 640 space

std::vector<uint8_t> ReadBytes(const std::string& path) {
  std::ifstream file(path, std::ios::binary | std::ios::ate);
  if (!file) {
    throw std::runtime_error("cannot open " + path);
  }
  const std::streamsize bytes = file.tellg();
  file.seekg(0, std::ios::beg);
  std::vector<uint8_t> data(static_cast<size_t>(bytes));
  file.read(reinterpret_cast<char*>(data.data()), bytes);
  return data;
}

std::vector<float> ReadFloats(const std::string& path) {
  std::ifstream file(path, std::ios::binary | std::ios::ate);
  if (!file) {
    throw std::runtime_error("cannot open " + path);
  }
  const std::streamsize bytes = file.tellg();
  file.seekg(0, std::ios::beg);
  std::vector<float> data(static_cast<size_t>(bytes) / sizeof(float));
  file.read(reinterpret_cast<char*>(data.data()), bytes);
  return data;
}

std::vector<Detection> ReadReference(const std::string& path) {
  std::ifstream file(path);
  if (!file) {
    throw std::runtime_error("cannot open " + path +
                             " (run make_container.py first)");
  }
  size_t n = 0;
  file >> n;
  std::vector<Detection> out(n);
  for (size_t i = 0; i < n; ++i) {
    file >> out[i].class_id >> out[i].score >> out[i].x >> out[i].y >>
        out[i].w >> out[i].h;
  }
  return out;
}

void Print(const std::string& tag, const std::vector<Detection>& dets) {
  std::cout << tag << " : " << dets.size() << " detections\n";
  std::cout << std::fixed << std::setprecision(2);
  for (size_t i = 0; i < dets.size(); ++i) {
    const Detection& d = dets[i];
    const char* name =
        (d.class_id >= 0 && d.class_id < 3) ? kClassNames[d.class_id] : "?";
    std::cout << "  [" << i << "] " << name << " score " << d.score
              << " origin (" << d.x << ", " << d.y << ") size " << d.w << " x "
              << d.h << "\n";
  }
}

bool Match(const std::vector<Detection>& a, const std::vector<Detection>& b) {
  if (a.size() != b.size()) {
    return false;
  }
  for (size_t i = 0; i < a.size(); ++i) {
    if (a[i].class_id != b[i].class_id) return false;
    if (std::fabs(a[i].score - b[i].score) > kScoreTolerance) return false;
    if (std::fabs(a[i].x - b[i].x) > kCoordTolerance) return false;
    if (std::fabs(a[i].y - b[i].y) > kCoordTolerance) return false;
    if (std::fabs(a[i].w - b[i].w) > kCoordTolerance) return false;
    if (std::fabs(a[i].h - b[i].h) > kCoordTolerance) return false;
  }
  return true;
}

}  // namespace

int main() {
  try {
    YOLOv5Detector detector(kModel);

    const std::vector<uint8_t> container = ReadBytes(kContainer);
    const std::vector<float> tensor =
        detector.preprocess(container.data(), container.size());

    // 1. Tensor vs NumPy reference.
    const std::vector<float> ref = ReadFloats(kPreprocessRef);
    bool tensor_ok = tensor.size() == ref.size();
    float max_abs = 0.0f;
    if (tensor_ok) {
      for (size_t i = 0; i < tensor.size(); ++i) {
        max_abs = std::max(max_abs, std::fabs(tensor[i] - ref[i]));
      }
      tensor_ok = max_abs <= kTensorTolerance;
    }
    std::cout << "tensor : " << tensor.size() << " floats, max abs diff "
              << std::scientific << max_abs << "\n"
              << std::defaultfloat;

    // 2. preprocess() + detect() vs Python reference.
    const std::vector<Detection> detections = detector.detect(tensor.data());
    Print("C++   ", detections);
    const std::vector<Detection> reference = ReadReference(kRefDetections);
    Print("Python", reference);

    const bool pass = tensor_ok && Match(detections, reference);
    std::cout << (pass ? "PASS" : "FAIL") << "\n";
    return pass ? 0 : 1;
  } catch (const std::exception& error) {
    std::cerr << "error: " << error.what() << "\n";
    return 2;
  }
}
