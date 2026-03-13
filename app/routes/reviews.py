from fastapi import APIRouter
from typing import List, Dict
from app.services.database_service import get_all_reviews, get_reviews_by_package

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])

@router.get("/", response_model=List[Dict])
async def list_reviews():
    """Retorna todos os reviews salvos no banco de dados SQLite."""
    reviews = get_all_reviews()
    return reviews

@router.get("/{package}", response_model=List[Dict])
async def list_reviews_by_app(package: str):
    """Retorna os reviews salvos no banco para um app específico (package)."""
    reviews = get_reviews_by_package(package)
    return reviews
