import logging
from typing import Optional

from google_play_scraper import app as gps_app
from google_play_scraper import reviews as gps_reviews
from google_play_scraper import Sort

from app.schemas.review import AppInfo, ReviewItem

logger = logging.getLogger(__name__)


def get_app_info(package: str, lang: str = "pt", country: str = "br") -> AppInfo:
    """Busca os metadados do app na Play Store."""
    try:
        data = gps_app(package, lang=lang, country=country)
    except Exception as e:
        logger.error(f"Erro ao buscar info do app '{package}': {e}")
        raise ValueError(f"App '{package}' não encontrado ou indisponível na Play Store.")

    return AppInfo(
        package=package,
        title=data.get("title", ""),
        version=data.get("version", "N/A"),
        score=data.get("score"),
        ratings=data.get("ratings"),
        reviews_count=data.get("reviews"),
        installs=data.get("installs"),
        developer=data.get("developer", ""),
        developer_email=data.get("developerEmail"),
        genre=data.get("genre"),
        released=data.get("released"),
        updated=str(data.get("updated")) if data.get("updated") else None,
        description_short=data.get("summary"),
        icon_url=data.get("icon"),
        url=data.get("url", f"https://play.google.com/store/apps/details?id={package}"),
    )


def get_reviews(
    package: str,
    lang: str = "pt",
    country: str = "br",
    count: int = 100,
) -> list[ReviewItem]:
    """Busca os reviews do app na Play Store."""
    try:
        result, _ = gps_reviews(
            package,
            lang=lang,
            country=country,
            sort=Sort.NEWEST,
            count=count,
        )
    except Exception as e:
        logger.error(f"Erro ao buscar reviews do app '{package}': {e}")
        raise ValueError(f"Não foi possível buscar reviews para '{package}'.")

    reviews = []
    for r in result:
        reviews.append(
            ReviewItem(
                review_id=r.get("reviewId", ""),
                user_name=r.get("userName", "Anônimo"),
                user_image=r.get("userImage"),
                rating=r.get("score", 3),
                content=r.get("content", ""),
                thumbs_up=r.get("thumbsUpCount", 0),
                app_version=r.get("reviewCreatedVersion"),
                date=r.get("at").isoformat() if r.get("at") else None,
                reply_content=r.get("replyContent"),
                reply_date=r.get("repliedAt").isoformat() if r.get("repliedAt") else None,
            )
        )
    return reviews
