import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
PROMPT_VERSION = "speaking-v2.1"
DISCLAIMER = "Điểm ước lượng do AI chấm, chỉ dùng để luyện tập, không thay thế điểm thi chính thức."
TEXT_LIMITATION = (
    "Đánh giá từ text chỉ phản ánh diễn đạt, từ vựng và ngữ pháp. "
    "Không quan sát được tốc độ nói, ngập ngừng thực tế hoặc phát âm."
)


@dataclass(frozen=True)
class Settings:
    api_key: str = field(repr=False)
    base_url: str = "https://llm.uit.edu.vn/gemma/v1"
    model: str = "gemma-4-26b"
    proxy: str | None = None
    timeout: float = 90
    max_tokens: int = 3000
    input_price: float | None = None
    output_price: float | None = None

    @classmethod
    def load(cls):
        load_dotenv(ROOT / ".env")
        key = os.getenv("OPENAI_API_KEY", "")
        if not key:
            raise ValueError("Thiếu OPENAI_API_KEY trong .env của dự án.")
        return cls(
            api_key=key,
            base_url=os.getenv("OPENAI_BASE_URL", cls.base_url).rstrip("/"),
            model=os.getenv("MODEL_NAME", cls.model),
            proxy=os.getenv("UIT_PROXY") or None,
            timeout=float(os.getenv("MODEL_TIMEOUT_SECONDS", "90")),
            max_tokens=int(os.getenv("MODEL_MAX_TOKENS", "3000")),
            input_price=float(os.environ["INPUT_USD_PER_MILLION"])
            if os.getenv("INPUT_USD_PER_MILLION") else None,
            output_price=float(os.environ["OUTPUT_USD_PER_MILLION"])
            if os.getenv("OUTPUT_USD_PER_MILLION") else None,
        )
