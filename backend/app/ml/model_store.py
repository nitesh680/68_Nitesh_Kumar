import os
from dataclasses import dataclass

import joblib

from app.core.config import settings


@dataclass
class ModelArtifacts:
    pipeline: object
    labels: list[str]


def artifacts_path() -> str:
    # Try custom model first, then fallback to default
    custom_path = os.path.join(settings.MODEL_DIR, "expense_model.joblib")
    default_path = os.path.join(settings.MODEL_DIR, "model.joblib")
    return custom_path if os.path.exists(custom_path) else default_path


def load_artifacts() -> ModelArtifacts | None:
    path = artifacts_path()
    if not os.path.exists(path):
        return None
    data = joblib.load(path)
    # Handle both formats: dict with pipeline/labels or direct pipeline
    if isinstance(data, dict) and "pipeline" in data and "labels" in data:
        return ModelArtifacts(pipeline=data["pipeline"], labels=data["labels"])
    elif hasattr(data, 'predict'):  # Direct pipeline object
        # Try to infer labels from the model
        if hasattr(data, 'classes_'):
            labels = list(data.classes_)
        else:
            labels = []  # Will be populated during first use
        return ModelArtifacts(pipeline=data, labels=labels)
    else:
        return None


def save_artifacts(pipeline: object, labels: list[str]) -> None:
    os.makedirs(settings.MODEL_DIR, exist_ok=True)
    joblib.dump({"pipeline": pipeline, "labels": labels}, artifacts_path())
