from typing import List, Dict
from pydantic import BaseModel

from app.services.db_interaction import DB_service
    
def save_name_metadata_background(name: str, country: str, suggestions: list[str]):
    """Background task function for saving to DB"""
    db_obj = DB_service()
    db_obj.save_name_metadata(name=name, country=country, suggestions=suggestions)