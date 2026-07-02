"""
Produce the raw image container and the preprocessing reference for the
OpenCV-free YOLOv5Detector::preprocess() path.

The SoC server has no usable OpenCV, so the IP cannot decode a PNG nor call
cv2.resize. Instead the host writes an already-decoded image into RAM1 using a
small self-describing container (16-byte header carrying the original size, then
RGB HWC uint8 pixels), and the IP resizes it itself. This script builds that
container from one test image and, crucially, also produces the reference the
C++ preprocess() is checked against:

  * container.bin            the bytes the host would place in RAM1
  * preprocess_ref.bin       the [1,3,640,640] float32 tensor, produced by a
                             NumPy bilinear resize that mirrors the C++ math
  * detections_container_ref.txt  the detections from running the model on that
                             tensor, so preprocess()+detect() can be checked
                             end to end

cv2 is used here only to DECODE the PNG (a host-side convenience); the resize is
hand-written in NumPy so it matches the IP's hand-written C++ resize rather than
cv2's fixed-point INTER_LINEAR.
"""

import os
import struct

import cv2
import numpy as np
import onnxruntime as ort

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.path.join(BASE, "..", "onnx", "best.onnx")
IMAGE = os.path.join(BASE, "..", "test_images", "extracted", "002071.png")

DATA_DIR = os.path.join(BASE, "data")
CONTAINER_BIN = os.path.join(DATA_DIR, "container.bin")
PREPROCESS_REF = os.path.join(DATA_DIR, "preprocess_ref.bin")
REF_DETECTIONS = os.path.join(DATA_DIR, "detections_container_ref.txt")

MAGIC = 0x4D493559  # 'Y','5','I','M'
DST = 640
NUM_CLASSES = 3
CONF_THRESHOLD = 0.25
IOU_THRESHOLD = 0.45
CLASS_NAMES = ["Car", "Pedestrian", "Cyclist"]


def write_container(rgb):
    h, w, c = rgb.shape
    with open(CONTAINER_BIN, "wb") as f:
        f.write(struct.pack("<IIII", MAGIC, w, h, c))
        f.write(np.ascontiguousarray(rgb, dtype=np.uint8).tobytes())
    return w, h, c


def resize_bilinear(rgb):
    # Half-pixel-centre bilinear resize in float32, the exact arithmetic the C++
    # preprocess() performs, so the two tensors agree up to float noise.
    src_h, src_w, _ = rgb.shape
    src = rgb.astype(np.float32)
    scale_x = np.float32(src_w) / np.float32(DST)
    scale_y = np.float32(src_h) / np.float32(DST)

    oy = np.arange(DST, dtype=np.float32)
    fy = (oy + np.float32(0.5)) * scale_y - np.float32(0.5)
    y0 = np.floor(fy).astype(np.int32)
    wy = (fy - y0).astype(np.float32)
    y0c = np.clip(y0, 0, src_h - 1)
    y1c = np.clip(y0 + 1, 0, src_h - 1)

    ox = np.arange(DST, dtype=np.float32)
    fx = (ox + np.float32(0.5)) * scale_x - np.float32(0.5)
    x0 = np.floor(fx).astype(np.int32)
    wx = (fx - x0).astype(np.float32)
    x0c = np.clip(x0, 0, src_w - 1)
    x1c = np.clip(x0 + 1, 0, src_w - 1)

    # Gather the four neighbours for every output pixel, then interpolate in the
    # same order as the C++: first along x, then along y.
    p00 = src[np.ix_(y0c, x0c)]
    p01 = src[np.ix_(y0c, x1c)]
    p10 = src[np.ix_(y1c, x0c)]
    p11 = src[np.ix_(y1c, x1c)]
    wx_ = wx[None, :, None]
    wy_ = wy[:, None, None]
    top = p00 * (np.float32(1.0) - wx_) + p01 * wx_
    bot = p10 * (np.float32(1.0) - wx_) + p11 * wx_
    out = (top * (np.float32(1.0) - wy_) + bot * wy_) / np.float32(255.0)

    chw = np.transpose(out, (2, 0, 1))  # HWC -> CHW
    return np.ascontiguousarray(chw[None], dtype=np.float32)


def iou(box, boxes):
    ix1 = np.maximum(box[0], boxes[:, 0])
    iy1 = np.maximum(box[1], boxes[:, 1])
    ix2 = np.minimum(box[2], boxes[:, 2])
    iy2 = np.minimum(box[3], boxes[:, 3])
    iw = np.clip(ix2 - ix1, 0.0, None)
    ih = np.clip(iy2 - iy1, 0.0, None)
    inter = iw * ih
    area_box = (box[2] - box[0]) * (box[3] - box[1])
    area_boxes = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    return inter / (area_box + area_boxes - inter)


def postprocess(output):
    objectness = output[:, 4]
    output = output[objectness >= CONF_THRESHOLD]
    if output.shape[0] == 0:
        return []
    class_scores = output[:, 5 : 5 + NUM_CLASSES]
    class_id = np.argmax(class_scores, axis=1)
    score = output[:, 4] * class_scores[np.arange(output.shape[0]), class_id]
    keep = score >= CONF_THRESHOLD
    output, class_id, score = output[keep], class_id[keep], score[keep]

    cx, cy, w, h = output[:, 0], output[:, 1], output[:, 2], output[:, 3]
    corners = np.stack([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], axis=1)
    order = np.argsort(-score)
    corners, class_id, score = corners[order], class_id[order], score[order]

    detections = []
    suppressed = np.zeros(len(score), dtype=bool)
    for i in range(len(score)):
        if suppressed[i]:
            continue
        detections.append((int(class_id[i]), float(score[i]), corners[i]))
        rest = np.arange(i + 1, len(score))
        same = (class_id[rest] == class_id[i]) & ~suppressed[rest]
        rest = rest[same]
        if rest.size:
            overlap = iou(corners[i], corners[rest])
            suppressed[rest[overlap > IOU_THRESHOLD]] = True
    return detections


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    bgr = cv2.imread(IMAGE, cv2.IMREAD_COLOR)
    if bgr is None:
        raise FileNotFoundError(IMAGE)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    w, h, c = write_container(rgb)
    print(f"image : {os.path.normpath(IMAGE)}  ({w}x{h}x{c})")
    print(f"wrote {CONTAINER_BIN} ({16 + w * h * c} bytes)")

    inp = resize_bilinear(rgb)
    inp.tofile(PREPROCESS_REF)
    print(f"wrote {PREPROCESS_REF} ({inp.nbytes} bytes)")

    sess = ort.InferenceSession(MODEL, providers=["CPUExecutionProvider"])
    in_name = sess.get_inputs()[0].name
    out_name = sess.get_outputs()[0].name
    out = sess.run([out_name], {in_name: inp})[0][0]

    detections = postprocess(out)
    print(f"{len(detections)} detections")
    with open(REF_DETECTIONS, "w") as f:
        f.write(f"{len(detections)}\n")
        for class_id, score, corner in detections:
            x, y = corner[0], corner[1]
            bw, bh = corner[2] - corner[0], corner[3] - corner[1]
            print(
                f"  {CLASS_NAMES[class_id]} score {score:.2f} "
                f"origin ({x:.2f}, {y:.2f}) size {bw:.2f} x {bh:.2f}"
            )
            f.write(
                f"{class_id} {score:.6f} {x:.6f} {y:.6f} "
                f"{bw:.6f} {bh:.6f}\n"
            )
    print(f"wrote {REF_DETECTIONS}")


if __name__ == "__main__":
    main()
