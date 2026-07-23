from fastapi import FastAPI
from pydantic import BaseModel
import argparse
import sys

from config import check_keys
from providers import call_provider
from audio_io import listen, speak

# -----------------------------
# FastAPI App (for Render)
# -----------------------------

app = FastAPI(title="Jarvis AI")

SYSTEM_PROMPT = (
    "You are a helpful, concise voice assistant. "
    "Keep replies conversational and brief."
)

EXIT_WORDS = {"exit", "quit", "stop", "goodbye", "bye"}


class ChatRequest(BaseModel):
    message: str
    provider: str = "openai"


@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Jarvis AI is running successfully!"
    }


@app.post("/chat")
def chat(req: ChatRequest):
    check_keys([req.provider])

reply = call_provider(
    req.provider,
    req.message,
    history=[],
    system_prompt=SYSTEM_PROMPT,
)

    return {
        "provider": req.provider,
        "reply": reply
    }


# -----------------------------
# Voice Assistant
# -----------------------------

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--provider",
        default="openai",
        choices=[
            "openai",
            "chatgpt",
            "claude",
            "anthropic",
            "gemini",
            "google",
        ],
    )

    parser.add_argument(
        "--text",
        action="store_true",
        help="Use keyboard instead of microphone",
    )

    parser.add_argument(
        "--no-voice-out",
        action="store_true",
        help="Disable speaking replies",
    )

    return parser.parse_args()


def maybe_switch_provider(user_text, current_provider):
    lowered = user_text.lower().strip()

    if lowered.startswith("switch to "):
        candidate = lowered.replace("switch to ", "").strip()

        if candidate in {
            "openai",
            "chatgpt",
            "claude",
            "anthropic",
            "gemini",
            "google",
        }:
            return candidate, True

    return current_provider, False


def voice_assistant():
    args = parse_args()

    provider = args.provider.lower()

    check_keys([provider])

    history = []

    print(f"Talking to {provider}")

    while True:

        if args.text:
            try:
                user_text = input("You: ").strip()
            except (KeyboardInterrupt, EOFError):
                break

        else:
            try:
                user_text = listen()
            except Exception as e:
                print(e)
                continue

            print("You:", user_text)

        if not user_text:
            continue

        if user_text.lower() in EXIT_WORDS:
            print("Goodbye!")
            break

        provider, switched = maybe_switch_provider(
            user_text,
            provider,
        )

        if switched:
            print(f"Switched to {provider}")

            if not args.no_voice_out:
                speak(f"Switched to {provider}")

            continue

        try:
            reply = call_provider(
                provider,
                user_text,
                history,
                SYSTEM_PROMPT,
            )

        except Exception as e:
            reply = str(e)

        print(reply)

        history.append(
            {
                "role": "user",
                "content": user_text,
            }
        )

        history.append(
            {
                "role": "assistant",
                "content": reply,
            }
        )

        if not args.no_voice_out:
            speak(reply)


if __name__ == "__main__":
    try:
        voice_assistant()
    except KeyboardInterrupt:
        print("\nBye!")
        sys.exit(0)
