import cv2
import numpy as np

class SIFT:
    def __init__(self):
        self.sift = cv2.SIFT_create()

    def find_and_draw_keypoints(self, img_color):
        gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
        keypoints, _ = self.sift.detectAndCompute(gray, None)
        img_with_keypoints = cv2.drawKeypoints(gray, keypoints, gray, color=(0, 255, 0))
        return img_with_keypoints

    def match_and_draw_keypoints(self, img1_color, img2_color):
        gray1 = cv2.cvtColor(img1_color, cv2.COLOR_BGR2GRAY)
        kp1, des1 = self.sift.detectAndCompute(gray1, None)

        gray2 = cv2.cvtColor(img2_color, cv2.COLOR_BGR2GRAY)
        kp2, des2 = self.sift.detectAndCompute(gray2, None)

        # Match keypoints using BFMatcher
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1, des2, k=2)

        # Apply Lowe's ratio test
        good_matches = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good_matches.append([m])

        img_matches = cv2.drawMatchesKnn(img1_color, kp1, img2_color, kp2,
                                         good_matches, None,
                                         flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

        return img_matches