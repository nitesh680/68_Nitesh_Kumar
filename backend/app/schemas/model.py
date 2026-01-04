from pydantic import BaseModel


class TrainRequest(BaseModel):
    dataset_path: str = ""  # Will be provided via upload, not hardcoded
    text_column: str = "description"
    label_column: str = "category"


class TrainResponse(BaseModel):
    trained: bool
    metrics: dict


class PredictRequest(BaseModel):
    description: str


class PredictResponse(BaseModel):
    category: str
    confidence: float
    source: str
    explanation: str
