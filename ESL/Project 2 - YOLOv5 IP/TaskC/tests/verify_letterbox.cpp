// Standalone check that the letterbox preprocess + scale-back in YOLOv5Detector
// recovers detections on the three demo containers, and reports boxes in
// original image pixels. Expected (from the Python ground-truth run):
//   002071 -> ~12 Cars, 003379 -> ~4, 005872 -> ~3.
//
// Build with the same flags as scripts/build.sh, then run from the TaskC dir.

#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

#include "YOLOv5Detector.h"

static std::vector<uint8_t> read_file(const std::string& path) {
  std::ifstream f(path, std::ios::binary);
  if (!f) throw std::runtime_error("cannot open " + path);
  return std::vector<uint8_t>((std::istreambuf_iterator<char>(f)),
                              std::istreambuf_iterator<char>());
}

int main(int argc, char** argv) {
  const std::string model =
      argc > 1 ? argv[1] : "../my_work/model/best.onnx";
  YOLOv5Detector det(model);

  const char* names[3] = {"Car", "Pedestrian", "Cyclist"};
  const char* ids[3] = {"002071", "003379", "005872"};

  for (const char* id : ids) {
    const std::string path = std::string("data/container_") + id + ".bin";
    std::vector<uint8_t> buf = read_file(path);
    std::vector<float> tensor = det.preprocess(buf.data(), buf.size());
    std::vector<Detection> dets = det.detect(tensor.data());

    int counts[3] = {0, 0, 0};
    for (const auto& d : dets)
      if (d.class_id >= 0 && d.class_id < 3) counts[d.class_id]++;

    std::cout << id << ": " << dets.size() << " detections  (Car " << counts[0]
              << " Ped " << counts[1] << " Cyc " << counts[2] << ")\n";
    for (const auto& d : dets) {
      std::cout << "    [" << names[d.class_id] << "] "
                << static_cast<int>(d.score * 100) << "%  origin("
                << static_cast<int>(d.x) << "," << static_cast<int>(d.y)
                << ") size(" << static_cast<int>(d.w) << "x"
                << static_cast<int>(d.h) << ")\n";
    }
  }
  return 0;
}
