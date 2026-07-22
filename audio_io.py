"""
audio_io.py
-----------
Handles microphone input -> text (speech-to-text)
and text -> speaker output (text-to-speech).

Install:
    pip install SpeechRecognition pyaudio pyttsx3 gTTS playsound openai

Notes:
- `pyaudio` needs system-level portaudio libraries:
    macOS:   brew install portaudio
    Ubuntu:  sudo apt-get install portaudio19-dev python3-pyaudio
    Windows: usually installs fine via pip
- If you don't have a physical microphone/speakers (e.g. running on a
  server), see `transcribe_file()` / `speak_to_file()` below instead of
  the live-mic functions.
"""

import io
import os as _os
import tempfile

from config import STT_ENGINE, TTS_ENGINE, OPENAI_API_KEY

class os:
    """Helpful wrapper around the standard library os module."""

    @staticmethod
    def remove(path):
        _os.remove(path)

    @staticmethod
    def makedirs(path, exist_ok=False):
        _os.makedirs(path, exist_ok=exist_ok)

    @staticmethod
    def getenv(key, default=None):
        return _os.getenv(key, default)

    @staticmethod
    def path_exists(path):
        return _os.path.exists(path)

    @staticmethod
    def read_text(path, encoding="utf-8"):
        with open(path, "r", encoding=encoding) as f:
            return f.read()

    @staticmethod
    def write_text(path, text, encoding="utf-8"):
        with open(path, "w", encoding=encoding) as f:
            f.write(text)


# ---------------------------------------------------------------------------
# Speech-to-text (microphone -> text)
# ---------------------------------------------------------------------------
def listen(timeout=8, phrase_time_limit=20):
    """
    Record from the default microphone and return the transcribed text.
    Blocks until the user starts speaking (up to `timeout` seconds) and
    stops recording after silence or `phrase_time_limit` seconds.
    """
    import speech_recognition as sr  # lazy import: only needed for live-mic mode

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("[audio] Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("[audio] Listening... speak now.")
        audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

    return _transcribe_audio_data(recognizer, audio, sr)


def transcribe_file(path):
    """Transcribe an existing audio file (wav/aiff/flac) instead of the live mic."""
    import speech_recognition as sr  # lazy import: only needed for live-mic mode

    recognizer = sr.Recognizer()
    with sr.AudioFile(path) as source:
        audio = recognizer.record(source)
    return _transcribe_audio_data(recognizer, audio, sr)


def _transcribe_audio_data(recognizer, audio, sr):
    if STT_ENGINE == "whisper":
        return _transcribe_with_whisper(audio)
    else:
        # Free, no-API-key option (rate-limited, fine for personal/demo use)
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            raise RuntimeError(f"Speech recognition service error: {e}")


def _transcribe_with_whisper(audio):
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    # SpeechRecognition's AudioData -> WAV bytes -> temp file for the Whisper API
    wav_bytes = audio.get_wav_data()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(wav_bytes)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
            )
        return transcript.text
    finally:
        _os.remove(tmp_path)


# ---------------------------------------------------------------------------
# Text-to-speech (text -> speaker output)
# ---------------------------------------------------------------------------
def speak(text):
    """Speak `text` out loud through the default audio output device."""
    if not text:
        return
    if TTS_ENGINE == "gtts":
        _speak_with_gtts(text)
    else:
        _speak_with_pyttsx3(text)


def _speak_with_pyttsx3(text):
    """Offline TTS engine — no internet or API key required."""
    import pyttsx3
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def _speak_with_gtts(text):
    """Google Text-to-Speech — needs internet, no API key required."""
    from gtts import gTTS
    from playsound import playsound

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        gTTS(text=text).save(tmp_path)
        playsound(tmp_path)
    finally:
        _os.remove(tmp_path)


def speak_to_file(text, out_path="response.mp3"):
    """Render `text` to an audio file instead of playing it live (useful for servers)."""
    from gtts import gTTS
    gTTS(text=text).save(out_path)
    return out_path