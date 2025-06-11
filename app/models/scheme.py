from typing import List, Optional, Generic, TypeVar
from pydantic import BaseModel , Field
from pydantic.generics import GenericModel

T = TypeVar('T')

class CorrectionRequest(BaseModel):
    name: str
    country: str = None

class Response(GenericModel, Generic[T]):
    code: str
    status: str
    message: str
    result: Optional[T]

class ScoreBreakdown(BaseModel):
    phonetic: float
    edit_distance: float
    jaro_winkler: float

class Suggestion(BaseModel):
    name: str
    similarity_score: float

class SpellCheckResponse(BaseModel):
    suggestions: List[Suggestion] = Field(..., description="List of spelling suggestions with similarity scores.")

class EvaluationResponse(BaseModel):
    is_good_match: bool
    filtered_suggestions: List[Suggestion] = Field(..., description="Suggestions that meet the evaluation criteria.")


