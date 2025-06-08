from app.services.db_interaction import DB_service
from app.services.llm_service import LLM_call, LLM_process
from app.services.spell_checker_service import SpellCheck
from sqlalchemy.orm import Session
from fastapi import HTTPException, BackgroundTasks
from app.models import models

async def spell_check(name: str, country: str, background_tasks: BackgroundTasks) -> list[str]:
    try: 
        spell_correct_obj = SpellCheck()

        # Check of the name is already searched before
        is_exist, response = spell_correct_obj.name_exist_check(name, country)
        if is_exist:
            return response

        # Step 1: get suggestions
        suggestions = spell_correct_obj.get_suggestions(name, country)

        # Step 2: check if this a good suggestion for not
        match_check = spell_correct_obj.evaluate_suggestions(suggestions)

        if not match_check.get("is_good_match"):
            suggestions = await LLM_process(name, country)

        background_tasks.add_task(
            save_name_metadata_background,
            name=name,
            country=country,
            suggestions=suggestions
        )
        
        return suggestions
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing: {str(e)}"
        )
    

def save_name_metadata_background(name: str, country: str, suggestions: list[str]):
    """Background task function for saving to DB"""
    db_obj = DB_service()
    db_obj.save_name_metadata(name=name, country=country, suggestions=suggestions)