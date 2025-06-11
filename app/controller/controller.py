from app.models.scheme import SpellCheckResponse, Suggestion
from app.services.db_interaction import DB_service
from app.services.llm_service import LLM_call, LLM_process
from app.services.spell_checker_service import SpellCheck
from sqlalchemy.orm import Session
from fastapi import HTTPException, BackgroundTasks
from app.models import models
from app.utils.utils import save_name_metadata_background
import logging

logger = logging.getLogger(__name__)

async def spell_check(name: str, country: str, db: Session, background_tasks: BackgroundTasks) -> SpellCheckResponse:
    try:
        logger.info(f"Starting spell check [name: {name}, country: {country}]")

        spell_correct_obj = SpellCheck(db_session=db)
  

        # Existency Check: Check if the name is already searched before
        is_exist, response_suggestions = spell_correct_obj.name_exist_check(name, country)
        if is_exist:
            return SpellCheckResponse(suggestions=response_suggestions)
        
        logger.info(f"name_exist_check completed [is_exist: {is_exist}]")

        # Step 1: get suggestions based on the metaphones
        suggestions = spell_correct_obj.get_suggestions(name, country)

        # Step 2: check if this a good suggestion or not
        match_check = spell_correct_obj.evaluate_suggestions(suggestions)

        logger.info(f"evaluate_suggestions completed [match_check: {match_check.is_good_match}]")

        # Step 3: if not a good match then use the LLM call
        if not match_check.is_good_match:
            llm_suggestions_raw = await LLM_process(name, country)
            suggestions = [Suggestion(**s) for s in llm_suggestions_raw]

            logger.info(f"LLM_process completed [llm_suggestions_raw: {llm_suggestions_raw}]")


        background_tasks.add_task(
            save_name_metadata_background,
            name=name,
            country=country,
            db_sesion=db,
            suggestions=[s.model_dump() for s in suggestions]
        )

        logger.info(f"Spell process completed!!")

        return SpellCheckResponse(suggestions=suggestions)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing: {str(e)}"
        )
    

