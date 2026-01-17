import cv2
import numpy as np

class AugmentedReality:
    def __init__(self, onboard_db_path, vertical_db_path):
        self.db_onboard = cv2.FileStorage(onboard_db_path, cv2.FILE_STORAGE_READ)
        self.db_vertical = cv2.FileStorage(vertical_db_path, cv2.FILE_STORAGE_READ)

        # Character positions on chessboard
        self.char_positions = [
            (7, 5), (4, 5), (1, 5),
            (7, 2), (4, 2), (1, 2)
        ]
        self.square_size = 0.02

    def draw_text(self, image, text, camera_matrix, dist_coeffs, rvec, tvec, is_vertical=False):
        img_copy = image.copy()
        db = self.db_vertical if is_vertical else self.db_onboard

        for i, char in enumerate(text):
            if i >= len(self.char_positions):
                break

            char_lines_3d = db.getNode(char).mat()
            if char_lines_3d is None:
                continue

            for line_segment_3d in char_lines_3d:
                # Translate to character position
                x_offset, y_offset = self.char_positions[i]
                translation_vector = np.array([x_offset, y_offset, 0], dtype=np.float32)
                translated_segment = line_segment_3d + translation_vector
                translated_segment_meters = translated_segment * self.square_size

                # Project 3D points to 2D
                projected_points, _ = cv2.projectPoints(translated_segment_meters, rvec, tvec,
                                                        camera_matrix, dist_coeffs)

                pt1 = tuple(projected_points[0].ravel().astype(int))
                pt2 = tuple(projected_points[1].ravel().astype(int))

                cv2.line(img_copy, pt1, pt2, (0, 0, 255), 4)

        return img_copy