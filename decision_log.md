# DECISION LOG & FUTURE ROADMAP

## Architecture Decisions (Archived)
* **Subtitle Edit CLI:** We initially tried routing translation through Subtitle Edit CLI. 
  * *Result:* Failed. SE explicitly blocks `/googletranslate` in CLI mode to prevent API abuse.
  * *Decision:* Abandoned SE in favor of native Python multithreading.

## Future Roadmap (Backlog)
1. **Audio to Text (No Subs Scenario):** If a video lacks embedded subtitles, extract audio via FFmpeg -> use local AI (e.g., `faster-whisper`) to generate English `.srt` -> run through our translation logic. (Will use 'Initial Prompt' for anime character names).
2. **Translation Engine:** Consider migrating from Google Translate to DeepL API or ChatGPT API for natural language.
3. **Vocal Isolation (UVR5):** Add a pre-processing step to isolate vocals from background noise/music before sending to Whisper.
4. **Automation:** Implement a "Watch Folder" script for zero-click automation.
5. **DevOps:** Containerize the final environment using Docker.