// Host validation of YOLOv5Detector postprocessing (decode + Non-Maximum
// Suppression). It reuses the preprocessed input.bin that Task B's
// make_reference.py produced, so no OpenCV is needed: the tensor is already
// prepared. The detections are checked against a Python reference produced by
// make_detections.py, the same way Task B checked raw outputs. A PASS means the
// C++ decode and NMS reproduce the Python result on the same model and input.
//
// Run from TaskC/ (build.sh does):
//   python scripts/make_detections.py  # -> data/detections_ref.txt
//   scripts/build.sh                   # -> bin/detect_test
//   bin/detect_test                    # -> per-box listing then PASS / FAIL

#include "YOLOv5Detector.h"

#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

namespace {

// data/input.bin is produced by Task B and shared from there (regenerable,
// gitignored).
const std::string kModel = "../onnx/best.onnx";
const std::string kInputBin = "../TaskB/data/input.bin";
const std::string kRefDetections = "data/detections_ref.txt";

const char* kClassNames[] = {"Car", "Pedestrian", "Cyclist"};

// Matching tolerances: the C++ and Python paths run the same model on the same
// input with the same algorithm, so agreement is exact up to float noise.
constexpr float kScoreTolerance = 1e-3f;
constexpr float kCoordTolerance = 0.5f;  // pixels in 640 space

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
                             " (run make_detections.py first)");
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

// Compare two detection lists already ordered by descending score.
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
    std::cout << "input node  : " << detector.input_name() << "\n";
    std::cout << "output node : " << detector.output_name() << "\n";

    std::vector<float> input = ReadFloats(kInputBin);
    const size_t expected = static_cast<size_t>(YOLOv5Detector::kChannels) *
                            YOLOv5Detector::kHeight * YOLOv5Detector::kWidth;
    if (input.size() != expected) {
      throw std::runtime_error("input.bin has " + std::to_string(input.size()) +
                               " floats, expected " + std::to_string(expected));
    }

    std::vector<Detection> detections = detector.detect(input.data());
    Print("C++   ", detections);

    std::vector<Detection> reference = ReadReference(kRefDetections);
    Print("Python", reference);

    const bool pass = Match(detections, reference);
    std::cout << (pass ? "PASS" : "FAIL") << "\n";
    return pass ? 0 : 1;
  } catch (const std::exception& error) {
    std::cerr << "error: " << error.what() << "\n";
    return 2;
  }
}
