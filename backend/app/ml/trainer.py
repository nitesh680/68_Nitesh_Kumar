import os
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from app.ml.model_store import save_artifacts


@dataclass
class TrainResult:
    metrics: dict
    confusion_matrix: list[list[int]]
    labels: list[str]


def train_from_csv(
    dataset_path: str,
    text_column: str,
    label_column: str,
) -> TrainResult:
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(dataset_path)

    df = pd.read_csv(dataset_path)

    if text_column not in df.columns:
        raise ValueError(f"Missing text column: {text_column}. Columns: {list(df.columns)}")
    if label_column not in df.columns:
        raise ValueError(f"Missing label column: {label_column}. Columns: {list(df.columns)}")

    X = df[text_column].fillna("").astype(str).values
    y = df[label_column].fillna("").astype(str).values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y if len(set(y)) > 1 and all(y.tolist().count(c) > 1 for c in set(y)) else None
    )

    pipeline: Pipeline = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=50000)),
            ("clf", LogisticRegression(max_iter=2000, n_jobs=None)),
        ]
    )

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)

    labels = sorted(list(set(y)))
    cm = confusion_matrix(y_test, y_pred, labels=labels)

    report = classification_report(y_test, y_pred, labels=labels, output_dict=True, zero_division=0)
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "report": report,
    }

    save_artifacts(pipeline=pipeline, labels=labels)

    return TrainResult(metrics=metrics, confusion_matrix=cm.tolist(), labels=labels)
