from datetime import datetime

from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    date: datetime
    description: str
    amount: float


class TransactionOut(BaseModel):
    id: str
    date: datetime
    description: str
    amount: float
    category: str | None = None
    confidence: float | None = None
    source: str | None = None
    explanation: str | None = None


class TransactionUploadResponse(BaseModel):
    inserted: int


class CategorizeResponse(BaseModel):
    category: str
    confidence: float
    source: str
    explanation: str


class MonthSummary(BaseModel):
    month: str = Field(description="YYYY-MM")
    total_spend: float
    by_category: dict[str, float]
