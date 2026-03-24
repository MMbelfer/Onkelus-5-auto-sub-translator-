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

# import tkinter as tk
# from tkinter import filedialog
# import os
# import subprocess
# import json


# def get_subtitle_tracks(video_path):
#     print("סורק את הוידאו...")
#     command = [
#         "ffprobe",
#         "-v",
#         "error",
#         "-select_streams",
#         "s",
#         "-show_entries",
#         "stream=index:stream_tags=language,title",
#         "-of",
#         "json",
#         video_path,
#     ]
#     try:
#         result = subprocess.run(command, capture_output=True, text=True, check=True)
#         data = json.loads(result.stdout)
#         return [
#             f"רצועה {s.get('index')}: {s.get('tags', {}).get('language', 'unknown')}"
#             for s in data.get("streams", [])
#         ]
#     except:
#         return []


# def choose_track_ui(tracks):
#     popup = tk.Toplevel()
#     popup.title("בחירת כתוביות")
#     selected = tk.StringVar(popup)
#     selected.set(tracks[0])
#     tk.Label(popup, text="בחר רצועה לתרגום:").pack(pady=5)
#     tk.OptionMenu(popup, selected, *tracks).pack(pady=5)
#     tk.Button(popup, text="אישור", command=popup.quit).pack(pady=5)
#     popup.mainloop()
#     res = selected.get()
#     popup.destroy()
#     return res


# def translate_with_se_cli(input_srt, output_srt):
#     print("מתחיל בתרגום מהיר לעברית בעזרת Subtitle Edit...")

#     # חזרנו לפקודה המקורית, אך שינינו את הקוד ל-he (Hebrew)
#     se_command = [
#         "SubtitleEdit",
#         "/convert",
#         input_srt,
#         "SubRip",
#         "/googletranslate:he",
#         f"/outputfilename:{output_srt}",
#     ]

#     try:
#         # התוספת הקריטית: הגדרת קידוד utf-8 והתעלמות משגיאות טקסט
#         result = subprocess.run(
#             se_command,
#             capture_output=True,
#             text=True,
#             encoding="utf-8",
#             errors="ignore",
#         )

#         if result.returncode == 0:
#             return True
#         else:
#             print(f"\nהתרגום נכשל. הודעת השגיאה מ-Subtitle Edit:")
#             # עכשיו נוכל לראות את השגיאה האמיתית אם היא תקרה, בלי שפייתון תקרוס
#             print(result.stderr if result.stderr else result.stdout)
#             return False

#     except Exception as e:
#         print(f"\nשגיאה בהרצת פקודת התרגום: {e}")
#         return False


# # --- פונקציית התרגום החדשה והמהירה בעזרת Subtitle Edit ---
# # def translate_with_se_cli(input_srt, output_srt):
# #     print("מתחיל בתרגום מהיר לעברית בעזרת Subtitle Edit...")

# #     # הפקודה המהירה ל-CLI של Subtitle Edit
# #     se_command = [
# #         "SubtitleEdit",
# #         "/convert",
# #         input_srt,
# #         "SubRip",
# #         "/translate:google:iw",  # הפורמט החדש (Translate במקום GoogleTranslate)
# #         f"/outputfilename:{output_srt}",
# #     ]

# #     try:
# #         # הפעלה חרישית (בלי חלונות קופצים)
# #         subprocess.run(
# #             se_command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
# #         )
# #         return True
# #     except FileNotFoundError:
# #         print(
# #             "\nשגיאה: Subtitle Edit לא נמצא ב-PATH שלך. אנא ודא שהוספת אותו למשתני הסביבה."
# #         )
# #         return False
# #     except Exception as e:
# #         print(f"\nשגיאה בתרגום: {e}")
# #         return False


# # --- הרצה מרכזית ---
# root = tk.Tk()
# root.withdraw()
# file_path = filedialog.askopenfilename(
#     title="בחר וידאו", filetypes=[("Video", "*.mkv *.mp4 *.avi")]
# )

# if file_path:
#     tracks = get_subtitle_tracks(file_path)
#     if tracks:
#         chosen = choose_track_ui(tracks)
#         track_index = chosen.split(":")[0].replace("רצועה ", "")

#         base_name = os.path.splitext(file_path)[0]
#         temp_srt = f"{base_name}_temp.srt"
#         final_srt = f"{base_name}_HEBREW.srt"

#         # 1. חילוץ (בעזרת FFmpeg - מהיר מאוד)
#         print("\nמחלץ כתוביות...")
#         subprocess.run(
#             ["ffmpeg", "-y", "-i", file_path, "-map", f"0:{track_index}", temp_srt],
#             stdout=subprocess.DEVNULL,
#             stderr=subprocess.DEVNULL,
#         )

#         # 2. תרגום (בעזרת Subtitle Edit - מהיר מאוד)
#         if translate_with_se_cli(temp_srt, final_srt):
#             # 3. ניקיון
#             if os.path.exists(temp_srt):
#                 os.remove(temp_srt)
#             print(f"\nבוצע בהצלחה! הקובץ המתורגם מחכה לך כאן:\n{final_srt}")
#         else:
#             print("\nהתרגום נכשל.")
# else:
#     print("בוטל.")
# input("\nלחץ Enter לסיום...")


# import tkinter as tk
# from tkinter import filedialog
# import os
# import subprocess
# import json
# from deep_translator import GoogleTranslator


# def get_subtitle_tracks(video_path):
#     print("סורק את הוידאו...")
#     command = [
#         "ffprobe",
#         "-v",
#         "error",
#         "-select_streams",
#         "s",
#         "-show_entries",
#         "stream=index:stream_tags=language,title",
#         "-of",
#         "json",
#         video_path,
#     ]
#     try:
#         result = subprocess.run(command, capture_output=True, text=True, check=True)
#         data = json.loads(result.stdout)
#         return [
#             f"רצועה {s.get('index')}: {s.get('tags', {}).get('language', 'unknown')}"
#             for s in data.get("streams", [])
#         ]
#     except:
#         return []


# def choose_track_ui(tracks):
#     popup = tk.Toplevel()
#     popup.title("בחירת כתוביות")
#     selected = tk.StringVar(popup)
#     selected.set(tracks[0])
#     tk.Label(popup, text="בחר רצועה לתרגום:").pack(pady=5)
#     tk.OptionMenu(popup, selected, *tracks).pack(pady=5)
#     tk.Button(popup, text="אישור", command=popup.quit).pack(pady=5)
#     popup.mainloop()
#     res = selected.get()
#     popup.destroy()
#     return res


# # --- פונקציית התרגום החדשה ---
# def translate_srt(input_file, output_file):
#     print("מתחיל בתרגום לעברית (זה עשוי לקחת רגע, תלוי באורך הקובץ)...")
#     translator = GoogleTranslator(source="en", target="iw")  # iw = Hebrew

#     with open(input_file, "r", encoding="utf-8") as f:
#         lines = f.readlines()

#     translated_lines = []
#     for line in lines:
#         # אנחנו מתרגמים רק שורות שהן טקסט (לא מספרים ולא זמני כתוביות)
#         if line.strip() and not line.strip().isdigit() and "-->" not in line:
#             try:
#                 translated_lines.append(translator.translate(line))
#             except:
#                 translated_lines.append(line)  # אם התרגום נכשל, נשאיר את המקור
#         else:
#             translated_lines.append(line)

#     with open(output_file, "w", encoding="utf-8") as f:
#         f.writelines(translated_lines)


# # --- הרצה מרכזית ---
# root = tk.Tk()
# root.withdraw()
# file_path = filedialog.askopenfilename(
#     title="בחר וידאו", filetypes=[("Video", "*.mkv *.mp4 *.avi")]
# )

# if file_path:
#     tracks = get_subtitle_tracks(file_path)
#     if tracks:
#         chosen = choose_track_ui(tracks)
#         track_index = chosen.split(":")[0].replace("רצועה ", "")

#         base_name = os.path.splitext(file_path)[0]
#         temp_srt = f"{base_name}_temp.srt"
#         final_srt = f"{base_name}_HEBREW.srt"

#         # חילוץ
#         subprocess.run(
#             ["ffmpeg", "-y", "-i", file_path, "-map", f"0:{track_index}", temp_srt],
#             stdout=subprocess.DEVNULL,
#             stderr=subprocess.DEVNULL,
#         )

#         # תרגום
#         translate_srt(temp_srt, final_srt)

#         # ניקיון: מחיקת קובץ ה-temp הזמני
#         if os.path.exists(temp_srt):
#             os.remove(temp_srt)

#         print(f"\nבוצע בהצלחה! הקובץ המתורגם מחכה לך כאן:\n{final_srt}")
# else:
#     print("בוטל.")
# input("\nלחץ Enter לסיום...")

########
# import tkinter as tk
# from tkinter import filedialog
# import os
# import subprocess
# import json


# def get_subtitle_tracks(video_path):
#     print("סורק את הוידאו למציאת כתוביות...")
#     command = [
#         "ffprobe",
#         "-v",
#         "error",
#         "-select_streams",
#         "s",
#         "-show_entries",
#         "stream=index:stream_tags=language,title",
#         "-of",
#         "json",
#         video_path,
#     ]
#     try:
#         result = subprocess.run(command, capture_output=True, text=True, check=True)
#         data = json.loads(result.stdout)
#         tracks = []
#         for stream in data.get("streams", []):
#             index = stream.get("index")
#             tags = stream.get("tags", {})
#             lang = tags.get("language", "לא ידוע")
#             title = tags.get("title", "")
#             track_info = f"רצועה {index}: {lang}"
#             if title:
#                 track_info += f" - {title}"
#             tracks.append(track_info)
#         return tracks
#     except Exception as e:
#         return [f"שגיאה בסריקה: {e}"]


# def choose_track_ui(tracks):
#     popup = tk.Toplevel()
#     popup.title("בחירת כתוביות")
#     popup.geometry("350x150")
#     tk.Label(popup, text="נמצאו הכתוביות הבאות. בחר מה לחלץ:", font=("Arial", 10)).pack(
#         pady=10
#     )

#     selected_track = tk.StringVar(popup)
#     selected_track.set(tracks[0])

#     dropdown = tk.OptionMenu(popup, selected_track, *tracks)
#     dropdown.pack(pady=5)

#     def on_confirm():
#         popup.quit()

#     tk.Button(popup, text="אישור", command=on_confirm).pack(pady=10)
#     popup.mainloop()
#     choice = selected_track.get()
#     popup.destroy()
#     return choice


# # --- תחילת התוכנית המרכזית ---
# root = tk.Tk()
# root.withdraw()
# print("פותח חלון בחירת קובץ...")

# file_path = filedialog.askopenfilename(
#     title="בחר קובץ וידאו עם כתוביות מובנות",
#     filetypes=[("Video files", "*.mkv *.mp4 *.avi"), ("All files", "*.*")],
# )

# if file_path:
#     print(f"הקובץ שנבחר: {file_path}")
#     real_tracks = get_subtitle_tracks(file_path)

#     if not real_tracks:
#         print("\nלא נמצאו כתוביות מובנות בקובץ הזה.")
#     elif "שגיאה" in real_tracks[0]:
#         print(f"\n{real_tracks[0]}")
#     else:
#         chosen = choose_track_ui(real_tracks)
#         print(f"\n>> בחרת: {chosen}")

#         # --- התוספת החדשה: חילוץ המספר והפעלת FFmpeg ---

#         # חילוץ המספר בלבד מתוך הטקסט (למשל מתוך "רצועה 2: eng")
#         track_index = chosen.split(":")[0].replace("רצועה ", "")

#         base_name = os.path.splitext(file_path)[0]
#         # כרגע נקרא לקובץ 'extracted' כי הוא עדיין באנגלית. בשלב הבא נתרגם אותו.
#         output_file = f"{base_name}_extracted.srt"

#         print(f"\nמתחיל לחלץ את רצועה {track_index} בעזרת FFmpeg...")

#         extract_command = [
#             "ffmpeg",
#             "-y",  # דורס את הקובץ אם הוא כבר קיים
#             "-i",
#             file_path,  # קובץ המקור
#             "-map",
#             f"0:{track_index}",  # הרצועה הספציפית שבחרנו
#             output_file,  # הקובץ שישמר
#         ]

#         try:
#             # מריץ את הפקודה ומסתיר את כל הטקסט המיותר ש-FFmpeg פולט בדרך כלל
#             subprocess.run(
#                 extract_command,
#                 check=True,
#                 stdout=subprocess.DEVNULL,
#                 stderr=subprocess.DEVNULL,
#             )
#             print(f"החילוץ עבר בהצלחה! הקובץ הזמני נוצר בתיקייה: {output_file}")
#             print("השלב הבא יהיה לתרגם אותו לעברית!")
#         except Exception as e:
#             print(f"שגיאה בחילוץ: {e}")

# else:
#     print("לא נבחר קובץ. התוכנית מסתיימת.")

# input("\nלחץ Enter כדי לסיים...")

#####
# import tkinter as tk
# from tkinter import filedialog
# import os
# import subprocess
# import json


# # --- פונקציה חדשה: סריקת הוידאו עם ffprobe ---
# def get_subtitle_tracks(video_path):
#     print("סורק את הוידאו למציאת כתוביות (זה ייקח שנייה)...")

#     # הפקודה שאנחנו שולחים ל-ffprobe: "תביא רק כתוביות (s) בפורמט json"
#     command = [
#         "ffprobe",
#         "-v",
#         "error",
#         "-select_streams",
#         "s",
#         "-show_entries",
#         "stream=index:stream_tags=language,title",
#         "-of",
#         "json",
#         video_path,
#     ]

#     try:
#         # הרצת הפקודה ולכידת הפלט
#         result = subprocess.run(command, capture_output=True, text=True, check=True)
#         data = json.loads(result.stdout)

#         tracks = []
#         for stream in data.get("streams", []):
#             index = stream.get("index")
#             tags = stream.get("tags", {})
#             lang = tags.get("language", "לא ידוע")  # אם אין תווית שפה
#             title = tags.get("title", "")

#             # בניית שורת טקסט יפה להצגה בתפריט הנגלל
#             track_info = f"רצועה {index}: {lang}"
#             if title:
#                 track_info += f" - {title}"
#             tracks.append(track_info)

#         return tracks
#     except Exception as e:
#         return [f"שגיאה בסריקה: {e}"]


# # --- פונקציית חלון הבחירה (עברה שינוי קל כדי לטפל במקרה שאין כתוביות) ---
# def choose_track_ui(tracks):
#     popup = tk.Toplevel()
#     popup.title("בחירת כתוביות")
#     popup.geometry("350x150")

#     tk.Label(
#         popup, text="נמצאו הכתוביות הבאות. בחר מה לתרגם:", font=("Arial", 10)
#     ).pack(pady=10)

#     selected_track = tk.StringVar(popup)
#     selected_track.set(tracks[0])

#     dropdown = tk.OptionMenu(popup, selected_track, *tracks)
#     dropdown.pack(pady=5)

#     def on_confirm():
#         popup.quit()

#     tk.Button(popup, text="אישור", command=on_confirm).pack(pady=10)

#     popup.mainloop()
#     choice = selected_track.get()
#     popup.destroy()
#     return choice


# # --- תחילת התוכנית המרכזית ---
# root = tk.Tk()
# root.withdraw()

# print("פותח חלון בחירת קובץ...")

# file_path = filedialog.askopenfilename(
#     title="בחר קובץ וידאו עם כתוביות מובנות",
#     filetypes=[("Video files", "*.mkv *.mp4 *.avi"), ("All files", "*.*")],
# )

# if file_path:
#     print(f"הקובץ שנבחר: {file_path}")

#     # הפעלת הסורק האמיתי!
#     real_tracks = get_subtitle_tracks(file_path)

#     # בדיקה אם בכלל נמצאו כתוביות או שהייתה שגיאה
#     if not real_tracks:
#         print("\nלא נמצאו כתוביות מובנות בקובץ הזה.")
#     elif "שגיאה" in real_tracks[0]:
#         print(f"\n{real_tracks[0]}")
#     else:
#         # הקפצת החלון עם הרשימה האמיתית
#         chosen = choose_track_ui(real_tracks)
#         print(f"\n>> מעולה! בחרת לתרגם את: {chosen}")

#         base_name = os.path.splitext(file_path)[0]
#         output_file = f"{base_name}_HE.srt"
#         print(f">> קובץ הכתוביות העתידי ישמר בשם: {output_file}")

# else:
#     print("לא נבחר קובץ. התוכנית מסתיימת.")

# input("\nלחץ Enter כדי לסיים...")


# import tkinter as tk
# from tkinter import filedialog
# import os


# # --- פונקציה חדשה: יצירת חלון קופץ לבחירת השפה ---
# def choose_track_ui(tracks):
#     popup = tk.Toplevel()
#     popup.title("בחירת כתוביות")
#     popup.geometry("300x150")

#     # טקסט הסבר
#     tk.Label(popup, text="בחר איזו רצועת כתוביות לתרגם:", font=("Arial", 10)).pack(
#         pady=10
#     )

#     # משתנה שישמור את הבחירה שלנו
#     selected_track = tk.StringVar(popup)
#     selected_track.set(tracks[0])  # ברירת המחדל היא האפשרות הראשונה

#     # תפריט נגלל (Dropdown)
#     dropdown = tk.OptionMenu(popup, selected_track, *tracks)
#     dropdown.pack(pady=5)

#     # פונקציה שמופעלת כשלוחצים על "אישור"
#     def on_confirm():
#         popup.quit()  # משחרר את העצירה של החלון

#     tk.Button(popup, text="אישור", command=on_confirm).pack(pady=10)

#     # עוצר את התוכנית עד שהמשתמש לוחץ על אישור
#     popup.mainloop()

#     choice = selected_track.get()
#     popup.destroy()  # סוגר את החלון הקטן
#     return choice


# # --- תחילת התוכנית המרכזית ---
# root = tk.Tk()
# root.withdraw()

# print("פותח חלון בחירת קובץ...")

# # 1. המשתמש בוחר את הוידאו
# file_path = filedialog.askopenfilename(
#     title="בחר קובץ וידאו עם כתוביות מובנות",
#     filetypes=[("Video files", "*.mkv *.mp4 *.avi"), ("All files", "*.*")],
# )

# if file_path:
#     print(f"הקובץ שנבחר: {file_path}")

#     # 2. רשימה מדומה זמנית (בשלב הבא נחליף אותה בסורק האמיתי שקורא מהוידאו)
#     fake_tracks = ["1: אנגלית (English)", "2: רוסית (Russian)", "3: צרפתית (French)"]

#     # 3. קריאה לחלון שבנינו
#     chosen = choose_track_ui(fake_tracks)
#     print(f"\n>> מעולה! בחרת לתרגם את: {chosen}")

#     # 4. הכנת השם לקובץ העתידי
#     base_name = os.path.splitext(file_path)[0]
#     output_file = f"{base_name}_HE.srt"
#     print(f">> קובץ הכתוביות העתידי ישמר בשם: {output_file}")

# else:
#     print("לא נבחר קובץ. התוכנית מסתיימת.")

# input("\nלחץ Enter כדי לסיים...")


# import tkinter as tk
# from tkinter import filedialog
# import os

# # יצירת חלון מוסתר (כדי שלא יקפוץ חלון ריק ומכוער של התוכנה, אלא רק חלון בחירת הקובץ)
# root = tk.Tk()
# root.withdraw()

# print("פותח חלון בחירת קובץ...")

# # הקפצת חלון בחירת קובץ
# file_path = filedialog.askopenfilename(
#     title="בחר קובץ וידאו עם כתוביות מובנות",
#     filetypes=[("Video files", "*.mkv *.mp4 *.avi"), ("All files", "*.*")],
# )

# # בדיקה אם המשתמש באמת בחר קובץ או שלחץ על "ביטול"
# if file_path:
#     print(f"הקובץ שנבחר: {file_path}")

#     # כאן בעתיד נוסיף את הקוד לחילוץ (Extract) והתרגום!

#     # יצירת הנתיב לקובץ הכתוביות החדש שיווצר באותה תיקייה
#     base_name = os.path.splitext(file_path)[0]
#     output_file = f"{base_name}_HE.srt"

#     print(f"קובץ הכתוביות העתידי ישמר בשם: {output_file}")

# else:
#     print("לא נבחר קובץ. התוכנית מסתיימת.")

# # עוצר את המסך כדי שתוכל לראות את התוצאות לפני שהחלון נסגר
# input("\nלחץ Enter כדי לסיים...")
