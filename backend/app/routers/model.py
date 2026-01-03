import os

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.deps import get_current_user
from app.ml.trainer import train_from_csv
from app.schemas.model import PredictRequest, PredictResponse, TrainRequest, TrainResponse
from app.services.categorizer import categorize

router = APIRouter()


@router.post("/train", response_model=TrainResponse)
async def train(payload: TrainRequest, user=Depends(get_current_user)):
    if not os.path.exists(payload.dataset_path):
        raise HTTPException(status_code=400, detail=f"Dataset not found: {payload.dataset_path}")

    result = train_from_csv(
        dataset_path=payload.dataset_path,
        text_column=payload.text_column,
        label_column=payload.label_column,
    )

    return TrainResponse(trained=True, metrics={"metrics": result.metrics, "confusion_matrix": result.confusion_matrix, "labels": result.labels})


@router.post("/train-upload", response_model=TrainResponse)
async def train_upload(file: UploadFile = File(...), user=Depends(get_current_user)):
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="wb") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    try:
        result = train_from_csv(
            dataset_path=tmp_path,
            text_column="description",
            label_column="category",
        )
        return TrainResponse(trained=True, metrics={"metrics": result.metrics, "confusion_matrix": result.confusion_matrix, "labels": result.labels})
    finally:
        os.unlink(tmp_path)


@router.post("/predict", response_model=PredictResponse)
async def predict(payload: PredictRequest, user=Depends(get_current_user)):
    res = await categorize(payload.description)
    return PredictResponse(category=res.category, confidence=res.confidence, source=res.source, explanation=res.explanation)
