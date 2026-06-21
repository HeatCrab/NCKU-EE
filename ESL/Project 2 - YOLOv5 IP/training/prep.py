import os
import random
import shutil


def split_kitti(root_dir, train_ratio=0.8):
    # Paths based on the conversion step (teacher already provided YOLO labels).
    img_dir = os.path.join(root_dir, 'image_2')
    lbl_dir = os.path.join(root_dir, 'labels')

    # Output to VM home: the team datadrive at root_dir is read-only, and an
    # absolute path avoids the spec's manual "move into ../dataset" step.
    base_out = os.path.join(os.path.expanduser('~'), 'datasets/kitti_final')
    for folder in ['images/train', 'images/val', 'labels/train', 'labels/val']:
        os.makedirs(os.path.join(base_out, folder), exist_ok=True)

    # Get all file stems (e.g., '000001') from the label files.
    # Skip dotfiles (e.g. macOS AppleDouble '._*.txt' companions) and use
    # splitext so a leading dot does not yield an empty stem.
    all_stems = [os.path.splitext(f)[0] for f in os.listdir(lbl_dir)
                 if f.endswith('.txt') and not f.startswith('.')]
    random.shuffle(all_stems)

    split_idx = int(len(all_stems) * train_ratio)
    train_stems = all_stems[:split_idx]
    val_stems = all_stems[split_idx:]

    def move_files(stems, subset):
        for stem in stems:
            # Copy image
            shutil.copy(os.path.join(img_dir, f"{stem}.png"),
                        os.path.join(base_out, f"images/{subset}/{stem}.png"))
            # Copy label
            shutil.copy(os.path.join(lbl_dir, f"{stem}.txt"),
                        os.path.join(base_out, f"labels/{subset}/{stem}.txt"))

    print(f"Splitting {len(all_stems)} images...")
    move_files(train_stems, 'train')
    move_files(val_stems, 'val')
    print(f"Done! Train: {len(train_stems)}, Val: {len(val_stems)} -> {base_out}")


if __name__ == "__main__":
    # Point this to the team datadrive's KITTI training folder.
    split_kitti('/team_data/datasets/kitti/training')
