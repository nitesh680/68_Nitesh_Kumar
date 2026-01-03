from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from app.core.config import settings
from app.ml.model_store import load_artifacts
from app.ml.rules import apply_rules
from app.services.gemini import gemini_classify


@dataclass
class CategorizeResult:
    category: str
    confidence: float
    source: str
    explanation: str


def _ml_predict(description: str) -> tuple[str, float, str] | None:
    artifacts = load_artifacts()
    if artifacts is None:
        return None

    proba = None
    if hasattr(artifacts.pipeline, "predict_proba"):
        proba = artifacts.pipeline.predict_proba([description])

    pred = artifacts.pipeline.predict([description])[0]

    if proba is None:
        return (str(pred), 0.5, "ml")

    proba = np.asarray(proba)[0]
    idx = int(np.argmax(proba))
    confidence = float(proba[idx])
    return (str(pred), confidence, "ml")


async def categorize(description: str) -> CategorizeResult:
    rule = apply_rules(description)
    if rule is not None:
        cat, conf, source, expl = rule
        return CategorizeResult(category=cat, confidence=conf, source=source, explanation=expl)

    ml = _ml_predict(description)
    if ml is not None:
        cat, conf, source = ml
        return CategorizeResult(
            category=cat,
            confidence=conf,
            source=source,
            explanation=f"ML prediction with confidence {conf:.2f}",
        )

    gem = await gemini_classify(description)
    if gem is not None:
        return gem

    return CategorizeResult(
        category="Other",
        confidence=0.25,
        source="default",
        explanation="No rule match; ML unavailable/low confidence; Gemini unavailable",
    )
