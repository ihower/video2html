# pip install srt
# pip install requests

import os
import re
from pathlib import Path
import srt
import requests
import json
import sys

openai_api_key = os.environ["OPENAI_API_KEY"]

def get_completion(messages, model="gpt-4o-mini", temperature=0, max_tokens=4096, seed=None):
  payload = { "model": model, "temperature": temperature, "messages": messages, "max_tokens": max_tokens }
  if seed:
    payload["seed"] = seed
  headers = { "Authorization": f'Bearer {openai_api_key}', "Content-Type": "application/json" }
  response = requests.post('https://api.openai.com/v1/chat/completions', headers = headers, data = json.dumps(payload) )
  obj = json.loads(response.text)
  if response.status_code == 200 :
    return obj["choices"][0]["message"]["content"]
  else :
    return obj["error"]

def translate(source_text):
    return  '' # 第一次跑建議先不要翻譯，看看 html 結果沒問題，再註解掉這裡

    if source_text == '':
      return ''

    messages = [{  "role": "system",
        "content": """You are a professional, authentic translation engine, an AI who is skilled in translating English to Chinese Mandarin Taiwanese fluently. Your task is to translate an article or part of the full article which will be provided to you after you acknowledge this message and say you're ready.

Constraints:
* Do not change any of the wording in the text in such a way that the original meaning is changed unless you are fixing typos or correcting the article.
* When you translate a quote from somebody, please use 「」『』 instead of ""
* Don't chat or ask、不要問是否要翻譯、不要要求ㄨDO NOT "請問您需要翻譯整篇文章還是部分內容"、DO NOT "請提供完��的文章或段落"、DO NOT "抱歉"
Pleases always respond in Chinese Mandarin Taiwanese and Taiwan terms. When mixing Chinese and English, add a whitespace between Chinese and English characters.
* 縮寫 LLM 不要翻譯，直接顯示 LLM
* 不要翻譯英文人名

Remember this is NOT dialogue. DO NOT explain any sentences, only returns translations.
"""        },
        {
            "role": "user",
            "content": f"""Translate the following source text and output directly without any additional text.
Source Text: {source_text}
Translated Text:"""
        }
    ]

    response = get_completion(messages, temperature=0.1)

    print(response)
    return response

def get_srt_file(directory):
    srt_files = list(Path(directory).glob('*.srt'))
    if len(srt_files) != 1:
        raise ValueError("指定目錄中應該只有一個 .srt 檔案")
    return srt_files[0]

def get_jpg_files(directory):
    html_dir = Path(directory) / 'html'
    files = html_dir.glob('frame_*.jpg')
    jpg_files = sorted(files, key=lambda x: int(re.search(r'frame_(\d+)\.jpg', x.name).group(1)))

    if not jpg_files:
        raise ValueError("在指定目錄中找不到 frame_*.jpg 檔案")
    return jpg_files

def parse_frame_number(filename):
    match = re.search(r'frame_(\d+)\.jpg', filename.name)
    if match:
        return int(match.group(1))
    raise ValueError(f"無法解析檔案名稱: {filename}")

def generate_html(srt_file, jpg_files, input_directory, output_directory):
    with open(srt_file, 'r', encoding='utf-8') as f:
        srt_content = f.read()

    subtitles = list(srt.parse(srt_content))

    frame_numbers = [parse_frame_number(jpg) for jpg in jpg_files]
    min_frame = min(frame_numbers)

    html_content = """
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            table { width: 100%; border-collapse: collapse; }
            td { vertical-align: top; padding: 10px; border: 1px solid #ddd; }
            .subtitle { width: 60%; }
            .images { width: 40%; }
            img { max-width: 100%; height: auto; margin-bottom: 10px; }
            .timestamp { font-size: 0.8em; color: #666; }
        </style>
    </head>
    <body>
        <h1><h1>

        <h3></h3>

    <blockquote style="background-color: #ffffff; border-left: 5px solid #FF0000; border: 2px solid #000000; padding: 20px; max-width: 600px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); line-height: 1.6; color: #333; margin: 20px 0 20px 20px;">
        請注意，本網頁為程式自動產生，可能會有錯誤，請觀賞原影片做查核。
    </blockquote>

        <p>
        </p>
        <table>
    """

    subtitle_index = 0
    for i, (jpg, frame_number) in enumerate(zip(jpg_files, frame_numbers)):
        image_time = frame_number * 5 - min_frame * 5
        next_image_time = frame_numbers[i+1] * 5 - min_frame * 5 if i+1 < len(frame_numbers) else float('inf')

        # 延後字幕匹配的時間範圍
        if i == 0:
            subtitle_start_time = 0
        else:
            subtitle_start_time = frame_numbers[i-1] * 5 - min_frame * 5
        subtitle_end_time = image_time

        subtitle_content = []
        while subtitle_index < len(subtitles):
            sub = subtitles[subtitle_index]
            if subtitle_start_time <= sub.start.total_seconds() < subtitle_end_time:
                subtitle_content.append(sub.content)
                subtitle_index += 1
            elif sub.start.total_seconds() >= subtitle_end_time:
                break
            else:
                subtitle_index += 1

        subtitle_text = "<br>".join(subtitle_content) if subtitle_content else ""
        translated_text = translate(subtitle_text)

        html_content += '<tr>'
        html_content += f'<td class="subtitle"><p>{subtitle_text}</p>'

        if translated_text != '':
            html_content += f'<p style="border: 1px dashed black; padding: 10px;">{translated_text}</p>'

        html_content += f'</td>'

        html_content += f'<td class="images">'
        html_content += f'<img src="{jpg.name}" alt="frame_{frame_number}">'
        html_content += f'<p class="timestamp">圖片編號: {frame_number} 圖片時間: {image_time:.2f}秒</p>'
        html_content += '</td>'
        html_content += '</tr>'

    # 處理剩餘的字幕
    if subtitle_index < len(subtitles):
        remaining_subtitles = [sub.content for sub in subtitles[subtitle_index:]]
        remaining_text = " ".join(remaining_subtitles)
        html_content += '<tr>'
        html_content += f'<td class="subtitle">{remaining_text}</td>'
        html_content += '<td class="images"></td>'
        html_content += '</tr>'

    html_content += """
        </table>
    </body>
    </html>
    """

    output_file = Path(output_directory) / 'index.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    if len(sys.argv) != 2:
        print("使用方法: python build_html.py <目錄路徑>")
        sys.exit(1)

    input_directory = sys.argv[1]
    output_directory = Path(input_directory) / 'html'

    try:
        srt_file = get_srt_file(input_directory)
        jpg_files = get_jpg_files(input_directory)
        generate_html(srt_file, jpg_files, input_directory, output_directory)
        print(f"處理完成，結果已保存到 {output_directory}/index.html")
    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    main()