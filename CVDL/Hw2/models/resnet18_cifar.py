"""
ResNet18 model modified for CIFAR-10 dataset

Key modifications:
1. Replace 7x7 conv stride 2 with 3x3 conv stride 1
2. Remove max pooling layer
3. Change output layer to 10 classes (instead of 1000)
"""

import torch
import torch.nn as nn


class BasicBlock(nn.Module):
    """Basic residual block for ResNet18"""
    expansion = 1

    def __init__(self, in_channels, out_channels, stride=1, downsample=None):
        super(BasicBlock, self).__init__()

        # First conv layer
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3,
                              stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)

        # Second conv layer
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3,
                              stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)

        # Downsample layer (for skip connection when dimensions change)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        identity = x

        # First conv + bn + relu
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        # Second conv + bn
        out = self.conv2(out)
        out = self.bn2(out)

        # Skip connection
        if self.downsample is not None:
            identity = self.downsample(x)

        out += identity
        out = self.relu(out)

        return out


class ResNet18CIFAR(nn.Module):
    """
    ResNet18 modified for CIFAR-10 (32x32 input images)

    Architecture changes from original ResNet18:
    - conv1: 7x7 stride 2 -> 3x3 stride 1
    - Removed max pooling after conv1
    - FC layer: 1000 classes -> 10 classes
    """

    def __init__(self, num_classes=10):
        super(ResNet18CIFAR, self).__init__()

        self.in_channels = 64

        # Modified first conv layer for CIFAR-10 (32x32 images)
        # Original: 7x7, stride 2, padding 3
        # Modified: 3x3, stride 1, padding 1
        self.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)

        # No max pooling (removed for small CIFAR-10 images)
        # Original ResNet18 has: maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)

        # ResNet layers
        # Layer 1: 64 channels, 2 blocks
        self.layer1 = self._make_layer(BasicBlock, 64, num_blocks=2, stride=1)

        # Layer 2: 128 channels, 2 blocks
        self.layer2 = self._make_layer(BasicBlock, 128, num_blocks=2, stride=2)

        # Layer 3: 256 channels, 2 blocks
        self.layer3 = self._make_layer(BasicBlock, 256, num_blocks=2, stride=2)

        # Layer 4: 512 channels, 2 blocks
        self.layer4 = self._make_layer(BasicBlock, 512, num_blocks=2, stride=2)

        # Global average pooling
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))

        # Fully connected layer (modified for CIFAR-10)
        # Original: in_features=512, out_features=1000
        # Modified: in_features=512, out_features=10
        self.fc = nn.Linear(512 * BasicBlock.expansion, num_classes)

        # Initialize weights
        self._initialize_weights()

    def _make_layer(self, block, out_channels, num_blocks, stride):
        """Create a ResNet layer with multiple blocks"""
        downsample = None

        # If dimensions change, create downsample layer for skip connection
        if stride != 1 or self.in_channels != out_channels * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(self.in_channels, out_channels * block.expansion,
                         kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels * block.expansion),
            )

        layers = []

        # First block (may downsample)
        layers.append(block(self.in_channels, out_channels, stride, downsample))
        self.in_channels = out_channels * block.expansion

        # Remaining blocks
        for _ in range(1, num_blocks):
            layers.append(block(self.in_channels, out_channels))

        return nn.Sequential(*layers)

    def _initialize_weights(self):
        """Initialize weights using He initialization"""
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)

    def forward(self, x):
        # Input: (batch_size, 3, 32, 32)

        # First conv + bn + relu
        x = self.conv1(x)  # (batch_size, 64, 32, 32)
        x = self.bn1(x)
        x = self.relu(x)

        # No max pooling for CIFAR-10

        # ResNet layers
        x = self.layer1(x)  # (batch_size, 64, 32, 32)
        x = self.layer2(x)  # (batch_size, 128, 16, 16)
        x = self.layer3(x)  # (batch_size, 256, 8, 8)
        x = self.layer4(x)  # (batch_size, 512, 4, 4)

        # Global average pooling
        x = self.avgpool(x)  # (batch_size, 512, 1, 1)
        x = torch.flatten(x, 1)  # (batch_size, 512)

        # Fully connected layer
        x = self.fc(x)  # (batch_size, 10)

        return x


def test_model():
    """Test the model with random input"""
    model = ResNet18CIFAR(num_classes=10)
    x = torch.randn(2, 3, 32, 32)  # Batch of 2 CIFAR-10 images
    output = model(x)
    print(f"Input shape: {x.shape}")
    print(f"Output shape: {output.shape}")
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")


if __name__ == '__main__':
    test_model()
