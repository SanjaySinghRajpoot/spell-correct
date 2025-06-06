from app.services.llm_service import LLM_call
from app.services.spell_checker_service import SpellCheck
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import models

async def spell_check(name: str, country: str) -> list[str]:
    try: 

        spell_correct_obj = SpellCheck()

        # Step1: get_phonetic_candidates
        phonetic_candidates = spell_correct_obj.get_phonetic_candidates(name, country)

        # Step2: get_closest_matches
        matches, is_good_match  = spell_correct_obj.get_closest_matches(name, phonetic_candidates)

        # Step3: if not a is_good_match then call the LLM
        if not is_good_match:
            return await LLM_process(name, country)
        
        return matches
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing: {str(e)}"
        )

async def LLM_process(word: str, country: str) -> str:
    try: 
        res = await LLM_call(word)
        if res:
            return res.get("response")
        
        return "something went wrong while processing LLM process."
           
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing products: {str(e)}"
        )