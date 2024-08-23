import sys
import os
from pytubefix import YouTube
from pytubefix.cli import on_progress

# 檢查是否提供了 URL 參數
if len(sys.argv) < 2:
    print("請提供 YouTube 影片 URL 作為參數")
    print("使用方式: python download_youtube.py https://www.youtube.com/watch?v=xxxx")
    sys.exit(1)

url = sys.argv[1]

yt = YouTube(url, on_progress_callback = on_progress)

# 創建目錄名稱
dir_name = yt.title.replace(' ', '_').lower()

# 創建目錄
os.makedirs(dir_name, exist_ok=True)

print(f"正在下載: {yt.title}")
print(f"保存到目錄: {dir_name}")

# 這個視訊的品質不好
#ys = yt.streams.get_highest_resolution()
#ys.download()

# 只有 mp3
#ys = yt.streams.get_audio_only()
#ys.download(mp3=True) 

# https://github.com/JuanBindez/pytubefix/issues/128
# 會分開下載
video_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('resolution').desc().first()
audio_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).order_by('abr').desc().first()

print("正在下載視頻...")
video_stream.download(output_path=dir_name, filename='video.mp4')
print("正在下載音頻...")
audio_stream.download(output_path=dir_name, filename='audio.mp4')

print("下載完成！")