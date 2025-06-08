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

class NameSuggestion(BaseModel):
    name: str
    similarity_score: float
    score_breakdown: ScoreBreakdown

class NameSuggestionSimple(BaseModel):
    name: str
    similarity_score: float

class NameSuggestionsResponse(BaseModel):
    suggestions: List[NameSuggestion]
    
class NameSuggestionsSimpleResponse(BaseModel):
    suggestions: List[NameSuggestionSimple]

