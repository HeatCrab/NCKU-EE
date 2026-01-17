from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QGroupBox, QPushButton, QLabel)
from PyQt5.QtCore import Qt


class MainWindowUI(QMainWindow):
    """Main window UI definition"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CVDL Homework 2")
        self.setGeometry(100, 100, 1200, 800)

        # UI components
        self.q1_image_label = None
        self.q2_image_label = None
        self.q2_result_label = None

        # Buttons
        self.btn_q1_1 = None
        self.btn_q1_2 = None
        self.btn_q1_3_load = None
        self.btn_q1_3_inference = None
        self.btn_q2_1 = None
        self.btn_q2_2 = None
        self.btn_q2_3 = None
        self.btn_q2_4 = None

        self.init_ui()

    def init_ui(self):
        """Initialize UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left panel - Q1 (Faster R-CNN)
        q1_group = self.create_q1_panel()
        main_layout.addWidget(q1_group)

        # Right panel - Q2 (ResNet18)
        q2_group = self.create_q2_panel()
        main_layout.addWidget(q2_group)

    def create_q1_panel(self):
        """Create Q1 panel"""
        q1_group = QGroupBox("Q1: Faster R-CNN Object Detector")
        q1_layout = QVBoxLayout()

        # Buttons
        self.btn_q1_1 = QPushButton("1.1 Show Architecture")
        q1_layout.addWidget(self.btn_q1_1)

        self.btn_q1_2 = QPushButton("1.2 Show Training Loss")
        q1_layout.addWidget(self.btn_q1_2)

        self.btn_q1_3_load = QPushButton("1.3 Load Image")
        q1_layout.addWidget(self.btn_q1_3_load)

        self.btn_q1_3_inference = QPushButton("1.3 Inference")
        q1_layout.addWidget(self.btn_q1_3_inference)

        # Image display
        self.q1_image_label = QLabel()
        self.q1_image_label.setMinimumSize(500, 500)
        self.q1_image_label.setStyleSheet("border: 2px solid #888; background-color: #f0f0f0;")
        self.q1_image_label.setAlignment(Qt.AlignCenter)
        self.q1_image_label.setText("No image loaded")
        q1_layout.addWidget(self.q1_image_label)

        q1_group.setLayout(q1_layout)
        return q1_group

    def create_q2_panel(self):
        """Create Q2 panel"""
        q2_group = QGroupBox("Q2: ResNet18 CIFAR-10 Classifier")
        q2_layout = QVBoxLayout()

        # Buttons
        self.btn_q2_1 = QPushButton("2.1 Load and Show Image")
        q2_layout.addWidget(self.btn_q2_1)

        self.btn_q2_2 = QPushButton("2.2 Show Model Structure")
        q2_layout.addWidget(self.btn_q2_2)

        self.btn_q2_3 = QPushButton("2.3 Show Acc and Loss")
        q2_layout.addWidget(self.btn_q2_3)

        self.btn_q2_4 = QPushButton("2.4 Inference")
        q2_layout.addWidget(self.btn_q2_4)

        # Image display
        self.q2_image_label = QLabel()
        self.q2_image_label.setMinimumSize(250, 250)
        self.q2_image_label.setStyleSheet("border: 2px solid #888; background-color: #f0f0f0;")
        self.q2_image_label.setAlignment(Qt.AlignCenter)
        self.q2_image_label.setText("No image loaded")
        q2_layout.addWidget(self.q2_image_label)

        # Result label
        self.q2_result_label = QLabel()
        self.q2_result_label.setMinimumHeight(60)
        self.q2_result_label.setStyleSheet("border: 1px solid #ccc; padding: 10px; background-color: white;")
        self.q2_result_label.setAlignment(Qt.AlignCenter)
        self.q2_result_label.setText("Prediction result will appear here")
        q2_layout.addWidget(self.q2_result_label)

        q2_group.setLayout(q2_layout)
        return q2_group
