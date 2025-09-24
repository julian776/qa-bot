from pydantic import BaseModel
from typing import Optional

class QARequest(BaseModel):
    question: str

class QAResponse(BaseModel):
    id: int
    question: str
    answer: str
