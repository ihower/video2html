# pip install imagehash

import numpy as np
import os
from PIL import Image
import time
import imagehash
import sys

def remove_duplicates(folder_path, hash_size, threshold):
    images = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".jpg"):
            img_path = os.path.join(folder_path, filename)
            images.append((filename, img_path))

    unique_images = []
    hashes = []

    for filename, img_path in images:
        # 讀取原始圖片
        img = Image.open(img_path)

        # 調整大小到 960x540
        img_resized = img.resize((1280, 720), Image.LANCZOS)

        # 計算 pHash
        hash = imagehash.phash(img_resized, hash_size=hash_size)

        if not any(hash - h <= threshold for h in hashes):
            # 保存縮小後的圖片
            resized_path = os.path.join(folder_path, f"resized_{filename}")
            img_resized.save(resized_path, "JPEG", quality=95)

            unique_images.append(f"resized_{filename}")
            hashes.append(hash)

        # 刪除原始大小的圖片
        os.remove(img_path)

    # 重命名所有縮小後的圖片，移除 "resized_" 前綴
    for filename in unique_images:
        old_path = os.path.join(folder_path, filename)
        new_path = os.path.join(folder_path, filename.replace("resized_", ""))
        os.rename(old_path, new_path)

    print(f"移除了 {len(images) - len(unique_images)} 個重複幀")
    print(f"保留了 {len(unique_images)} 個唯一幀")


def main():
    if len(sys.argv) != 2:
        print("Usage: python process-image.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]
    print(f"Processing images in folder: {folder_path}")


    remove_duplicates(folder_path, hash_size=16, threshold=8)

if __name__ == "__main__":
    main()