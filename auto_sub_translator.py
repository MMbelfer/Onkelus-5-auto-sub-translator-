import tkinter as tk
from tkinter import filedialog
import os
import subprocess
import json
from deep_translator import GoogleTranslator
from concurrent.futures import ThreadPoolExecutor


def get_subtitle_tracks(video_path):
    print("סורק את הוידאו...")
    command = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "s",
        "-show_entries",
        "stream=index:stream_tags=language,title",
        "-of",
        "json",
        video_path,
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        return [
            f"רצועה {s.get('index')}: {s.get('tags', {}).get('language', 'unknown')}"
            for s in data.get("streams", [])
        ]
    except:
        return []


def choose_track_ui(tracks):
    popup = tk.Toplevel()
    popup.title("בחירת כתוביות")
    selected = tk.StringVar(popup)
    selected.set(tracks[0])
    tk.Label(popup, text="בחר רצועה לתרגום:").pack(pady=5)
    tk.OptionMenu(popup, selected, *tracks).pack(pady=5)
    tk.Button(popup, text="אישור", command=popup.quit).pack(pady=5)
    popup.mainloop()
    res = selected.get()
    popup.destroy()
    return res


# --- פונקציית התרגום המקבילית (הסופר-מהירה) של פייתון ---
def process_single_line(line):
    text = line.strip()
    # מסננים שורות ריקות, מספרים רציפים וזמנים
    if text and not text.isdigit() and "-->" not in text:
        try:
            # כל תהליכון פותח "חיבור" משלו לגוגל
            translated = GoogleTranslator(source="en", target="iw").translate(text)
            return translated + "\n"
        except:
            return line  # במקרה של שגיאה נקודתית, מחזירים את המקור
    return line


def translate_srt_fast(input_file, output_file):
    print("מתחיל בתרגום מקבילי מהיר (Multithreading)...")

    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # שימוש ב-20 תהליכונים במקביל כדי לשלוח בקשות לגוגל
    with ThreadPoolExecutor(max_workers=20) as executor:
        translated_lines = list(executor.map(process_single_line, lines))

    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines(translated_lines)


# --- הרצה מרכזית ---
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(
    title="בחר וידאו", filetypes=[("Video", "*.mkv *.mp4 *.avi")]
)

if file_path:
    tracks = get_subtitle_tracks(file_path)
    if tracks:
        chosen = choose_track_ui(tracks)
        track_index = chosen.split(":")[0].replace("רצועה ", "")

        base_name = os.path.splitext(file_path)[0]
        temp_srt = f"{base_name}_temp.srt"
        final_srt = f"{base_name}_HEBREW.srt"

        # 1. חילוץ מהיר עם FFmpeg
        print("\nמחלץ כתוביות...")
        subprocess.run(
            ["ffmpeg", "-y", "-i", file_path, "-map", f"0:{track_index}", temp_srt],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # 2. תרגום מהיר בפייתון (מחליף את Subtitle Edit)
        translate_srt_fast(temp_srt, final_srt)

        # 3. ניקיון
        if os.path.exists(temp_srt):
            os.remove(temp_srt)

        print(f"\nבוצע בהצלחה! הקובץ המתורגם מחכה לך כאן:\n{final_srt}")
else:
    print("בוטל.")
input("\nלחץ Enter לסיום...")
