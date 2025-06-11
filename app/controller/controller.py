from app.models.scheme import SpellCheckResponse, Suggestion
from app.services.db_interaction import DB_service
from app.services.llm_service import LLM_call, LLM_process
from app.services.spell_checker_service import SpellCheck
from sqlalchemy.orm import Session
from fastapi import HTTPException, BackgroundTasks
from app.models import models
from app.utils.utils import save_name_metadata_background

async def spell_check(name: str, country: str, background_tasks: BackgroundTasks) -> SpellCheckResponse:
    try:
        spell_correct_obj = SpellCheck()

        # Existency Check: Check if the name is already searched before
        is_exist, response_suggestions = spell_correct_obj.name_exist_check(name, country)
        if is_exist:
            return SpellCheckResponse(suggestions=response_suggestions)

        # Step 1: get suggestions based on the metaphones
        suggestions = spell_correct_obj.get_suggestions(name, country)

        # Step 2: check if this a good suggestion or not
        match_check = spell_correct_obj.evaluate_suggestions(suggestions)

        # Step 3: if not a good match then use the LLM call
        if not match_check.is_good_match:
            llm_suggestions_raw = await LLM_process(name, country)
            suggestions = [Suggestion(**s) for s in llm_suggestions_raw]


        background_tasks.add_task(
            save_name_metadata_background,
            name=name,
            country=country,
            suggestions=[s.model_dump() for s in suggestions] # Convert Pydantic models to dict for background task
        )

        return SpellCheckResponse(suggestions=suggestions)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing: {str(e)}"
        )
    

