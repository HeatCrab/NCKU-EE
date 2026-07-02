"""
Produce the Python reference detections for YOLOv5Detector validation.

This is the postprocessing counterpart to Task B's make_reference.py. It loads
the preprocessed input.bin that Task B produced, runs the YOLOv5l ONNX model in
ONNX Runtime, then decodes the [1, 25200, 8] output into bounding boxes and
applies Non-Maximum Suppression. The detections are printed and written to
detections_ref.txt so the C++ testbench (detect_test) can confirm its own decode
and NMS reproduce these values.

No OpenCV is needed: input.bin is already preprocessed, so this reads raw
float32 and runs only ONNX Runtime plus NumPy. The algorithm mirrors
YOLOv5Detector.cpp exactly (objectness gate, best-class confidence, per-class
NMS) so a mismatch points to a C++ porting error rather than a model issue.
"""

import os

import numpy as np
import onnxruntime as ort

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.path.join(BASE, "..", "onnx", "best.onnx")
INPUT_BIN = os.path.join(BASE, "..", "TaskB", "data", "input.bin")
DATA_DIR = os.path.join(BASE, "data")
REF_DETECTIONS = os.path.join(DATA_DIR, "detections_ref.txt")

CHANNELS, HEIGHT, WIDTH = 3, 640, 640
NUM_CLASSES = 3
CONF_THRESHOLD = 0.25
IOU_THRESHOLD = 0.45
CLASS_NAMES = ["Car", "Pedestrian", "Cyclist"]


def iou(box, boxes):
    # box and boxes are in corner form [x1, y1, x2, y2].
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
    # output: [25200, 8] = cx, cy, w, h, objectness, class scores...
    objectness = output[:, 4]
    keep = objectness >= CONF_THRESHOLD
    output = output[keep]
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
        same_class = (class_id[rest] == class_id[i]) & ~suppressed[rest]
        rest = rest[same_class]
        if rest.size:
            overlap = iou(corners[i], corners[rest])
            suppressed[rest[overlap > IOU_THRESHOLD]] = True
    return detections


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    inp = np.fromfile(INPUT_BIN, dtype=np.float32)
    inp = inp.reshape(1, CHANNELS, HEIGHT, WIDTH)

    sess = ort.InferenceSession(MODEL, providers=["CPUExecutionProvider"])
    in_name = sess.get_inputs()[0].name
    out_name = sess.get_outputs()[0].name
    out = sess.run([out_name], {in_name: inp})[0][0]  # [25200, 8]

    detections = postprocess(out)
    print(f"{len(detections)} detections")
    with open(REF_DETECTIONS, "w") as f:
        f.write(f"{len(detections)}\n")
        for class_id, score, corner in detections:
            x, y = corner[0], corner[1]
            w, h = corner[2] - corner[0], corner[3] - corner[1]
            name = CLASS_NAMES[class_id]
            print(
                f"  {name} score {score:.2f} "
                f"origin ({x:.2f}, {y:.2f}) size {w:.2f} x {h:.2f}"
            )
            f.write(f"{class_id} {score:.6f} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")
    print(f"wrote {REF_DETECTIONS}")


if __name__ == "__main__":
    main()
