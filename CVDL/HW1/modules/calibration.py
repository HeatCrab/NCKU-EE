import cv2
import numpy as np
import glob
import os
from .utils import show_image, show_images_sequence

class CameraCalibration:
    def __init__(self):
        self.images = []
        self.image_paths = []
        self.corners_list = []
        self.camera_matrix = None
        self.dist_coeffs = None
        self.rvecs = []
        self.tvecs = []

        self.chessboard_size = (11, 8)
        self.square_size = 0.02

        # Prepare 3D object points
        self.objp = np.zeros((self.chessboard_size[0] * self.chessboard_size[1], 3), np.float32)
        self.objp[:, :2] = np.mgrid[0:self.chessboard_size[0],
                                     0:self.chessboard_size[1]].T.reshape(-1, 2)
        self.objp *= self.square_size

        self.objpoints = []
        self.imgpoints = []
        
    def load_images(self, folder_path):
        patterns = ['*.bmp', '*.jpg', '*.png']
        self.image_paths = []

        for pattern in patterns:
            search_path = os.path.join(folder_path, pattern)
            paths = sorted(glob.glob(search_path))
            self.image_paths.extend(paths)

        if not self.image_paths:
            print(f"No images found in {folder_path}")
            return False

        self.images = []
        for path in self.image_paths:
            img = cv2.imread(path)
            if img is not None:
                self.images.append(img)

        print(f"Loaded {len(self.images)} images")
        return len(self.images) > 0
    
    def find_corners(self, silent=False):
        if not self.images:
            print("Please load images first!")
            return False

        self.corners_list = []
        self.objpoints = []
        self.imgpoints = []

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        if not silent:
            print("\n=== Finding Corners ===")
            print("Press any key to see next image, or ESC to skip all")

        for idx, img in enumerate(self.images):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(gray, self.chessboard_size, None)

            if ret:
                # Refine corner positions
                corners_refined = cv2.cornerSubPix(
                    gray, corners,
                    winSize=(5, 5),
                    zeroZone=(-1, -1),
                    criteria=criteria
                )

                self.corners_list.append(corners_refined)
                self.objpoints.append(self.objp)
                self.imgpoints.append(corners_refined)

                if not silent:
                    # Display corners
                    img_with_corners = img.copy()
                    cv2.drawChessboardCorners(img_with_corners, self.chessboard_size,
                                            corners_refined, ret)

                    display_img = self._resize_for_display(img_with_corners)

                    text = f"Image {idx + 1}/{len(self.images)} - Press any key for next"
                    cv2.putText(display_img, text, (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                    window_name = "Chessboard Corners Detection"
                    cv2.imshow(window_name, display_img)

                    key = cv2.waitKey(0)
                    if key == 27:
                        cv2.destroyWindow(window_name)
                        break

                    cv2.destroyWindow(window_name)
            elif not silent:
                print(f"Cannot find chessboard corners in image {idx + 1}")

        if not silent:
            print(f"\nFound corners in {len(self.corners_list)}/{len(self.images)} images")
        return len(self.corners_list) > 0
    
    def calibrate_camera(self, silent=False):
        if not self.objpoints or not self.imgpoints:
            if not silent:
                print("Please find corners first!")
            return False

        img_size = (self.images[0].shape[1], self.images[0].shape[0])

        ret, self.camera_matrix, self.dist_coeffs, self.rvecs, self.tvecs = \
            cv2.calibrateCamera(self.objpoints, self.imgpoints, img_size, None, None)

        if ret:
            if not silent:
                print("\nIntrinsic Matrix (K):")
                print(self.camera_matrix)
            return True
        else:
            if not silent:
                print("Camera calibration failed!")
            return False
    
    def get_extrinsic_matrix(self, image_index):
        if not self.rvecs or not self.tvecs:
            print("Please calibrate camera first!")
            return None

        idx = image_index - 1

        if idx < 0 or idx >= len(self.rvecs):
            print(f"Invalid image index: {image_index}")
            return None

        rotation_matrix, _ = cv2.Rodrigues(self.rvecs[idx])
        extrinsic_matrix = np.hstack((rotation_matrix, self.tvecs[idx]))

        print(f"\nExtrinsic Matrix for Image {image_index}:")
        print(extrinsic_matrix)

        return extrinsic_matrix
    
    def get_distortion_coefficients(self):
        if self.dist_coeffs is None:
            print("Please calibrate camera first!")
            return None

        print("\nDistortion Coefficients:")
        print(self.dist_coeffs)

        return self.dist_coeffs
    
    def show_undistorted_images(self):
        if self.camera_matrix is None or self.dist_coeffs is None:
            print("Please calibrate camera first!")
            return

        print("\n=== Showing Undistorted Results ===")
        print("Press any key to see next image, or ESC to stop")

        for idx, img in enumerate(self.images):
            undistorted = cv2.undistort(img, self.camera_matrix, self.dist_coeffs)

            img_resized = self._resize_for_display(img)
            undistorted_resized = self._resize_for_display(undistorted)

            # Combine images side-by-side
            h, w = img_resized.shape[:2]
            combined = np.hstack((img_resized, undistorted_resized))

            cv2.putText(combined, 'Distorted', (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)
            cv2.putText(combined, 'Undistorted', (w + 50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)

            text = f"Image {idx + 1}/{len(self.images)}"
            cv2.putText(combined, text, (50, h - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            window_name = "Undistortion Result"
            cv2.imshow(window_name, combined)

            key = cv2.waitKey(0)
            if key == 27:
                cv2.destroyWindow(window_name)
                break

            cv2.destroyWindow(window_name)

        cv2.destroyAllWindows()

    def _resize_for_display(self, img, max_width=800):
        h, w = img.shape[:2]
        if w > max_width:
            scale = max_width / w
            new_w = max_width
            new_h = int(h * scale)
            return cv2.resize(img, (new_w, new_h))
        return img