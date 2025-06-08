from typing import List, Dict
from pydantic import BaseModel

from app.models.scheme import NameSuggestion, NameSuggestionSimple, NameSuggestionsResponse, NameSuggestionsSimpleResponse
from app.services.db_interaction import DB_service


def convert_to_pydantic_response(json_response: List[Dict[str, float]], include_breakdown: bool = False) -> BaseModel:
    """
    Convert JSON response to Pydantic model response.
    
    Args:
        json_response: The JSON response from get_suggestions
        include_breakdown: Whether to include score breakdown in response
        
    Returns:
        Either NameSuggestionsResponse or NameSuggestionsSimpleResponse
    """
    if include_breakdown:
        suggestions = [NameSuggestion(**suggestion) for suggestion in json_response]
        return NameSuggestionsResponse(suggestions=suggestions)
    else:
        simple_suggestions = [NameSuggestionSimple(
            name=suggestion["name"],
            similarity_score=suggestion["similarity_score"]
        ) for suggestion in json_response]
        return NameSuggestionsSimpleResponse(suggestions=simple_suggestions)
    
def save_name_metadata_background(name: str, country: str, suggestions: list[str]):
    """Background task function for saving to DB"""
    db_obj = DB_service()
    db_obj.save_name_metadata(name=name, country=country, suggestions=suggestions)