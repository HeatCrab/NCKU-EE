"""
Produce the Python inference results for the YOLOv5l ONNX model.

Task B requires a C++ testbench whose inference results match the values seen in
Python. This script loads best.onnx in ONNX Runtime, preprocesses one test image
(resize to 640x640, BGR to RGB, scale to [0,1], HWC to CHW), runs inference, and
writes the preprocessed input and the output tensor to raw float32 files. The C++
testbench loads the same input and compares its output against these values.

Preprocessing follows the description literally (resize to 640x640). The C++ side
reproduces the identical steps, so any difference isolates a C++ implementation
issue rather than a model issue.
"""

import os

import cv2
import numpy as np
import onnxruntime as ort

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.path.join(BASE, "..", "onnx", "best.onnx")
IMAGE = os.path.join(BASE, "..", "test_images", "extracted", "002071.png")

DATA_DIR = os.path.join(BASE, "data")
INPUT_BIN = os.path.join(DATA_DIR, "input.bin")
REF_OUT_BIN = os.path.join(DATA_DIR, "ref_out.bin")


def preprocess(path):
    img = cv2.imread(path, cv2.IMREAD_COLOR)  # BGR, HWC, uint8
    if img is None:
        raise FileNotFoundError(path)
    img = cv2.resize(img, (640, 640), interpolation=cv2.INTER_LINEAR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32) / 255.0
    img = np.transpose(img, (2, 0, 1))  # HWC -> CHW
    img = np.expand_dims(img, 0)  # [1, 3, 640, 640]
    return np.ascontiguousarray(img, dtype=np.float32)


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    print(f"model : {os.path.normpath(MODEL)}")
    print(f"image : {os.path.normpath(IMAGE)}")

    inp = preprocess(IMAGE)
    print(f"input shape : {inp.shape}  dtype {inp.dtype}")

    sess = ort.InferenceSession(MODEL, providers=["CPUExecutionProvider"])
    in_name = sess.get_inputs()[0].name
    out_name = sess.get_outputs()[0].name
    print(f"input node  : {in_name} {sess.get_inputs()[0].shape}")
    print(f"output node : {out_name} {sess.get_outputs()[0].shape}")

    out = sess.run([out_name], {in_name: inp})[0]
    out = np.ascontiguousarray(out, dtype=np.float32)
    print(f"output shape: {out.shape}  dtype {out.dtype}")
    print(f"output[0,0,:8] = {out.reshape(-1)[:8]}")

    inp.tofile(INPUT_BIN)
    out.tofile(REF_OUT_BIN)
    print(f"wrote {INPUT_BIN} ({inp.nbytes} bytes)")
    print(f"wrote {REF_OUT_BIN} ({out.nbytes} bytes)")


if __name__ == "__main__":
    main()
