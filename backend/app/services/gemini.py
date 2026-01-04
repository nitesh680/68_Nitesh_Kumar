from __future__ import annotations

from dataclasses import dataclass
import json

from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings


@dataclass
class GeminiResult:
    category: str
    confidence: float
    source: str
    explanation: str


async def gemini_classify(description: str) -> GeminiResult | None:
    if not settings.GEMINI_API_KEY:
        return None
    
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=settings.GEMINI_API_KEY)
        prompt = (
            "You are a personal finance categorization expert. "
            "Categorize this transaction description into one of these categories: "
            "Business lunch, Clothing, Coffee, Communal, Events, Entertainment, Fuel, "
            "Groceries, Health, Home, Insurance, Market, Other, Personal, Restaurant, "
            "Shopping, Subscriptions, Taxes, Transport, Travel, Utilities, Work. "
            "Respond with JSON: {\"category\": \"<category>\", \"confidence\": <0.0-1.0>, "
            "\"explanation\": \"<brief explanation>\"}\n\n"
            f"Transaction: {description}"
        )
        resp = llm.invoke(prompt)
        
        # Parse response to extract category, confidence, explanation
        content = resp.content.strip()
        if content.startswith('{') and content.endswith('}'):
            import json
            try:
                data = json.loads(content)
                return GeminiResult(
                    category=data.get("category", "Other"),
                    confidence=float(data.get("confidence", 0.5)),
                    source="gemini",
                    explanation=data.get("explanation", "AI categorization")
                )
            except json.JSONDecodeError:
                pass
        
        # Fallback if JSON parsing fails
        return GeminiResult(
            category="Other",
            confidence=0.3,
            source="gemini",
            explanation="AI categorization"
        )
        
    except Exception as e:
        # Log error but don't crash
        print(f"Gemini API error: {e}")
        return None
