// Task B testbench: verify that best.onnx runs correctly on the local machine.
//
// The script make_reference.py produced two raw float32 files in Python:
//   data/input.bin   - the preprocessed input tensor [1, 3, 640, 640]
//   data/ref_out.bin - the output tensor [1, 25200, 8] returned by ONNX Runtime
//
// This testbench performs two checks, both against the values seen in Python:
//
//   1. Functional Validation. Load input.bin, Run Inference with the C++ ONNX
//      Runtime, and Check Values: the output must match ref_out.bin. This
//      confirms the model produces identical results in C++ and Python.
//
//   2. Preprocessing parity. Read the same test image with OpenCV, reproduce
//      the preprocessing (resize to 640x640, BGR to RGB, scale to [0,1],
//      HWC to CHW), and confirm the resulting tensor matches input.bin. This
//      isolates any future preprocessing issue from the model itself.
//
// Both checks use the same maximum-absolute-difference tolerance.

#include <onnxruntime/onnxruntime_cxx_api.h>

#include <opencv2/opencv.hpp>

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

namespace {

constexpr int kChannels = 3;
constexpr int kHeight = 640;
constexpr int kWidth = 640;

// The output tensor spans two scales: class and objectness scores in [0, 1] and
// bounding-box coordinates up to the 640-pixel image extent. A flat absolute
// tolerance cannot fit both, so the values are compared the way numpy.allclose
// does, |a - b| <= atol + rtol * |b|, which judges large values by their
// relative agreement. A genuine inference error differs by orders of magnitude,
// far beyond these bounds; cross-version floating-point noise stays well within.
constexpr float kAbsTolerance = 1e-4f;
constexpr float kRelTolerance = 1e-3f;

// Paths are relative to this directory; run the testbench from TaskB/ (as
// build.sh and make_reference.py do) so it works on any machine without
// editing absolute paths.
const std::string kModel = "../onnx/best.onnx";
const std::string kImage = "../test_images/extracted/002071.png";
const std::string kInputBin = "data/input.bin";
const std::string kRefOutBin = "data/ref_out.bin";

// Read a raw float32 file into a vector.
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

// Maximum absolute difference between two equally sized buffers.
float MaxAbsDiff(const std::vector<float>& a, const std::vector<float>& b) {
  if (a.size() != b.size()) {
    throw std::runtime_error("size mismatch: " + std::to_string(a.size()) +
                             " vs " + std::to_string(b.size()));
  }
  float worst = 0.0f;
  for (size_t i = 0; i < a.size(); ++i) {
    worst = std::max(worst, std::fabs(a[i] - b[i]));
  }
  return worst;
}

// Maximum relative difference, |a - b| / |b|, ignoring near-zero reference
// values where a relative measure is undefined.
float MaxRelDiff(const std::vector<float>& a, const std::vector<float>& b) {
  float worst = 0.0f;
  for (size_t i = 0; i < a.size(); ++i) {
    const float denom = std::fabs(b[i]);
    if (denom > 1.0f) {
      worst = std::max(worst, std::fabs(a[i] - b[i]) / denom);
    }
  }
  return worst;
}

// numpy.allclose semantics: every element within atol + rtol * |reference|.
bool AllClose(const std::vector<float>& a, const std::vector<float>& b,
              float atol, float rtol) {
  for (size_t i = 0; i < a.size(); ++i) {
    if (std::fabs(a[i] - b[i]) > atol + rtol * std::fabs(b[i])) {
      return false;
    }
  }
  return true;
}

// Reproduce make_reference.py preprocessing and return a CHW tensor.
std::vector<float> Preprocess(const std::string& path) {
  cv::Mat img = cv::imread(path, cv::IMREAD_COLOR);  // BGR, HWC, uint8
  if (img.empty()) {
    throw std::runtime_error("cannot read image " + path);
  }
  cv::resize(img, img, cv::Size(kWidth, kHeight), 0, 0, cv::INTER_LINEAR);
  cv::cvtColor(img, img, cv::COLOR_BGR2RGB);
  img.convertTo(img, CV_32F, 1.0 / 255.0);

  // HWC to CHW: split into channels and lay them out channel-major.
  std::vector<cv::Mat> channels(kChannels);
  cv::split(img, channels);
  std::vector<float> chw(static_cast<size_t>(kChannels) * kHeight * kWidth);
  const size_t plane = static_cast<size_t>(kHeight) * kWidth;
  for (int c = 0; c < kChannels; ++c) {
    std::memcpy(chw.data() + c * plane, channels[c].data, plane * sizeof(float));
  }
  return chw;
}

}  // namespace

int main() {
  try {
    Ort::Env env(ORT_LOGGING_LEVEL_WARNING, "verify_onnx");
    Ort::SessionOptions options;
    options.SetIntraOpNumThreads(1);  // Keep it simple for the SystemC context.
    Ort::Session session(env, kModel.c_str(), options);
    Ort::AllocatorWithDefaultOptions allocator;

    // Inspect Model Metadata: input and output node counts and shapes.
    const size_t input_count = session.GetInputCount();
    const size_t output_count = session.GetOutputCount();
    std::cout << "inputs : " << input_count << ", outputs : " << output_count
              << "\n";

    auto input_name = session.GetInputNameAllocated(0, allocator);
    auto output_name = session.GetOutputNameAllocated(0, allocator);
    const auto input_shape = session.GetInputTypeInfo(0)
                                 .GetTensorTypeAndShapeInfo()
                                 .GetShape();
    const auto output_shape = session.GetOutputTypeInfo(0)
                                  .GetTensorTypeAndShapeInfo()
                                  .GetShape();

    auto print_shape = [](const std::string& label, const char* name,
                          const std::vector<int64_t>& shape) {
      std::cout << label << " : " << name << " [";
      for (size_t i = 0; i < shape.size(); ++i) {
        std::cout << shape[i] << (i + 1 < shape.size() ? ", " : "");
      }
      std::cout << "]\n";
    };
    print_shape("input node ", input_name.get(), input_shape);
    print_shape("output node", output_name.get(), output_shape);

    // Run Inference on the input tensor seen in Python.
    std::vector<float> input = ReadFloats(kInputBin);
    const std::vector<int64_t> dims{1, kChannels, kHeight, kWidth};
    Ort::MemoryInfo memory =
        Ort::MemoryInfo::CreateCpu(OrtArenaAllocator, OrtMemTypeDefault);
    Ort::Value input_tensor = Ort::Value::CreateTensor<float>(
        memory, input.data(), input.size(), dims.data(), dims.size());

    const char* input_names[] = {input_name.get()};
    const char* output_names[] = {output_name.get()};
    auto outputs = session.Run(Ort::RunOptions{nullptr}, input_names,
                               &input_tensor, 1, output_names, 1);

    const float* output_data = outputs[0].GetTensorData<float>();
    const size_t output_size = outputs[0]
                                   .GetTensorTypeAndShapeInfo()
                                   .GetElementCount();
    std::vector<float> output(output_data, output_data + output_size);

    // Print the leading output values so they can be read against the values
    // printed by make_reference.py in Python.
    std::cout << "output[:8] =";
    for (size_t i = 0; i < 8 && i < output.size(); ++i) {
      std::cout << " " << output[i];
    }
    std::cout << "\n";

    // Check Values: C++ output versus the values seen in Python.
    std::vector<float> reference = ReadFloats(kRefOutBin);
    const bool output_ok =
        AllClose(output, reference, kAbsTolerance, kRelTolerance);
    std::cout << "output max abs diff : " << MaxAbsDiff(output, reference)
              << ", max rel diff : " << MaxRelDiff(output, reference) << "\n";

    // Preprocessing parity: C++ preprocessing versus input.bin. The values lie
    // in [0, 1], so the absolute tolerance alone is the right measure here.
    std::vector<float> preprocessed = Preprocess(kImage);
    const float input_diff = MaxAbsDiff(preprocessed, input);
    const bool input_ok = input_diff < kAbsTolerance;
    std::cout << "input  max abs diff : " << input_diff << "\n";

    const bool pass = output_ok && input_ok;
    std::cout << (pass ? "PASS" : "FAIL") << "\n";
    return pass ? 0 : 1;
  } catch (const std::exception& error) {
    std::cerr << "error: " << error.what() << "\n";
    return 2;
  }
}
