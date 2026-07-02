// YOLOv5Detector: the C++ inference class the SystemC wrapper (Task C) drives.
//
// It wraps the trained YOLOv5l ONNX model behind a small interface: construct
// with the model path (loadModel), then call detect() on one preprocessed
// tensor to obtain the surviving bounding boxes after confidence filtering and
// Non-Maximum Suppression.
//
// The class deliberately has NO OpenCV dependency. preprocess() resizes from a
// raw RGB image carried in a small self-describing container (see below), and
// detect() consumes the resulting [1, 3, 640, 640] float32 CHW tensor, so the
// whole class builds on the SoC server where only ONNX Runtime is installed.
// This keeps the spec's loadModel/preprocess/detect interface while replacing
// its cv2.imread/cv2.resize steps, which are unavailable on the lab server.
//
// Image container the host writes into the shared memory RAM1 (little-endian).
// A fixed 16-byte header carries the original size, which is why the IP needs
// no SIZE control register: the module reads the header, learns width/height,
// then reads the pixel block.
//   offset 0  : uint32 magic = 'Y','5','I','M'  (0x4D493559)
//   offset 4  : uint32 width
//   offset 8  : uint32 height
//   offset 12 : uint32 channels (3)
//   offset 16 : width * height * 3 bytes, RGB, HWC, row-major, uint8

#ifndef YOLOV5_DETECTOR_H_
#define YOLOV5_DETECTOR_H_

// Include the flat header name and let the build's -I point at the directory
// that directly contains it. The location differs across installs (Homebrew:
// include/onnxruntime/, the lab's prebuilt linux-x64 release: include/, conda:
// include/onnxruntime/core/session/), so a fixed prefix here would not port.
#include <onnxruntime_cxx_api.h>

#include <cstdint>
#include <string>
#include <vector>

// One detected traffic object. Coordinates are in ORIGINAL image pixel space:
// preprocess() letterboxes the image into the 640x640 model input, and detect()
// maps the boxes back through that letterbox (undo padding, divide by the
// scale) so CPU_0 prints origin x, y and width, length directly on the source
// image, ready to draw without any further host-side rescaling.
struct Detection {
  int class_id;  // 0 Car, 1 Pedestrian, 2 Cyclist
  float score;   // objectness * class probability
  float x;       // origin x (left)
  float y;       // origin y (top)
  float w;       // width
  float h;       // height (length)
};

class YOLOv5Detector {
 public:
  static constexpr int kChannels = 3;
  static constexpr int kHeight = 640;
  static constexpr int kWidth = 640;
  static constexpr int kNumBoxes = 25200;
  static constexpr int kNumClasses = 3;
  static constexpr int kStride = 5 + kNumClasses;  // 8 values per candidate

  // Image container layout (see the file header for the field table).
  static constexpr uint32_t kImageMagic = 0x4D493559u;  // 'Y','5','I','M'
  static constexpr int kHeaderBytes = 16;

  // Defaults match the YOLOv5 detection defaults.
  static constexpr float kConfThreshold = 0.25f;
  static constexpr float kIouThreshold = 0.45f;

  explicit YOLOv5Detector(const std::string& model_path);

  // Turn one in-RAM image container into the [1, 3, 640, 640] CHW tensor
  // detect() expects: parse the header for the original size, letterbox the RGB
  // pixels into 640x640 (aspect-preserving bilinear resize centered on a 114
  // gray canvas, the way YOLOv5 was trained, instead of a plain stretch which
  // distorts wide images and starves the detector), scale to [0, 1], and lay
  // the channels out as CHW. The letterbox scale and padding are recorded so
  // detect() can map boxes back to original image coordinates.
  // Throws std::runtime_error on a malformed or too-short container.
  std::vector<float> preprocess(const uint8_t* image, std::size_t length) const;

  // Run inference on one preprocessed tensor [1, 3, 640, 640] and return the
  // detections that survive confidence filtering and Non-Maximum Suppression.
  std::vector<Detection> detect(const float* input_chw,
                                float conf_threshold = kConfThreshold,
                                float iou_threshold = kIouThreshold);

  const std::string& input_name() const { return input_name_; }
  const std::string& output_name() const { return output_name_; }

 private:
  // Configure the session before it is created (single intra-op thread keeps
  // the behavior simple and deterministic for the SystemC context).
  static Ort::SessionOptions MakeOptions();

  // Decode the raw [1, 25200, 8] output into boxes, then apply per-class NMS.
  std::vector<Detection> postprocess(const float* output, float conf_threshold,
                                     float iou_threshold) const;

  Ort::Env env_;
  Ort::SessionOptions options_;
  Ort::Session session_;
  std::string input_name_;
  std::string output_name_;

  // Letterbox geometry of the most recent preprocess(), used by postprocess()
  // to map detections back to original image pixels. Mutable so preprocess()
  // can stay logically const while recording the mapping for its paired
  // detect() call. (preprocess() then detect() are always called in sequence on
  // the same image, both in YOLOv5_HW and in the host tests.)
  mutable float lb_scale_ = 1.0f;  // resized / original
  mutable float lb_pad_x_ = 0.0f;  // left padding in the 640 canvas
  mutable float lb_pad_y_ = 0.0f;  // top padding in the 640 canvas
  mutable float src_w_ = 0.0f;     // original image width
  mutable float src_h_ = 0.0f;     // original image height
};

#endif  // YOLOV5_DETECTOR_H_
