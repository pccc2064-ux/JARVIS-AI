"""
main.py
-------
Text-in / text-out assistant that can talk to ChatGPT (OpenAI), Claude
(Anthropic), or Gemini (Google) — you choose the provider per session,
or switch on the fly by saying "switch to <provider>".

This version has NO microphone or speaker dependency — it works purely
through typed input and printed output, so it runs anywhere (including
cloud servers with no audio hardware).

Usage:
    python main.py                  # interactive text loop, default provider = openai
    python main.py --provider claude
    python main.py --provider gemini

Environment variables needed (set the ones for the provider(s) you use):
    OPENAI_API_KEY
    ANTHROPIC_API_KEY
    GOOGLE_API_KEY
"""

import argparse
import sys

from config import check_keys
from providers import call_provider

SYSTEM_PROMPT = "You are a helpful, concise assistant. Keep replies conversational and brief."

EXIT_WORDS = {"exit", "quit", "stop", "goodbye", "bye"}


def parse_args():
    parser = argparse.ArgumentParser(description="Multi-provider text AI assistant")
    parser.add_argument(
        "--provider",
        default="openai",
        choices=["openai", "chatgpt", "claude", "anthropic", "gemini", "google"],
        help="Which AI backend to talk to (default: openai)",
    )
    return parser.parse_args()


def maybe_switch_provider(user_text, current_provider):
    """Lets the user say things like 'switch to claude' mid-conversation."""
    lowered = user_text.lower().strip()
    if lowered.startswith("switch to "):
        candidate = lowered.replace("switch to ", "").strip()
        if candidate in {"openai", "chatgpt", "claude", "anthropic", "gemini", "google"}:
            return candidate, True
    return current_provider, False


def main():
    args = parse_args()
    provider = args.provider.lower()
    check_keys([provider])

    history = []  # list of {"role": "user"/"assistant", "content": str}

    print(f"[assistant] Ready. Talking to '{provider}'. Type 'exit' to quit.")
    print("[assistant] Type 'switch to <openai|claude|gemini>' to change providers.")

    while True:
        # 1. Get typed input
        try:
            user_text = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_text:
            print("[assistant] (empty input, try again)")
            continue

        if user_text.lower().strip() in EXIT_WORDS:
            print("[assistant] Goodbye!")
            break

        # 2. Allow switching providers mid-conversation
        provider, switched = maybe_switch_provider(user_text, provider)
        if switched:
            print(f"[assistant] Switched to {provider}.")
            continue

        # 3. Call the chosen AI provider
        try:
            reply = call_provider(provider, user_text, history=history, system_prompt=SYSTEM_PROMPT)
        except KeyError:
            print(f"[assistant] Unknown provider '{provider}'.")
            continue
        except Exception as e:
            reply = f"Sorry, I hit an error talking to {provider}: {e}"

        print(f"{provider.capitalize()}: {reply}")

        # 4. Update history
        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[assistant] Interrupted. Bye!")
        sys.exit(0)
