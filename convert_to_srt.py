from vtt_to_srt.vtt_to_srt import ConvertFile

convert_file = ConvertFile("transcript.vtt", "utf-8")
convert_file.convert()