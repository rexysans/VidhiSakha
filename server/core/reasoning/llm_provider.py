"""
Ollama-only LLM provider for VidhiSakhā.
"""

import os
import time
import threading
from dotenv import load_dotenv

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(dotenv_path=os.path.join(_PROJECT_ROOT, ".env"), override=True)


_CB_CONSECUTIVE_FAILURES = 0
_CB_OPEN_UNTIL_TS = 0.0
_LLM_LOCK = threading.Lock()


def _to_float(value: str, default: float) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _to_int(value: str, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _call_ollama(prompt: str) -> str:
    import ollama

    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    timeout_s = _to_float(os.getenv("LLM_TIMEOUT_SECONDS", "120"), 120.0)

    client = ollama.Client(host=host)
    max_prompt_chars = _to_int(os.getenv("LLM_MAX_PROMPT_CHARS", "12000"), 12000)
    prompt = (prompt or "")[:max_prompt_chars]

    response = client.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        options={
            "temperature": 0.1,
            "num_ctx": _to_int(os.getenv("LLM_NUM_CTX", "2048"), 2048),
            "num_predict": _to_int(os.getenv("LLM_NUM_PREDICT", "384"), 384),
        },
        keep_alive="5m",
    )

    msg = ""
    if isinstance(response, dict):
        msg = (response.get("message") or {}).get("content", "")
    else:
        message_obj = getattr(response, "message", None)
        msg = getattr(message_obj, "content", "") if message_obj else ""

    if not msg or not str(msg).strip():
        raise RuntimeError("ollama returned empty content")

    elapsed = time.time() - _call_ollama._started_at
    if elapsed > timeout_s:
        raise TimeoutError(f"ollama call exceeded timeout ({elapsed:.2f}s > {timeout_s:.2f}s)")

    return str(msg).strip()


def llm_generate(prompt: str, max_retries: int = 1) -> str:
    global _CB_CONSECUTIVE_FAILURES, _CB_OPEN_UNTIL_TS

    mode = os.getenv("LLM_PROVIDER_MODE", "ollama_only").strip().lower()
    if mode != "ollama_only":
        print(f"[LLM] provider_mode={mode!r} not supported in this runtime; forcing ollama_only")

    retries = _to_int(os.getenv("LLM_MAX_RETRIES", str(max_retries)), max_retries)
    retries = max(1, retries)

    cb_failure_threshold = _to_int(os.getenv("LLM_CB_FAILURE_THRESHOLD", "3"), 3)
    cb_cooldown_minutes = _to_float(os.getenv("LLM_CB_COOLDOWN_MINUTES", "5"), 5.0)

    now = time.time()
    if now < _CB_OPEN_UNTIL_TS:
        remaining = int(_CB_OPEN_UNTIL_TS - now)
        print(f"[LLM] circuit=open provider=ollama skip=true remaining_s={remaining}")
        return ""

    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")

    with _LLM_LOCK:
        for attempt in range(1, retries + 1):
            _call_ollama._started_at = time.time()
            try:
                start = time.time()
                out = _call_ollama(prompt)
                elapsed_ms = int((time.time() - start) * 1000)
                print(f"[LLM] provider=ollama model={model} host={host} attempt={attempt}/{retries} latency_ms={elapsed_ms}")
                _CB_CONSECUTIVE_FAILURES = 0
                _CB_OPEN_UNTIL_TS = 0.0
                return out
            except Exception as e:
                _CB_CONSECUTIVE_FAILURES += 1
                print(f"[LLM] provider=ollama model={model} attempt={attempt}/{retries} error={e}")

    if _CB_CONSECUTIVE_FAILURES >= cb_failure_threshold:
        _CB_OPEN_UNTIL_TS = time.time() + (cb_cooldown_minutes * 60.0)
        print(
            f"[LLM] circuit=opened provider=ollama failures={_CB_CONSECUTIVE_FAILURES} "
            f"cooldown_min={cb_cooldown_minutes:.2f}"
        )

    print("[LLM] fallback=empty_response reason=ollama_unavailable")
    return ""
