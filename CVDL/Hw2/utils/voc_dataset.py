"""
Pascal VOC Dataset wrapper for Faster R-CNN training

Converts VOC XML format to Faster R-CNN expected format:
- boxes: [[xmin, ymin, xmax, ymax], ...]
- labels: [class_id, ...]
- image_id: int
"""

import os
import torch
from torch.utils.data import Dataset
from torchvision.datasets import VOCDetection
from torchvision import transforms
import xml.etree.ElementTree as ET
from PIL import Image


# VOC class names (20 classes)
VOC_CLASSES = [
    'aeroplane', 'bicycle', 'bird', 'boat', 'bottle',
    'bus', 'car', 'cat', 'chair', 'cow',
    'diningtable', 'dog', 'horse', 'motorbike', 'person',
    'pottedplant', 'sheep', 'sofa', 'train', 'tvmonitor'
]

# Create class name to index mapping (1-indexed, 0 is background)
CLASS_TO_IDX = {cls_name: idx + 1 for idx, cls_name in enumerate(VOC_CLASSES)}


class VOCDatasetWrapper(Dataset):
    """
    Wrapper for VOC dataset that converts XML annotations to Faster R-CNN format

    Returns:
        image: PIL Image or Tensor
        target: dict with keys:
            - boxes: FloatTensor[N, 4] (xmin, ymin, xmax, ymax)
            - labels: Int64Tensor[N] (class indices, 1-20, 0 is background)
            - image_id: Int64Tensor[1]
            - area: FloatTensor[N]
            - iscrowd: UInt8Tensor[N] (all 0 for VOC)
    """

    def __init__(self, root, year='2007', image_set='train', transform=None):
        """
        Args:
            root: Root directory of VOC dataset
            year: Year of dataset (e.g., '2007')
            image_set: 'train', 'val', or 'trainval'
            transform: Optional transform to apply to images
        """
        # Load VOC dataset using torchvision
        self.voc_dataset = VOCDetection(
            root=root,
            year=year,
            image_set=image_set,
            download=False  # Dataset should already be downloaded
        )

        self.transform = transform
        self.image_set = image_set

    def __len__(self):
        return len(self.voc_dataset)

    def __getitem__(self, idx):
        """
        Get image and target in Faster R-CNN format

        Returns:
            image: PIL Image or Tensor
            target: dict
        """
        # Get image and annotation from VOC dataset
        img, annotation = self.voc_dataset[idx]

        # Parse annotation
        boxes = []
        labels = []
        areas = []

        # Extract objects from annotation
        objects = annotation['annotation']['object']

        # Handle case where there's only one object (not a list)
        if not isinstance(objects, list):
            objects = [objects]

        for obj in objects:
            # Get class name and convert to index
            class_name = obj['name']
            if class_name not in CLASS_TO_IDX:
                continue  # Skip unknown classes

            label = CLASS_TO_IDX[class_name]

            # Get bounding box
            bbox = obj['bndbox']
            xmin = float(bbox['xmin'])
            ymin = float(bbox['ymin'])
            xmax = float(bbox['xmax'])
            ymax = float(bbox['ymax'])

            # Validate bounding box
            if xmax <= xmin or ymax <= ymin:
                continue

            boxes.append([xmin, ymin, xmax, ymax])
            labels.append(label)

            # Calculate area
            area = (xmax - xmin) * (ymax - ymin)
            areas.append(area)

        # Convert to tensors
        boxes = torch.as_tensor(boxes, dtype=torch.float32)
        labels = torch.as_tensor(labels, dtype=torch.int64)
        areas = torch.as_tensor(areas, dtype=torch.float32)
        image_id = torch.tensor([idx])

        # Create target dictionary
        target = {
            'boxes': boxes,
            'labels': labels,
            'image_id': image_id,
            'area': areas,
            'iscrowd': torch.zeros((len(labels),), dtype=torch.uint8)
        }

        # Apply transform if provided
        if self.transform is not None:
            img = self.transform(img)

        return img, target

    def get_image_info(self, idx):
        """Get image metadata"""
        _, annotation = self.voc_dataset[idx]
        size = annotation['annotation']['size']
        return {
            'height': int(size['height']),
            'width': int(size['width']),
            'depth': int(size['depth'])
        }


def collate_fn(batch):
    """
    Custom collate function for DataLoader

    Faster R-CNN expects a list of images and a list of targets,
    not a batched tensor, because images can have different sizes
    and different numbers of objects.

    Args:
        batch: List of (image, target) tuples

    Returns:
        images: List of tensors
        targets: List of dicts
    """
    images = []
    targets = []

    for img, target in batch:
        # Convert PIL Image to tensor if needed
        if not isinstance(img, torch.Tensor):
            img = transforms.ToTensor()(img)

        images.append(img)
        targets.append(target)

    return images, targets


def test_dataset():
    """Test the dataset wrapper"""
    import torchvision.transforms as T

    # Path to VOC dataset
    voc_root = 'data'

    # Create dataset
    dataset = VOCDatasetWrapper(
        root=voc_root,
        year='2007',
        image_set='train',
        transform=None
    )

    print(f"Dataset size: {len(dataset)}")

    # Test first sample
    img, target = dataset[0]
    print(f"\nFirst sample:")
    print(f"  Image type: {type(img)}")
    print(f"  Image size: {img.size if hasattr(img, 'size') else img.shape}")
    print(f"  Number of objects: {len(target['labels'])}")
    print(f"  Boxes shape: {target['boxes'].shape}")
    print(f"  Labels: {target['labels']}")
    print(f"  Areas: {target['area']}")

    # Test DataLoader with custom collate_fn
    from torch.utils.data import DataLoader

    dataloader = DataLoader(
        dataset,
        batch_size=2,
        shuffle=True,
        collate_fn=collate_fn
    )

    images, targets = next(iter(dataloader))
    print(f"\nDataLoader batch:")
    print(f"  Number of images: {len(images)}")
    print(f"  Number of targets: {len(targets)}")
    print(f"  First image shape: {images[0].shape}")
    print(f"  First target keys: {targets[0].keys()}")


if __name__ == '__main__':
    test_dataset()
