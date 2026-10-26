import time
from urllib.parse import urlparse

import httpx
from pydantic import TypeAdapter

from agent.config import PROMPT_VERSION, Settings
from agent.models import FinalAction, ToolAction


class ModelError(RuntimeError):
    pass


class UITModel:
    def __init__(self, settings: Settings):
        self.settings = settings
        parsed = urlparse(settings.base_url)
        if parsed.scheme != "https" or parsed.hostname != "llm.uit.edu.vn":
            raise ValueError("Phase 1 chỉ cho phép HTTPS tới llm.uit.edu.vn.")

    def complete(self, messages: list[dict], trace) -> str:
        settings = self.settings
        trace.emit("model_started", model=settings.model, prompt_version=PROMPT_VERSION)
        started = time.perf_counter()
        try:
            with httpx.Client(
                proxy=settings.proxy, timeout=settings.timeout,
                follow_redirects=False, trust_env=False,
            ) as client:
                response = client.post(
                    settings.base_url + "/chat/completions",
                    headers={"Authorization": f"Bearer {settings.api_key}"},
                    json={
                        "model": settings.model, "messages": messages,
                        "temperature": 0, "max_tokens": settings.max_tokens,
                        "tool_choice": "none", "stream": False,
                        "response_format": {
                            "type": "json_schema",
                            "json_schema": {
                                "name": "agent_action",
                                "schema": TypeAdapter(ToolAction | FinalAction).json_schema(),
                            },
                        },
                    },
                )
                if response.status_code != 200:
                    raise ModelError(
                        f"UIT API trả HTTP {response.status_code}. "
                        "Kiểm tra SSH tunnel, key và cấu hình model."
                    )
                data = response.json()
            choice = data["choices"][0]
            if choice.get("finish_reason") == "length":
                raise ModelError("Model hết giới hạn token; thử tăng MODEL_MAX_TOKENS.")
            content = choice["message"].get("content")
            if not isinstance(content, str) or not content.strip():
                raise ModelError("UIT API trả nội dung trống.")
            usage = data.get("usage") or {}
            cost = None
            if settings.input_price is not None and settings.output_price is not None:
                if "prompt_tokens" in usage and "completion_tokens" in usage:
                    cost = (
                        usage["prompt_tokens"] * settings.input_price
                        + usage["completion_tokens"] * settings.output_price
                    ) / 1_000_000
            trace.emit(
                "model_completed", model=settings.model,
                duration_ms=round((time.perf_counter() - started) * 1000),
                prompt_tokens=usage.get("prompt_tokens"),
                completion_tokens=usage.get("completion_tokens"),
                cost_usd=cost,
            )
            return content
        except (httpx.HTTPError, KeyError, IndexError, ValueError, ModelError) as exc:
            trace.emit("model_error", error_type=type(exc).__name__)
            if isinstance(exc, ModelError):
                raise
            raise ModelError(
                "Không gọi được UIT API. Kiểm tra kết nối/tunnel rồi bấm thử lại; bài đã lưu."
            ) from None
