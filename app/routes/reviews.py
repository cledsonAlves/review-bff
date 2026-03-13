from fastapi import APIRouter
from typing import List, Dict
from app.services.database_service import get_all_reviews

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])

@router.get("/", response_model=List[Dict])
async def list_reviews():
    """Retorna todos os reviews salvos no banco de dados SQLite."""
    reviews = get_all_reviews()
    return reviews
