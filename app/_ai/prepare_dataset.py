# app/ai/prepare_dataset.py
"""
Merges train/ + val/ + test/ into a single flat dataset,
keeps only the 3 target classes, then augments to reach TARGET_PER_CLASS.

Run:
    python -m app.ai.prepare_dataset

Output:
    app/ai/datasets_clean/
        Black_Pod_Disease/   (~300+ images)
        Frosty_Pod_Rot/      (~300+ images)
        Healthy/             (~300+ images)
"""

import os
import cv2
import random
import shutil
import numpy as np
from pathlib import Path

# ================================================================
# CONFIG
# ================================================================

SPLITS          = ["train", "val", "test"]
SOURCE_BASE     = Path("app/ai/datasets")
OUTPUT_DIR      = Path("app/ai/datasets_clean")
TARGET_CLASSES  = ["Black_Pod_Disease", "Frosty_Pod_Rot", "Healthy"]
TARGET_PER_CLASS = 300
IMG_SIZE        = (224, 224)
BLUR_THRESHOLD  = 80.0
MIN_SIZE        = 100
SEED            = 42

random.seed(SEED)
np.random.seed(SEED)

# ================================================================
# QUALITY CHECKS
# ================================================================

def is_blurry(img) -> bool:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var() < BLUR_THRESHOLD

def is_too_small(img) -> bool:
    h, w = img.shape[:2]
    return h < MIN_SIZE or w < MIN_SIZE

def is_valid(path: str):
    img = cv2.imread(path)
    if img is None:
        return False
    if is_too_small(img):
        return False
    if is_blurry(img):
        return False
    return True

# ================================================================
# AUGMENTATION  — aggressive to compensate for small dataset
# ================================================================

def augment(img):
    augmented = []

    # 1. Horizontal flip
    augmented.append(cv2.flip(img, 1))

    # 2. Vertical flip
    augmented.append(cv2.flip(img, 0))

    # 3. Rotation +20
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w//2, h//2), 20, 1)
    augmented.append(cv2.warpAffine(img, M, (w, h)))

    # 4. Rotation -20
    M = cv2.getRotationMatrix2D((w//2, h//2), -20, 1)
    augmented.append(cv2.warpAffine(img, M, (w, h)))

    # 5. Brightness up
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.3, 0, 255)
    augmented.append(cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR))

    # 6. Brightness down
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 0.7, 0, 255)
    augmented.append(cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR))

    # 7. Gaussian blur (simulate out-of-focus phone camera)
    augmented.append(cv2.GaussianBlur(img, (5, 5), 0))

    # 8. Zoom in (center crop + resize)
    crop_size = int(min(h, w) * 0.8)
    start_y = (h - crop_size) // 2
    start_x = (w - crop_size) // 2
    cropped = img[start_y:start_y+crop_size, start_x:start_x+crop_size]
    augmented.append(cv2.resize(cropped, (w, h)))

    # 9. Flip + rotation combo
    flipped = cv2.flip(img, 1)
    M = cv2.getRotationMatrix2D((w//2, h//2), 15, 1)
    augmented.append(cv2.warpAffine(flipped, M, (w, h)))

    # 10. Saturation boost (vivid colours — common in phone cameras)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.4, 0, 255)
    augmented.append(cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR))

    return augmented  # 10 augmented versions per image

# ================================================================
# STEP 1 — MERGE
# ================================================================

def merge():
    print("\n📦 STEP 1: Merging train/ + val/ + test/ ...\n")

    merged_dir = Path("app/ai/datasets_merged")
    merged_dir.mkdir(parents=True, exist_ok=True)

    total_copied = 0

    for cls in TARGET_CLASSES:
        cls_out = merged_dir / cls
        cls_out.mkdir(parents=True, exist_ok=True)

        count = 0
        for split in SPLITS:
            src = SOURCE_BASE / split / cls
            if not src.exists():
                print(f"  ⚠️  Missing: {src}")
                continue

            for img_file in src.iterdir():
                if img_file.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
                    continue

                # Unique name to avoid collisions across splits
                dest_name = f"{split}_{img_file.name}"
                dest = cls_out / dest_name

                if not dest.exists():
                    shutil.copy2(str(img_file), str(dest))
                    count += 1

        print(f"  ✅ {cls}: {count} images merged")
        total_copied += count

    print(f"\n  Total merged: {total_copied} images → {merged_dir}\n")
    return merged_dir

# ================================================================
# STEP 2 — CLEAN
# ================================================================

def clean(merged_dir: Path):
    print("🔍 STEP 2: Cleaning (removing blurry/small/corrupt) ...\n")

    removed = 0
    for cls in TARGET_CLASSES:
        cls_path = merged_dir / cls
        before = len(list(cls_path.iterdir()))

        for img_file in list(cls_path.iterdir()):
            if not is_valid(str(img_file)):
                img_file.unlink()
                removed += 1

        after = len(list(cls_path.iterdir()))
        print(f"  {cls}: {before} → {after} ({before - after} removed)")

    print(f"\n  Total removed: {removed}\n")

# ================================================================
# STEP 3 — AUGMENT TO TARGET
# ================================================================

def augment_to_target(merged_dir: Path):
    print(f"🔁 STEP 3: Augmenting to {TARGET_PER_CLASS} per class ...\n")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for cls in TARGET_CLASSES:
        src_dir  = merged_dir / cls
        out_dir  = OUTPUT_DIR / cls
        out_dir.mkdir(parents=True, exist_ok=True)

        # Copy originals first
        originals = list(src_dir.iterdir())
        for img_file in originals:
            dest = out_dir / img_file.name
            if not dest.exists():
                shutil.copy2(str(img_file), str(dest))

        current_count = len(list(out_dir.iterdir()))
        print(f"  {cls}: {current_count} originals", end="")

        if current_count >= TARGET_PER_CLASS:
            print(f" — already at target ✅")
            continue

        # Augment until target reached
        aug_idx = 0
        source_images = list(src_dir.iterdir())
        random.shuffle(source_images)

        while current_count < TARGET_PER_CLASS:
            for img_file in source_images:
                if current_count >= TARGET_PER_CLASS:
                    break

                img = cv2.imread(str(img_file))
                if img is None:
                    continue

                img = cv2.resize(img, IMG_SIZE)
                aug_versions = augment(img)

                for aug_img in aug_versions:
                    if current_count >= TARGET_PER_CLASS:
                        break

                    aug_name = f"aug_{aug_idx:04d}_{img_file.name}"
                    cv2.imwrite(str(out_dir / aug_name), aug_img)
                    aug_idx += 1
                    current_count += 1

        print(f" → {current_count} after augmentation ✅")

# ================================================================
# STEP 4 — REPORT
# ================================================================

def report():
    print(f"\n📊 FINAL DATASET REPORT ({OUTPUT_DIR})\n")
    print(f"  {'Class':<30} {'Count':>6}  {'Status'}")
    print("  " + "-"*50)

    all_good = True
    for cls in TARGET_CLASSES:
        cls_path = OUTPUT_DIR / cls
        count = len(list(cls_path.iterdir())) if cls_path.exists() else 0
        status = "✅ Ready" if count >= TARGET_PER_CLASS else f"⚠️  Need {TARGET_PER_CLASS - count} more"
        if count < TARGET_PER_CLASS:
            all_good = False
        print(f"  {cls:<30} {count:>6}  {status}")

    print()
    if all_good:
        print("  🚀 Dataset ready! Run:")
        print("     python -m app.ai.train")
    else:
        print("  ⚠️  Some classes are below target.")
        print("     Consider adding more source images from Roboflow/Kaggle.")
    print()

# ================================================================
# MAIN
# ================================================================

if __name__ == "__main__":
    print("=" * 55)
    print("  Boa Mi Cocoa — Dataset Preparation")
    print("=" * 55)

    merged = merge()
    clean(merged)
    augment_to_target(merged)
    report()