#include "YOLOv5Detector.h"

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstring>
#include <stdexcept>

std::vector<float> YOLOv5Detector::preprocess(const uint8_t* image,
                                              std::size_t length) const {
  if (length < static_cast<std::size_t>(kHeaderBytes)) {
    throw std::runtime_error("image container shorter than its header");
  }
  uint32_t magic = 0, src_w = 0, src_h = 0, channels = 0;
  std::memcpy(&magic, image + 0, 4);
  std::memcpy(&src_w, image + 4, 4);
  std::memcpy(&src_h, image + 8, 4);
  std::memcpy(&channels, image + 12, 4);
  if (magic != kImageMagic) {
    throw std::runtime_error("image container has a bad magic number");
  }
  if (channels != static_cast<uint32_t>(kChannels) || src_w == 0 ||
      src_h == 0) {
    throw std::runtime_error("image container has an unexpected geometry");
  }
  const std::size_t pixels_bytes =
      static_cast<std::size_t>(src_w) * src_h * kChannels;
  if (length < static_cast<std::size_t>(kHeaderBytes) + pixels_bytes) {
    throw std::runtime_error("image container is shorter than its header says");
  }
  const uint8_t* px = image + kHeaderBytes;  // RGB, HWC, row-major

  // Letterbox: scale the image to fit 640x640 while preserving its aspect ratio,
  // then center it on a 114-gray canvas. This is the preprocessing YOLOv5 was
  // trained with; a plain stretch (the earlier path) squashes wide KITTI frames
  // (1242x375) into a square and makes the detector miss most objects.
  const float r = std::min(static_cast<float>(kHeight) / src_h,
                           static_cast<float>(kWidth) / src_w);
  const int new_w = static_cast<int>(std::lround(src_w * r));
  const int new_h = static_cast<int>(std::lround(src_h * r));
  const int pad_x = (kWidth - new_w) / 2;
  const int pad_y = (kHeight - new_h) / 2;

  // Record the mapping so detect() can undo it on the output boxes.
  src_w_ = static_cast<float>(src_w);
  src_h_ = static_cast<float>(src_h);
  lb_scale_ = r;
  lb_pad_x_ = static_cast<float>(pad_x);
  lb_pad_y_ = static_cast<float>(pad_y);

  // Start every pixel at the gray fill; the resized image overwrites the
  // centered region below.
  const float pad_val = 114.0f / 255.0f;
  std::vector<float> out(
      static_cast<std::size_t>(kChannels) * kHeight * kWidth, pad_val);

  // Half-pixel-centered bilinear resize into the centered new_w x new_h region.
  const float scale_x = static_cast<float>(src_w) / new_w;
  const float scale_y = static_cast<float>(src_h) / new_h;
  const int max_x = static_cast<int>(src_w) - 1;
  const int max_y = static_cast<int>(src_h) - 1;

  for (int ly = 0; ly < new_h; ++ly) {
    const int oy = ly + pad_y;
    const float fy = (ly + 0.5f) * scale_y - 0.5f;
    const int y0 = static_cast<int>(std::floor(fy));
    const float wy = fy - y0;
    const int y0c = std::min(std::max(y0, 0), max_y);
    const int y1c = std::min(std::max(y0 + 1, 0), max_y);
    for (int lx = 0; lx < new_w; ++lx) {
      const int ox = lx + pad_x;
      const float fx = (lx + 0.5f) * scale_x - 0.5f;
      const int x0 = static_cast<int>(std::floor(fx));
      const float wx = fx - x0;
      const int x0c = std::min(std::max(x0, 0), max_x);
      const int x1c = std::min(std::max(x0 + 1, 0), max_x);

      const std::size_t row0 = static_cast<std::size_t>(y0c) * src_w;
      const std::size_t row1 = static_cast<std::size_t>(y1c) * src_w;
      for (int c = 0; c < kChannels; ++c) {
        const float p00 = px[(row0 + x0c) * kChannels + c];
        const float p01 = px[(row0 + x1c) * kChannels + c];
        const float p10 = px[(row1 + x0c) * kChannels + c];
        const float p11 = px[(row1 + x1c) * kChannels + c];
        const float top = p00 * (1.0f - wx) + p01 * wx;
        const float bot = p10 * (1.0f - wx) + p11 * wx;
        const float value = (top * (1.0f - wy) + bot * wy) / 255.0f;
        out[(static_cast<std::size_t>(c) * kHeight + oy) * kWidth + ox] = value;
      }
    }
  }
  return out;
}

Ort::SessionOptions YOLOv5Detector::MakeOptions() {
  Ort::SessionOptions options;
  options.SetIntraOpNumThreads(1);
  return options;
}

YOLOv5Detector::YOLOv5Detector(const std::string& model_path)
    : env_(ORT_LOGGING_LEVEL_WARNING, "yolov5_detector"),
      options_(MakeOptions()),
      session_(env_, model_path.c_str(), options_) {
  Ort::AllocatorWithDefaultOptions allocator;
  input_name_ = session_.GetInputNameAllocated(0, allocator).get();
  output_name_ = session_.GetOutputNameAllocated(0, allocator).get();
}

std::vector<Detection> YOLOv5Detector::detect(const float* input_chw,
                                              float conf_threshold,
                                              float iou_threshold) {
  const std::vector<int64_t> dims{1, kChannels, kHeight, kWidth};
  const size_t count =
      static_cast<size_t>(kChannels) * kHeight * kWidth;

  Ort::MemoryInfo memory =
      Ort::MemoryInfo::CreateCpu(OrtArenaAllocator, OrtMemTypeDefault);
  // ONNX Runtime does not modify the input; the const_cast only satisfies the
  // non-const pointer the tensor factory expects.
  Ort::Value input_tensor = Ort::Value::CreateTensor<float>(
      memory, const_cast<float*>(input_chw), count, dims.data(), dims.size());

  const char* input_names[] = {input_name_.c_str()};
  const char* output_names[] = {output_name_.c_str()};
  auto outputs = session_.Run(Ort::RunOptions{nullptr}, input_names,
                              &input_tensor, 1, output_names, 1);

  return postprocess(outputs[0].GetTensorData<float>(), conf_threshold,
                     iou_threshold);
}

std::vector<Detection> YOLOv5Detector::postprocess(const float* output,
                                                   float conf_threshold,
                                                   float iou_threshold) const {
  // A decoded candidate in corner form, kept for the IoU math in NMS.
  struct Candidate {
    float x1, y1, x2, y2;
    float score;
    int class_id;
  };

  // Decode every candidate above the confidence threshold. The exported model
  // already maps the box to 640-pixel xywh (center) form, so no anchor decode
  // is needed here: filter on objectness, pick the best class, then convert.
  std::vector<Candidate> candidates;
  for (int i = 0; i < kNumBoxes; ++i) {
    const float* p = output + static_cast<size_t>(i) * kStride;
    const float objectness = p[4];
    if (objectness < conf_threshold) {
      continue;  // objectness gate, as in YOLOv5
    }
    int best_class = 0;
    float best_class_score = p[5];
    for (int c = 1; c < kNumClasses; ++c) {
      if (p[5 + c] > best_class_score) {
        best_class_score = p[5 + c];
        best_class = c;
      }
    }
    const float score = objectness * best_class_score;
    if (score < conf_threshold) {
      continue;
    }
    const float cx = p[0];
    const float cy = p[1];
    const float w = p[2];
    const float h = p[3];
    candidates.push_back({cx - w * 0.5f, cy - h * 0.5f, cx + w * 0.5f,
                          cy + h * 0.5f, score, best_class});
  }

  // Non-Maximum Suppression, highest score first, suppressing only boxes of the
  // same class (per-class NMS, the class-offset trick YOLOv5 uses).
  std::sort(candidates.begin(), candidates.end(),
            [](const Candidate& a, const Candidate& b) {
              return a.score > b.score;
            });

  // Undo the letterbox on a 640-space coordinate to get an original-image pixel
  // (subtract the padding, divide by the scale), clamped to the image bounds.
  auto to_src_x = [this](float v) {
    return std::min(std::max((v - lb_pad_x_) / lb_scale_, 0.0f), src_w_);
  };
  auto to_src_y = [this](float v) {
    return std::min(std::max((v - lb_pad_y_) / lb_scale_, 0.0f), src_h_);
  };

  std::vector<Detection> detections;
  std::vector<char> suppressed(candidates.size(), 0);
  for (size_t i = 0; i < candidates.size(); ++i) {
    if (suppressed[i]) {
      continue;
    }
    const Candidate& a = candidates[i];
    // NMS runs in 640 letterbox space (an affine map preserves IoU ordering);
    // only the reported box is mapped back to original image coordinates.
    const float ox1 = to_src_x(a.x1);
    const float oy1 = to_src_y(a.y1);
    const float ox2 = to_src_x(a.x2);
    const float oy2 = to_src_y(a.y2);
    detections.push_back(
        {a.class_id, a.score, ox1, oy1, ox2 - ox1, oy2 - oy1});

    const float area_a = (a.x2 - a.x1) * (a.y2 - a.y1);
    for (size_t j = i + 1; j < candidates.size(); ++j) {
      if (suppressed[j] || candidates[j].class_id != a.class_id) {
        continue;
      }
      const Candidate& b = candidates[j];
      const float ix1 = std::max(a.x1, b.x1);
      const float iy1 = std::max(a.y1, b.y1);
      const float ix2 = std::min(a.x2, b.x2);
      const float iy2 = std::min(a.y2, b.y2);
      const float iw = std::max(0.0f, ix2 - ix1);
      const float ih = std::max(0.0f, iy2 - iy1);
      const float intersection = iw * ih;
      const float area_b = (b.x2 - b.x1) * (b.y2 - b.y1);
      const float iou = intersection / (area_a + area_b - intersection);
      if (iou > iou_threshold) {
        suppressed[j] = 1;
      }
    }
  }
  return detections;
}
