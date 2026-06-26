from pydantic import BaseModel
from typing import Optional


class Lead(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    message: str


class AIAnalysis(BaseModel):
    client_type: str  # Малый бизнес / Корпорат / Частное лицо
    priority: str     # Высокий / Средний / Низкий
    summary: str
