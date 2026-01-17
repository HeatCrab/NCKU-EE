from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QGroupBox, QFileDialog, 
                             QLineEdit, QComboBox, QTextEdit)
from PyQt5.QtCore import Qt
import sys
import cv2
from modules.utils import show_images_sequence, create_stereo_display_image, resize_image_for_display
from modules.calibration import CameraCalibration
from modules.augmented_reality import AugmentedReality
from modules.stereo_disparity import StereoDisparity
from modules.sift import SIFT


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.folder_path = ""
        self.image_l_path = ""
        self.image_r_path = ""
        self.sift_image1_path = ""
        self.sift_image2_path = ""

        # Initialize modules
        self.calibration = CameraCalibration()
        self.ar = AugmentedReality('Dataset/Q2_Image/Q2_db/alphabet_db_onboard.txt',
                                    'Dataset/Q2_Image/Q2_db/alphabet_db_vertical.txt')
        self.stereo = StereoDisparity()
        self.sift = SIFT()
        
    def init_ui(self):
        self.setWindowTitle('CVDL Homework 1')
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left panel: Load Image controls
        left_layout = QVBoxLayout()
        load_group = self.create_load_image_group()
        left_layout.addWidget(load_group)
        left_layout.addStretch()

        # Middle panel: Main features
        middle_layout = QVBoxLayout()
        calibration_group = self.create_calibration_group()
        middle_layout.addWidget(calibration_group)
        ar_group = self.create_augmented_reality_group()
        middle_layout.addWidget(ar_group)
        sift_group = self.create_sift_group()
        middle_layout.addWidget(sift_group)
        middle_layout.addStretch()

        # Right panel: Stereo Disparity
        right_layout = QVBoxLayout()
        stereo_group = self.create_stereo_group()
        right_layout.addWidget(stereo_group)
        right_layout.addStretch()

        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(middle_layout, 2)
        main_layout.addLayout(right_layout, 1)
        
    def create_load_image_group(self):
        group = QGroupBox("Load Image")
        layout = QVBoxLayout()

        self.btn_load_folder = QPushButton("Load Folder")
        self.btn_load_folder.clicked.connect(self.load_folder)
        layout.addWidget(self.btn_load_folder)
        layout.addSpacing(20)

        self.btn_load_image_l = QPushButton("Load Image_L")
        self.btn_load_image_l.clicked.connect(self.load_image_l)
        layout.addWidget(self.btn_load_image_l)
        layout.addSpacing(20)

        self.btn_load_image_r = QPushButton("Load Image_R")
        self.btn_load_image_r.clicked.connect(self.load_image_r)
        layout.addWidget(self.btn_load_image_r)

        group.setLayout(layout)
        return group
    
    def create_calibration_group(self):
        group = QGroupBox("1. Calibration")
        layout = QVBoxLayout()

        btn_find_corners = QPushButton("1.1 Find Corners")
        btn_find_corners.clicked.connect(self.find_corners)
        layout.addWidget(btn_find_corners)

        btn_find_intrinsic = QPushButton("1.2 Find Intrinsic")
        btn_find_intrinsic.clicked.connect(self.find_intrinsic)
        layout.addWidget(btn_find_intrinsic)

        layout.addWidget(QLabel("1.3 Find Extrinsic"))
        self.combo_image_index = QComboBox()
        self.combo_image_index.addItems([str(i) for i in range(1, 16)])
        layout.addWidget(self.combo_image_index)
        btn_find_extrinsic = QPushButton("1.3 Find Extrinsic")
        btn_find_extrinsic.clicked.connect(self.find_extrinsic)
        layout.addWidget(btn_find_extrinsic)

        btn_find_distortion = QPushButton("1.4 Find Distortion")
        btn_find_distortion.clicked.connect(self.find_distortion)
        layout.addWidget(btn_find_distortion)

        btn_show_result = QPushButton("1.5 Show Result")
        btn_show_result.clicked.connect(self.show_undistorted_result)
        layout.addWidget(btn_show_result)

        group.setLayout(layout)
        return group
    
    def create_augmented_reality_group(self):
        group = QGroupBox("2. Augmented Reality")
        layout = QVBoxLayout()

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Enter text (e.g., CAMERA)")
        self.text_input.setMaxLength(6)
        layout.addWidget(self.text_input)

        btn_show_words = QPushButton("2.1 Show Words on Board")
        btn_show_words.clicked.connect(self.show_words_on_board)
        layout.addWidget(btn_show_words)

        btn_show_vertical = QPushButton("2.2 Show Words Vertically")
        btn_show_vertical.clicked.connect(self.show_words_vertically)
        layout.addWidget(btn_show_vertical)

        group.setLayout(layout)
        return group
    
    def create_stereo_group(self):
        group = QGroupBox("3. Stereo Disparity Map")
        layout = QVBoxLayout()

        btn_stereo = QPushButton("3.1 Stereo Disparity Map")
        btn_stereo.clicked.connect(self.show_stereo_disparity)
        layout.addWidget(btn_stereo)

        group.setLayout(layout)
        return group
    
    def create_sift_group(self):
        group = QGroupBox("4. SIFT")
        layout = QVBoxLayout()

        btn_load_img1 = QPushButton("Load Image1")
        btn_load_img1.clicked.connect(self.load_sift_image1)
        layout.addWidget(btn_load_img1)

        btn_load_img2 = QPushButton("Load Image2")
        btn_load_img2.clicked.connect(self.load_sift_image2)
        layout.addWidget(btn_load_img2)

        btn_keypoints = QPushButton("4.1 Keypoints")
        btn_keypoints.clicked.connect(self.show_keypoints)
        layout.addWidget(btn_keypoints)

        btn_matched = QPushButton("4.2 Matched Keypoints")
        btn_matched.clicked.connect(self.show_matched_keypoints)
        layout.addWidget(btn_matched)

        group.setLayout(layout)
        return group
    
    def load_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_path = folder
            if self.calibration.load_images(folder):
                print(f"Loaded folder: {folder}")
            else:
                print("Failed to load images from folder")
    
    def load_image_l(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Image_L", "", "Images (*.png *.jpg *.bmp)")
        if file:
            self.image_l_path = file
            print(f"Loaded Image_L: {file}")
    
    def load_image_r(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Image_R", "", "Images (*.png *.jpg *.bmp)")
        if file:
            self.image_r_path = file
            print(f"Loaded Image_R: {file}")
    
    def load_sift_image1(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Image1", "", "Images (*.png *.jpg *.bmp)")
        if file:
            self.sift_image1_path = file
            print(f"Loaded SIFT Image1: {file}")
    
    def load_sift_image2(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Image2", "", "Images (*.png *.jpg *.bmp)")
        if file:
            self.sift_image2_path = file
            print(f"Loaded SIFT Image2: {file}")
    
    def find_corners(self):
        if not self.calibration.images:
            print("Please load folder first!")
            return
        self.calibration.find_corners()

    def find_intrinsic(self):
        if not self.calibration.corners_list:
            print("Please find corners first!")
            return
        self.calibration.calibrate_camera()

    def find_extrinsic(self):
        idx = int(self.combo_image_index.currentText())
        self.calibration.get_extrinsic_matrix(idx)

    def find_distortion(self):
        self.calibration.get_distortion_coefficients()

    def show_undistorted_result(self):
        self.calibration.show_undistorted_images()
    
    def show_words_on_board(self):
        text = self.text_input.text().upper()
        if len(text) > 6 or len(text) == 0:
            print("Please enter 1-6 characters!")
            return

        # Check if calibration has been done
        if not self.calibration.rvecs or not self.calibration.tvecs:
            print("Calibration not done. Performing automatic calibration...")
            # Find corners first (silent mode - no GUI)
            if not self.calibration.find_corners(silent=True):
                print("Failed to find corners!")
                return
            # Then calibrate (silent mode)
            if not self.calibration.calibrate_camera(silent=True):
                print("Failed to calibrate camera!")
                return
            print("Calibration completed successfully!")

        print(f"Showing '{text}' on board...")

        # Process first 5 images
        result_images = []
        for i in range(min(5, len(self.calibration.images))):
            img = self.calibration.images[i]
            rvec = self.calibration.rvecs[i]
            tvec = self.calibration.tvecs[i]

            result_img = self.ar.draw_text(
                img, text,
                self.calibration.camera_matrix,
                self.calibration.dist_coeffs,
                rvec, tvec,
                is_vertical=False
            )
            result_images.append(result_img)

        show_images_sequence(result_images, [f"Result {i+1}" for i in range(len(result_images))])
    
    def show_words_vertically(self):
        text = self.text_input.text().upper()
        if len(text) > 6 or len(text) == 0:
            print("Please enter 1-6 characters!")
            return

        # Check if calibration has been done
        if not self.calibration.rvecs or not self.calibration.tvecs:
            print("Calibration not done. Performing automatic calibration...")
            # Find corners first (silent mode - no GUI)
            if not self.calibration.find_corners(silent=True):
                print("Failed to find corners!")
                return
            # Then calibrate (silent mode)
            if not self.calibration.calibrate_camera(silent=True):
                print("Failed to calibrate camera!")
                return
            print("Calibration completed successfully!")

        print(f"Showing '{text}' vertically...")
        result_images = []
        for i in range(min(5, len(self.calibration.images))):
            img = self.calibration.images[i]
            rvec = self.calibration.rvecs[i]
            tvec = self.calibration.tvecs[i]

            result_img = self.ar.draw_text(
                img, text,
                self.calibration.camera_matrix,
                self.calibration.dist_coeffs,
                rvec, tvec,
                is_vertical=True
            )
            result_images.append(result_img)

        show_images_sequence(result_images, [f"Result {i+1}" for i in range(len(result_images))])
    
    def show_stereo_disparity(self):
        print("Showing stereo disparity map...")
        if not self.image_l_path or not self.image_r_path:
            print("Please load both Image_L and Image_R first!")
            return

        imgL_color = cv2.imread(self.image_l_path)
        imgR_color = cv2.imread(self.image_r_path)

        if imgL_color is None or imgR_color is None:
            print("Failed to read one or both images. Check file paths.")
            return

        imgL_gray = cv2.cvtColor(imgL_color, cv2.COLOR_BGR2GRAY)
        imgR_gray = cv2.cvtColor(imgR_color, cv2.COLOR_BGR2GRAY)

        print("Calculating Stereo Disparity Map...")
        disparity_map = self.stereo.compute(imgL_gray, imgR_gray)
        combined_image = create_stereo_display_image(imgL_color, imgR_color, disparity_map)

        cv2.imshow('Stereo Disparity Result (Left, Right, Map)', combined_image)
        print("Displaying results. Press any key in the image window to close it.")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    def show_keypoints(self):
        print("Showing SIFT keypoints...")
        if not self.sift_image1_path:
            print("Please load Image1 for SIFT first!")
            return

        img = cv2.imread(self.sift_image1_path)
        if img is None:
            print("Failed to read SIFT Image1.")
            return

        print("Finding SIFT keypoints...")
        img_with_keypoints = self.sift.find_and_draw_keypoints(img)
        display_img = resize_image_for_display(img_with_keypoints, max_height=800)

        cv2.imshow('SIFT Keypoints', img_with_keypoints)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
    def show_matched_keypoints(self):
        print("Showing matched keypoints...")
        if not self.sift_image1_path or not self.sift_image2_path:
            print("Please load both Image1 and Image2 for SIFT matching!")
            return
            
        img1 = cv2.imread(self.sift_image1_path)
        img2 = cv2.imread(self.sift_image2_path)
        
        if img1 is None or img2 is None:
            print("Failed to read one or both SIFT images.")
            return

        print("Matching SIFT keypoints...")
        img_matches = self.sift.match_and_draw_keypoints(img1, img2)
        display_img = resize_image_for_display(img_matches, max_height=600)

        cv2.imshow('SIFT Matched Keypoints', img_matches)
        cv2.waitKey(0)
        cv2.destroyAllWindows()