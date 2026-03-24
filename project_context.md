# PROJECT CONTEXT: Automated Subtitle Extractor & Translator

## Current Architecture
A Python script using `tkinter` for GUI, `subprocess` with `ffmpeg`/`ffprobe` for media processing, and native multithreading for translation.

## Current State (MVP v1.0)
* **UI:** Native `tkinter` (filedialog, OptionMenu).
* **Extraction:** Uses `ffmpeg` to extract the selected embedded subtitle track locally.
* **Translation:** Uses Python's `deep-translator` (Google Translate) with `ThreadPoolExecutor` (max_workers=20) for blazing-fast parallel translation.
* **Execution:** Generates a temporary `.srt`, translates it ignoring timestamps (`-->`), saves as `[OriginalFileName]_HEBREW.srt`, and cleans up temp files.

**Note to AI:** For historical decisions (like why we dropped Subtitle Edit) or future roadmap (Whisper, UVR5), please refer to `decision_log.md`.

## AI Working Protocol (Strict Rules for Future Sessions)
* **Clean Code Only:** NEVER leave commented-out historical code in the Python scripts. We rely on Git for version control. Keep files lean and executable.
* **Separation of Context:** Update THIS file (`project_context.md`) ONLY with the current, working architecture. 
* **The Graveyard & Future:** Move all failed attempts, abandoned tools (e.g., Subtitle Edit CLI), and future roadmap items to `decision_log.md`. Do not clutter the active context.
* **End of Session:** When requested to "summarize for update", generate the concise technical changes so the user can easily paste them into these two files accordingly.