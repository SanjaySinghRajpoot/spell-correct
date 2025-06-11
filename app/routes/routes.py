from fastapi import APIRouter, HTTPException, Path, Request
from fastapi import Depends, BackgroundTasks
from app.db_config import SessionLocal
from app.controller.controller import spell_check
from sqlalchemy.orm import Session
from app.models.scheme import CorrectionRequest, Response
from app.services.db_interaction import DB_service


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def read_root():

    data = DB_service()

    data.initialize_database()

    return {"Hello": "World"}


@router.post("/name-correction")
async def spell_suggest(
    request: CorrectionRequest,
    background_tasks: BackgroundTasks,
):
    try:
        name = request.name
        country = request.country if request.country else None
        
        suggested_names = await spell_check(name, country, background_tasks)
        
        return Response(
            status="Ok",
            code="200",
            message="Successfully processed",
            result=suggested_names
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing: {str(e)}"
        )