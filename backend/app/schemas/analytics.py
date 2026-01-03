from pydantic import BaseModel


class DashboardSummary(BaseModel):
    month: str
    total_spend: float
    top_category: str | None
    top_category_spend: float
    avg_confidence: float | None


class TrendPoint(BaseModel):
    month: str
    total_spend: float


class AnomalyPoint(BaseModel):
    date: str
    amount: float
    description: str
    zscore: float
