from __future__ import annotations
from typing import List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
from backend.app.core.config import get_settings

_settings = get_settings()


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def generate_response(prompt: str, system: str | None = None) -> str:
    provider = _settings.llm_provider
    if provider == "ollama":
        return _generate_ollama(prompt, system)
    return _generate_openai(prompt, system)


def _generate_openai(prompt: str, system: str | None) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=_settings.openai_api_key)
    model = _settings.openai_model
    messages: List[Dict[str, Any]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    resp = client.chat.completions.create(model=model, messages=messages, temperature=0.2)
    return resp.choices[0].message.content or ""


def _generate_ollama(prompt: str, system: str | None) -> str:
    import ollama

    full_prompt = f"<|system|>\n{system or ''}\n<|user|>\n{prompt}\n<|assistant|>"
    response = ollama.generate(model=_settings.ollama_model, prompt=full_prompt, options={"temperature": 0.2})
    return response.get("response", "")