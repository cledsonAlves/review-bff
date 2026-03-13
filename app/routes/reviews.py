from fastapi import APIRouter, Query
from typing import List, Dict, Optional
from app.services.database_service import get_all_reviews, get_reviews_by_package, get_reviews_by_package_and_store

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])

@router.get("/", response_model=List[Dict])
async def list_reviews(
    package: Optional[str] = Query(None, description="ID do pacote do app"),
    store: Optional[str] = Query(None, description="Loja (google_play ou apple_store)")
):
    """
    Retorna os reviews salvos no banco. 
    Permite filtrar por package e store para trazer apenas os dados da plataforma escolhida.
    """
    if package and store:
        return get_reviews_by_package_and_store(package, store)
    elif package:
        return get_reviews_by_package(package)
    
    return get_all_reviews()

@router.get("/{package}", response_model=List[Dict])
async def list_reviews_by_app(package: str):
    """Retorna os reviews salvos no banco para um app específico (package)."""
    reviews = get_reviews_by_package(package)
    return reviews
