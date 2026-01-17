import cv2
import numpy as np
from .utils import show_image

class StereoDisparity:
    def __init__(self):
        self.stereo = cv2.StereoBM_create(numDisparities=432, blockSize=25)

    def compute(self, imgL_gray, imgR_gray):
        disparity = self.stereo.compute(imgL_gray, imgR_gray)
        disparity_normalized = cv2.normalize(disparity, None, alpha=0, beta=255,
                                             norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        return disparity_normalized