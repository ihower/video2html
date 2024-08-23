# Video2HTML

注意: 適合採用投影片的影片

以下 https://www.youtube.com/watch?v=bjNYEc908oQ Building Reliable Agentic Systems: Eno Reyes 影片為例:

## 1. 下載 video 檔案

安裝 pip insatll pip install pytubefix

> python download_youtube.py https://www.youtube.com/watch?v=bjNYEc908oQ

下載影片，這會建立 building_reliable_agentic_systems_eno_reyes 目錄並將 video.mp4 (這沒有聲音) 和 audio.mp4 (這只有聲音) 放到目錄內

## 2. 準備 audio 檔案 -> 轉成 srt 字幕檔案

推薦用 macwhisper 任何工具可以語音辨識的工具，將 audio.mp4 轉成 srt 字幕檔案。
字幕檔案請存成 transcript.srt 放在相同 building_reliable_agentic_systems_eno_reyes 目錄下

如果你拿到 vtt 檔案，可以用 convert_to_srt.py 進行轉換，需安裝 pip install vtt-to-srt

## 3. 擷取圖片

> python extract.py building_reliable_agentic_systems_eno_reyes/video.mp4

這會每 5 秒擷取一張圖片，放在 building_reliable_agentic_systems_eno_reyes/html 目錄下


## 4. 刪減重複圖片

> python process-images.py building_reliable_agentic_systems_eno_reyes/html

這會刪剪 building_reliable_agentic_systems_eno_reyes/html 目錄下的圖片 frame_xxx.jpg

這個部分建議人工檢查 building_reliable_agentic_systems_eno_reyes/html 目錄下的圖片

* 程式中的 remove_duplicates(folder_path, hash_size=16, threshold=8) 你可以調高 threshold 再跑一次，刪更多重複的
* 也可以人工刪除，看到重複的圖片就刪掉，但最好保持適當時間間距，因為圖片會搭配對應的幾段字幕

## 5. 產生 HTML

> python build_html.py building_reliable_agentic_systems_eno_reyes

如此就會產生 building_reliable_agentic_systems_eno_reyes/html/index.html

* 翻譯部分是 translation function，預設我先 return  '' 不要翻譯
* 第一次跑建議先不要做翻譯，先看看出來的 HTML 結果如何: 主要是看圖片是不是太多了，造成單一個 frame 對應的文字太少。如果是，就繼續刪重複圖片。
* 如果ok，就可以打開翻譯，產生最終 HTML 版本
