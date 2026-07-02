"""
Host-side image -> container converter for the demo.

The IP consumes the raw RGB container (16-byte header + pixels) described in
YOLOv5Detector.h, never a PNG, because the lab server cannot decode one. This
script decodes a PNG with OpenCV on the host and writes container_<stem>.bin,
ready to load into RAM1. Decoding is the only OpenCV use and it stays on the
host, exactly where Task B's preprocessing lived.

The demo shows three images; the three below were picked for it (002071 is the
one Task C validated end to end). Edit the list to use different images.

Run from TaskC/:  python scripts/make_containers.py
Output:           data/container_<stem>.bin for each listed image
"""

import os
import struct

import cv2

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_DIR = os.path.join(BASE, "..", "test_images", "extracted")
DATA_DIR = os.path.join(BASE, "data")

MAGIC = 0x4D493559  # 'Y','5','I','M'
IMAGES = ["002071", "003379", "005872"]


def write_container(path, rgb):
    h, w, c = rgb.shape
    with open(path, "wb") as f:
        f.write(struct.pack("<IIII", MAGIC, w, h, c))
        f.write(rgb.tobytes())
    return w, h


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    for stem in IMAGES:
        image = os.path.join(IMAGE_DIR, f"{stem}.png")
        bgr = cv2.imread(image, cv2.IMREAD_COLOR)
        if bgr is None:
            raise FileNotFoundError(image)
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        out = os.path.join(DATA_DIR, f"container_{stem}.bin")
        w, h = write_container(out, rgb)
        print(f"{stem}: {w}x{h} -> {os.path.basename(out)} "
              f"({16 + w * h * 3} bytes)")


if __name__ == "__main__":
    main()
