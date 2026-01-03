from __future__ import annotations

from dataclasses import dataclass

# Removed langchain import to avoid model initialization errors

from app.core.config import settings


@dataclass
class GeminiResult:
    category: str
    confidence: float
    source: str
    explanation: str


async def gemini_classify(description: str) -> GeminiResult | None:
    # Temporarily disable Gemini due to model availability issues
    return None
