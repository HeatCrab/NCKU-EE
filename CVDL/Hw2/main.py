import sys
import os
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import torch
import torchvision
from torchvision import transforms
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import cv2

# Import UI
from ui_main import MainWindowUI

# Import custom modules
from models.resnet18_cifar import ResNet18CIFAR


class MainWindow(MainWindowUI):
    def __init__(self):
        super().__init__()

        # Model paths
        self.faster_rcnn_model_path = "weights/faster_rcnn_best.pth"
        self.resnet18_model_path = "weights/resnet18_best.pth"

        # VOC class names (20 classes + background)
        self.voc_classes = [
            '__background__', 'aeroplane', 'bicycle', 'bird', 'boat',
            'bottle', 'bus', 'car', 'cat', 'chair', 'cow', 'diningtable',
            'dog', 'horse', 'motorbike', 'person', 'pottedplant', 'sheep',
            'sofa', 'train', 'tvmonitor'
        ]

        # CIFAR-10 class names
        self.cifar_classes = ['airplane', 'automobile', 'bird', 'cat', 'deer',
                             'dog', 'frog', 'horse', 'ship', 'truck']

        # Initialize models as None
        self.faster_rcnn_model = None
        self.resnet18_model = None

        # Current loaded image paths
        self.q1_image_path = None
        self.q2_image_path = None

        # Device
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")

        # Connect signals
        self.connect_signals()

    def connect_signals(self):
        """Connect button signals to slots"""
        # Q1 buttons
        self.btn_q1_1.clicked.connect(self.q1_1_show_architecture)
        self.btn_q1_2.clicked.connect(self.q1_2_show_training_loss)
        self.btn_q1_3_load.clicked.connect(self.q1_3_load_image)
        self.btn_q1_3_inference.clicked.connect(self.q1_3_inference)

        # Q2 buttons
        self.btn_q2_1.clicked.connect(self.q2_1_load_show_image)
        self.btn_q2_2.clicked.connect(self.q2_2_show_model_structure)
        self.btn_q2_3.clicked.connect(self.q2_3_show_acc_loss)
        self.btn_q2_4.clicked.connect(self.q2_4_inference)

    # ========== Q1: Faster R-CNN Methods ==========
    def q1_1_show_architecture(self):
        """1.1 Load and show Faster R-CNN architecture"""
        print("\n" + "=" * 80)
        print("Faster R-CNN Architecture (ResNet50-FPN backbone)")
        print("=" * 80)

        # Create model
        model = torchvision.models.detection.fasterrcnn_resnet50_fpn(
            num_classes=21,  # 20 VOC classes + background
            weights=None
        )
        print(model)
        print("=" * 80)

        QMessageBox.information(self, "Architecture",
                               "Faster R-CNN architecture has been printed in the terminal!\n\n"
                               "Model: fasterrcnn_resnet50_fpn\n"
                               "Backbone: ResNet50 with FPN\n"
                               "Number of classes: 21 (20 VOC classes + background)")

    def q1_2_show_training_loss(self):
        """1.2 Show training loss curve"""
        loss_img_path = "results/faster_rcnn_loss.png"

        if not os.path.exists(loss_img_path):
            QMessageBox.warning(self, "Warning",
                              f"Training loss curve not found!\n\n"
                              f"Expected path: {loss_img_path}\n\n"
                              "Please train the model first using:\n"
                              "python train_faster_rcnn.py")
            return

        # Show image in new matplotlib window
        img = Image.open(loss_img_path)
        plt.figure(figsize=(10, 6))
        plt.imshow(img)
        plt.axis('off')
        plt.title('Faster R-CNN Training Loss Curve')
        plt.tight_layout()
        plt.show()

    def q1_3_load_image(self):
        """1.3 Load image for inference"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image for Faster R-CNN Inference",
            "Q1_InferenceImages",
            "Images (*.jpg *.jpeg *.png *.bmp)"
        )

        if file_path:
            self.q1_image_path = file_path
            # Display original image
            pixmap = QPixmap(file_path)
            scaled_pixmap = pixmap.scaled(500, 500, Qt.KeepAspectRatio,
                                         Qt.SmoothTransformation)
            self.q1_image_label.setPixmap(scaled_pixmap)
            print(f"Loaded image: {file_path}")

    def q1_3_inference(self):
        """1.3 Run inference with Faster R-CNN"""
        if self.q1_image_path is None:
            QMessageBox.warning(self, "Warning",
                              "Please load an image first using '1.3 Load Image' button!")
            return

        # Load model if not loaded
        if self.faster_rcnn_model is None:
            if not os.path.exists(self.faster_rcnn_model_path):
                QMessageBox.warning(self, "Model Not Found",
                                  f"Trained model not found!\n\n"
                                  f"Expected path: {self.faster_rcnn_model_path}\n\n"
                                  "Please train the model first using:\n"
                                  "python train_faster_rcnn.py")
                return

            print("Loading Faster R-CNN model...")
            self.faster_rcnn_model = torchvision.models.detection.fasterrcnn_resnet50_fpn(
                num_classes=21,
                weights=None
            )
            self.faster_rcnn_model.load_state_dict(
                torch.load(self.faster_rcnn_model_path, map_location=self.device)
            )
            self.faster_rcnn_model.to(self.device)
            self.faster_rcnn_model.eval()
            print("Model loaded successfully!")

        # Load and preprocess image
        image = Image.open(self.q1_image_path).convert('RGB')
        transform = transforms.Compose([transforms.ToTensor()])
        image_tensor = transform(image)

        # Run inference
        print("Running inference...")
        with torch.no_grad():
            prediction = self.faster_rcnn_model([image_tensor.to(self.device)])[0]

        # Draw bounding boxes on image
        image_np = np.array(image)
        # Convert RGB to BGR for OpenCV drawing functions
        image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

        threshold = 0.5
        num_detections = 0

        for box, label, score in zip(prediction['boxes'],
                                     prediction['labels'],
                                     prediction['scores']):
            if score > threshold:
                num_detections += 1
                box = box.cpu().numpy().astype(int)
                label_idx = label.cpu().item()
                score_val = score.cpu().item()

                # Draw bounding box (BGR format: Green = (0, 255, 0))
                cv2.rectangle(image_np,
                            (box[0], box[1]),
                            (box[2], box[3]),
                            (0, 255, 0), 3)

                # Prepare label text
                label_text = f"{self.voc_classes[label_idx]}: {score_val:.2f}"

                # Draw background for text
                (text_width, text_height), _ = cv2.getTextSize(
                    label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
                )
                cv2.rectangle(image_np,
                            (box[0], box[1] - text_height - 10),
                            (box[0] + text_width, box[1]),
                            (0, 255, 0), -1)

                # Draw label text
                cv2.putText(image_np, label_text,
                           (box[0], box[1] - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                           (0, 0, 0), 2)

        print(f"Detection complete! Found {num_detections} objects (threshold={threshold})")

        # Convert BGR back to RGB for Qt display
        image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)

        # Convert to QPixmap and display
        height, width, channel = image_np.shape
        bytes_per_line = 3 * width
        q_image = QImage(image_np.data, width, height, bytes_per_line,
                        QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(500, 500, Qt.KeepAspectRatio,
                                     Qt.SmoothTransformation)
        self.q1_image_label.setPixmap(scaled_pixmap)

    # ========== Q2: ResNet18 CIFAR-10 Methods ==========
    def q2_1_load_show_image(self):
        """2.1 Load and show image for CIFAR-10"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image for CIFAR-10 Classification",
            "Q2_inference_img",
            "Images (*.jpg *.jpeg *.png *.bmp)"
        )

        if file_path:
            self.q2_image_path = file_path
            # Load image
            img = Image.open(file_path).convert('RGB')

            # Display image (show larger version for visibility)
            pixmap = QPixmap(file_path)
            scaled_pixmap = pixmap.scaled(250, 250, Qt.KeepAspectRatio,
                                         Qt.SmoothTransformation)
            self.q2_image_label.setPixmap(scaled_pixmap)

            # Update result label
            self.q2_result_label.setText(
                f"Image loaded: {os.path.basename(file_path)}\n"
                f"Will be resized to 32x32 for inference"
            )
            print(f"Loaded image: {file_path}")

    def q2_2_show_model_structure(self):
        """2.2 Show ResNet18 model structure"""
        print("\n" + "=" * 80)
        print("ResNet18 CIFAR-10 Architecture")
        print("=" * 80)

        model = ResNet18CIFAR(num_classes=10)
        print(model)

        print("\n" + "-" * 80)
        print("Model Summary:")
        print(f"  - Modified first conv: 3x3 kernel, stride 1 (instead of 7x7, stride 2)")
        print(f"  - Removed max pooling layer")
        print(f"  - Output layer: 10 classes (CIFAR-10)")
        print(f"  - Input size: 32x32x3")
        print("=" * 80)

        QMessageBox.information(self, "Model Structure",
                               "ResNet18 model structure has been printed in the terminal!\n\n"
                               "Key modifications for CIFAR-10:\n"
                               "- First conv: 3x3 stride 1 (vs 7x7 stride 2)\n"
                               "- No max pooling\n"
                               "- FC layer: 512 -> 10 classes")

    def q2_3_show_acc_loss(self):
        """2.3 Show accuracy and loss curves"""
        curves_img_path = "results/resnet18_curves.png"

        if not os.path.exists(curves_img_path):
            QMessageBox.warning(self, "Warning",
                              f"Training curves not found!\n\n"
                              f"Expected path: {curves_img_path}\n\n"
                              "Please train the model first using:\n"
                              "python train_resnet18.py")
            return

        # Show image in new matplotlib window
        img = Image.open(curves_img_path)
        plt.figure(figsize=(14, 6))
        plt.imshow(img)
        plt.axis('off')
        plt.title('ResNet18 Training/Validation Accuracy and Loss Curves')
        plt.tight_layout()
        plt.show()

    def q2_4_inference(self):
        """2.4 Run inference with ResNet18"""
        if self.q2_image_path is None:
            QMessageBox.warning(self, "Warning",
                              "Please load an image first using '2.1 Load and Show Image' button!")
            return

        # Load model if not loaded
        if self.resnet18_model is None:
            if not os.path.exists(self.resnet18_model_path):
                QMessageBox.warning(self, "Model Not Found",
                                  f"Trained model not found!\n\n"
                                  f"Expected path: {self.resnet18_model_path}\n\n"
                                  "Please train the model first using:\n"
                                  "python train_resnet18.py")
                return

            print("Loading ResNet18 model...")
            self.resnet18_model = ResNet18CIFAR(num_classes=10)
            self.resnet18_model.load_state_dict(
                torch.load(self.resnet18_model_path, map_location=self.device)
            )
            self.resnet18_model.to(self.device)
            self.resnet18_model.eval()
            print("Model loaded successfully!")

        # Load and preprocess image
        img = Image.open(self.q2_image_path).convert('RGB')
        img_resized = img.resize((32, 32))

        # CIFAR-10 normalization
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.4914, 0.4822, 0.4465),
                               (0.2023, 0.1994, 0.2010))
        ])
        img_tensor = transform(img_resized).unsqueeze(0)

        # Run inference
        print("Running inference...")
        with torch.no_grad():
            output = self.resnet18_model(img_tensor.to(self.device))
            probabilities = torch.softmax(output, dim=1)[0]

        probs = probabilities.cpu().numpy()
        max_prob = np.max(probs)
        predicted_class = np.argmax(probs)

        # Threshold for detecting "out of distribution" images
        threshold = 0.5

        if max_prob < threshold:
            predicted_label = "Others"
            result_color = "red"
        else:
            predicted_label = self.cifar_classes[predicted_class]
            result_color = "green"

        # Update result label
        self.q2_result_label.setStyleSheet(
            f"border: 2px solid {result_color}; padding: 10px; "
            f"background-color: white; font-weight: bold;"
        )
        self.q2_result_label.setText(
            f"Predicted Class: {predicted_label}\n"
            f"Confidence: {max_prob:.4f}"
        )

        print(f"Prediction: {predicted_label} (confidence: {max_prob:.4f})")

        # Show probability distribution in new window
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(self.cifar_classes, probs, color='skyblue', edgecolor='navy')

        # Highlight the predicted class
        if max_prob >= threshold:
            bars[predicted_class].set_color('green')

        ax.set_xlabel('Class', fontsize=12)
        ax.set_ylabel('Probability', fontsize=12)
        ax.set_title(
            f'Probability Distribution\n'
            f'Predicted: {predicted_label} (Confidence: {max_prob:.4f})',
            fontsize=14, fontweight='bold'
        )
        ax.set_ylim([0, 1])
        ax.axhline(y=threshold, color='r', linestyle='--',
                  label=f'Threshold ({threshold})')
        ax.legend()
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
