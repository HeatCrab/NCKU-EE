import cv2
import numpy as np
import time

def show_image(title, image, wait_time=0):
    cv2.imshow(title, image)
    if wait_time == 0:
        cv2.waitKey(0)
    else:
        cv2.waitKey(wait_time)
    cv2.destroyAllWindows()

def show_images_sequence(images, titles, wait_time=1000):
    for img, title in zip(images, titles):
        cv2.imshow(title, img)
        cv2.waitKey(wait_time)
        cv2.destroyAllWindows()

def load_images_from_folder(folder_path, pattern="*.bmp"):
    import glob
    import os

    search_path = os.path.join(folder_path, pattern)
    image_paths = sorted(glob.glob(search_path))

    images = []
    for path in image_paths:
        img = cv2.imread(path)
        if img is not None:
            images.append(img)

    return images, image_paths

def create_stereo_display_image(imgL_color, imgR_color, disparity_map, height=600):
    def resize_image(img, target_height):
        aspect_ratio = img.shape[1] / img.shape[0]
        target_width = int(target_height * aspect_ratio)
        return cv2.resize(img, (target_width, target_height))

    imgL_display = resize_image(imgL_color, height)
    imgR_display = resize_image(imgR_color, height)

    disparity_display_bgr = cv2.cvtColor(disparity_map, cv2.COLOR_GRAY2BGR)
    disparity_display = resize_image(disparity_display_bgr, height)

    combined_result = np.hstack([imgL_display, imgR_display, disparity_display])
    return combined_result

def resize_image_for_display(img, max_height=800):
    h, w = img.shape[:2]
    if h > max_height:
        aspect_ratio = w / h
        target_height = max_height
        target_width = int(target_height * aspect_ratio)
        return cv2.resize(img, (target_width, target_height))
    return img