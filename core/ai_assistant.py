"""Call an OpenAI-compatible chat API for one-shot text processing.

Supports any provider exposing the /chat/completions endpoint, e.g.
DeepSeek, Volcengine Ark (Doubao), OpenAI, Moonshot, etc.
Uses only the standard library so the packaged EXE needs no extra deps.
"""
import json
import urllib.error
import urllib.request


AI_PROMPTS = {
    "总结": "你是一个高效的文本总结助手。请用简洁的中文概括以下文本的核心内容，"
    "保留关键信息，不要输出额外解释。",
    "翻译": "请将以下文本翻译成流畅自然的中文。如果原文已经是中文，则翻译成英文。"
    "只输出译文，不要解释。",
    "润色": "请润色以下文本，修正语法错误并使表达更通顺专业。只输出润色后的文本，不要解释。",
}

DEFAULT_ACTION = "总结"


def build_payload(model: str, action: str, text: str) -> dict:
    """Build the JSON request body for a one-shot completion."""
    system = AI_PROMPTS.get(action, AI_PROMPTS[DEFAULT_ACTION])
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": text},
        ],
        "stream": False,
    }


def call_ai(base_url: str, api_key: str, model: str, action: str, text: str,
            timeout: int = 30) -> str:
    """Call the chat API and return the assistant reply text.

    Raises ValueError on missing configuration or network/API errors.
    """
    if not api_key.strip():
        raise ValueError("尚未配置 API Key，请在“设置”中填写。")
    if not base_url.strip() or not model.strip():
        raise ValueError("尚未配置接口地址或模型名，请在“设置”中填写。")

    url = base_url.rstrip("/") + "/chat/completions"
    body = json.dumps(build_payload(model, action, text)).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    request.add_header("Authorization", f"Bearer {api_key}")
    request.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:300]
        raise ValueError(f"接口返回错误（HTTP {error.code}）：{detail}") from error
    except urllib.error.URLError as error:
        raise ValueError(f"网络请求失败：{error.reason}") from error
    except (json.JSONDecodeError, KeyError, IndexError) as error:
        raise ValueError("接口返回格式无法解析。") from error

    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as error:
        raise ValueError("接口返回中没有可用内容。") from error
