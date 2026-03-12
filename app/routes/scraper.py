import logging

from fastapi import APIRouter, HTTPException, Path

from app.schemas.review import AppInfo, ScrapeRequest, ScrapeResponse
from app.services.play_store import get_app_info as get_play_app_info, get_reviews as get_play_reviews
from app.services.apple_store import get_app_info as get_apple_app_info, get_reviews as get_apple_reviews
from app.services.database_service import save_reviews_to_sqlite

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["App Stores"])


@router.post(
    "/scrape",
    response_model=ScrapeResponse,
    summary="Scrape reviews e informações do app",
    description=(
        "Busca informações do app (versão, rating, instalações) e os reviews "
        "mais recentes da Google Play Store para o pacote informado."
    ),
)
async def scrape_app(request: ScrapeRequest) -> ScrapeResponse:
    try:
        if request.store == "apple_store":
            app_info = get_apple_app_info(request.package, lang=request.lang, country=request.country)
            reviews = get_apple_reviews(
                request.package,
                lang=request.lang,
                country=request.country,
                count=request.count,
            )
        else:
            app_info = get_play_app_info(request.package, lang=request.lang, country=request.country)
            reviews = get_play_reviews(
                request.package,
                lang=request.lang,
                country=request.country,
                count=request.count,
            )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Erro inesperado ao processar scraping de '{request.package}'")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar dados das lojas.")

    # Salva os reviews no SQLite de forma assíncrona (ou apenas chama a função)
    # Nota: Poderíamos disparar isso em background, mas para simplicidade faremos aqui.
    if reviews:
        save_reviews_to_sqlite(reviews, request.store, request.package)

    return ScrapeResponse(
        app_info=app_info,
        reviews=reviews,
        total=len(reviews),
        lang=request.lang,
        country=request.country,
        store=request.store,
    )


@router.get(
    "/app-info/{package:path}",
    response_model=AppInfo,
    summary="Busca informações do app",
    description="Retorna somente os metadados do app (versão, desenvolvedor, rating etc).",
)
async def app_info(
    package: str = Path(..., description="ID do pacote. Ex: com.itau.investimentos"),
    store: str = "google_play",
    lang: str = "pt",
    country: str = "br",
) -> AppInfo:
    try:
        if store == "apple_store":
            return get_apple_app_info(package, lang=lang, country=country)
        return get_play_app_info(package, lang=lang, country=country)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        logger.exception(f"Erro inesperado ao buscar info do app '{package}'")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar dados das lojas.")
