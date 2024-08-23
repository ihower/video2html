# pip install opencv-python
# pip install Pillow


import cv2
import numpy as np
import os
from PIL import Image
import time
import argparse

#  youtube-dl https://www.youtube.com/watch?v=5zE2sMka620 --cookies www.youtube.com_cookies.txt
def extract_frames(video_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    frame_count = 0
    saved_count = 0
    last_report_time = 0
    start_time = time.time()

    # 計算每 5 秒對應的幀數
    frames_per_extract = int(fps * 5)

    while True:
        success, frame = video.read()
        if not success:
            break

        current_time = frame_count / fps

        # 每 5 秒截圖一張
        if frame_count % frames_per_extract == 0:
            frame_path = os.path.join(output_folder, f"frame_{saved_count}.jpg")
            cv2.imwrite(frame_path, frame)
            saved_count += 1

        # 每 10 分鐘報告進度
        if current_time - last_report_time >= 600:  # 600 秒 = 10 分鐘
            minutes = int(current_time / 60)
            seconds = int(current_time % 60)
            print(f"當前進度：{minutes:02d}:{seconds:02d}")
            last_report_time = current_time

        frame_count += 1

    video.release()

    end_time = time.time()
    process_duration = end_time - start_time
    print(f"視頻處理完成。總時長：{duration:.2f} 秒")
    print(f"已保存 {saved_count} 幀")
    print(f"處理時間：{process_duration:.2f} 秒")

def remove_duplicates(folder_path):
    images = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".jpg"):
            img_path = os.path.join(folder_path, filename)
            img = Image.open(img_path).convert('RGB')
            images.append((filename, np.array(img)))

    unique_images = []
    for filename, img in images:
        if not any(np.array_equal(img, u_img) for _, u_img in unique_images):
            unique_images.append((filename, img))
        else:
            os.remove(os.path.join(folder_path, filename))

    print(f"移除了 {len(images) - len(unique_images)} 個完全重複幀")

def main():
    parser = argparse.ArgumentParser(description='Extract frames from a video and remove duplicates.')
    parser.add_argument('video_path', type=str, help='Path to the input video file')
    parser.add_argument('-o', '--output', type=str, help='Output folder name (default: video filename without extension)')
    args = parser.parse_args()

    video_path = args.video_path
    if not os.path.exists(video_path):
        print(f"錯誤：找不到視頻文件 '{video_path}'")
        return

    if args.output:
        output_folder = args.output
    else:
        # 使用視頻文件名（不包括擴展名）作為輸出文件夾名
        output_folder = "html"

    output_folder = os.path.join(os.path.dirname(video_path), output_folder)

    print(f"處理視頻：{video_path}")
    print(f"輸出文件夾：{output_folder}")

    extract_frames(video_path, output_folder)
    # remove_duplicates(output_folder)

if __name__ == "__main__":
    main()