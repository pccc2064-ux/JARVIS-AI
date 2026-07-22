"""
providers.py
------------
Thin wrapper functions around each AI provider's chat API.

Each function takes:
    prompt        : the user's text (already transcribed from audio)
    history       : optional list of {"role": "user"/"assistant", "content": str}
    system_prompt : optional system/persona instruction

...and returns a plain string reply.

Install only the SDKs for the providers you plan to use:
    pip install openai anthropic google-genai
"""

from config import (
    OPENAI_API_KEY, OPENAI_MODEL,
    ANTHROPIC_API_KEY, ANTHROPIC_MODEL,
    GOOGLE_API_KEY, GEMINI_MODEL,
)


# ---------------------------------------------------------------------------
# OpenAI / ChatGPT
# ---------------------------------------------------------------------------
def call_openai(prompt, history=None, system_prompt="You are a helpful voice assistant."):
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
    )
    return response.choices[0].message.content


# ---------------------------------------------------------------------------
# Anthropic / Claude
# ---------------------------------------------------------------------------
def call_claude(prompt, history=None, system_prompt="You are a helpful voice assistant."):
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    messages = []
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": prompt})

    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
    )
    # response.content is a list of content blocks
    return "".join(block.text for block in response.content if block.type == "text")


# ---------------------------------------------------------------------------
# Google Gemini
# ---------------------------------------------------------------------------
def call_gemini(prompt, history=None, system_prompt="You are a helpful voice assistant."):
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=GOOGLE_API_KEY)

    # Gemini uses "user"/"model" roles for history.
    chat_history = []
    if history:
        for turn in history:
            role = "model" if turn["role"] == "assistant" else "user"
            chat_history.append(types.Content(role=role, parts=[types.Part.from_text(text=turn["content"])]))

    chat = client.chats.create(
        model=GEMINI_MODEL,
        config=types.GenerateContentConfig(system_instruction=system_prompt),
        history=chat_history,
    )
    response = chat.send_message(prompt)
    return response.text


# ---------------------------------------------------------------------------
# Registry so main.py can look providers up by name
# ---------------------------------------------------------------------------
PROVIDERS = {
    "openai": call_openai,
    "chatgpt": call_openai,      # alias
    "claude": call_claude,
    "anthropic": call_claude,    # alias
    "gemini": call_gemini,
    "google": call_gemini,       # alias
}


def call_provider(name, prompt, history=None, system_prompt=None):
    """Dispatch to the right provider by name. Raises KeyError if unknown."""
    fn = PROVIDERS[name.lower()]
    kwargs = {}
    if system_prompt:
        kwargs["system_prompt"] = system_prompt
    return fn(prompt, history=history, **kwargs)