# Multi-Provider Voice AI Assistant

Talk to it, and it talks back — with your choice of backend:
**OpenAI (ChatGPT)**, **Anthropic (Claude)**, or **Google (Gemini)**.

## How it works

```
microphone --> speech-to-text --> [ OpenAI | Claude | Gemini ] --> text-to-speech --> speaker
```

| File | Purpose |
|---|---|
| `config.py` | Loads API keys / model names from environment variables |
| `providers.py` | Wrapper functions that call each AI provider's chat API |
| `audio_io.py` | Microphone capture → text (STT), and text → speech (TTS) |
| `main.py` | Ties it together into a voice conversation loop |

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   `pyaudio` needs a system library first:
   - macOS: `brew install portaudio`
   - Ubuntu/Debian: `sudo apt-get install portaudio19-dev python3-pyaudio`
   - Windows: usually just works via pip

2. **Set your API keys**
   Copy `.env.example` to `.env` and fill in keys for whichever provider(s)
   you want to use — you don't need all three, just the one(s) you'll call.
   ```bash
   cp .env.example .env
   ```
   Or export them directly:
   ```bash
   export OPENAI_API_KEY=sk-...
   export ANTHROPIC_API_KEY=sk-ant-...
   export GOOGLE_API_KEY=AIza...
   ```

3. **Run it**
   ```bash
   python main.py --provider claude
   ```
   Say something, wait for the transcript to print, and the reply will be
   spoken back to you.

## Useful flags

```bash
python main.py --provider gemini          # start with Gemini
python main.py --text                     # type instead of speaking (no mic needed)
python main.py --no-voice-out             # print replies instead of speaking them
```

While it's running, you can also say (or type):
- `"switch to claude"` / `"switch to openai"` / `"switch to gemini"` — change backend mid-conversation
- `"exit"` / `"quit"` / `"stop"` — end the session

## Swapping in other AI tools

`providers.py` has a `PROVIDERS` dict at the bottom — add a new function with
the same signature (`prompt, history=None, system_prompt=...`) and register
it there to plug in another model (e.g. a local Llama server, Mistral API,
Cohere, etc.).

## Notes & limitations

- The default speech-to-text (`STT_ENGINE=google` in `config.py`) uses
  SpeechRecognition's free hosted Google Web Speech API — no key needed,
  but it's rate-limited and not meant for heavy production use. Switch to
  `STT_ENGINE=whisper` for OpenAI's Whisper API (needs `OPENAI_API_KEY`
  and costs per minute of audio).
- Default text-to-speech (`TTS_ENGINE=pyttsx3`) runs fully offline. Switch
  to `TTS_ENGINE=gtts` for Google's (online) TTS voices.
- No audio hardware (e.g. running on a headless server)? Use
  `audio_io.transcribe_file()` and `audio_io.speak_to_file()` instead of
  the live-mic functions, or run with `--text --no-voice-out`.
- Keep API keys out of source control — `.env` should be in your
  `.gitignore`.
