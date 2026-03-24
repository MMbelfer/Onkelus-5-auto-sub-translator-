# PROJECT CONTEXT: Automated Subtitle Extractor & Translator

## Current Architecture
A Python script using `tkinter` for GUI, `subprocess` with `ffmpeg`/`ffprobe` for media processing, and native multithreading for translation.

## Current State (MVP v1.0)
* **UI:** Native `tkinter` (filedialog, OptionMenu).
* **Extraction:** Uses `ffmpeg` to extract the selected embedded subtitle track locally.
* **Translation:** Uses Python's `deep-translator` (Google Translate) with `ThreadPoolExecutor` (max_workers=20) for blazing-fast parallel translation.
* **Execution:** Generates a temporary `.srt`, translates it ignoring timestamps (`-->`), saves as `[OriginalFileName]_HEBREW.srt`, and cleans up temp files.

**Note to AI:** For historical decisions (like why we dropped Subtitle Edit) or future roadmap (Whisper, UVR5), please refer to `decision_log.md`.