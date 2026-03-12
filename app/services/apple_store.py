import logging
import requests
from app.schemas.review import AppInfo, ReviewItem

logger = logging.getLogger(__name__)

def get_app_info(package: str, lang: str = "pt", country: str = "br") -> AppInfo:
    """Busca os metadados do app na App Store usando iTunes Lookup API."""
    url = f"https://itunes.apple.com/lookup?bundleId={package}&country={country}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("resultCount", 0) == 0:
            raise ValueError(f"App '{package}' não encontrado ou indisponível na App Store.")
        
        info = data["results"][0]
        
        return AppInfo(
            package=package,
            title=info.get("trackName", ""),
            version=info.get("version", "N/A"),
            score=info.get("averageUserRating"),
            ratings=info.get("userRatingCount"),
            reviews_count=info.get("userRatingCount"),
            installs=None, # A App Store não fornece contagem de instalações publica
            developer=info.get("artistName", ""),
            developer_email=None,
            genre=info.get("primaryGenreName"),
            released=info.get("releaseDate"),
            updated=info.get("currentVersionReleaseDate"),
            description_short=info.get("description", "")[:250] if info.get("description") else None,
            icon_url=info.get("artworkUrl512", info.get("artworkUrl100")),
            url=info.get("trackViewUrl", f"https://apps.apple.com/{country}/app/id{info.get('trackId')}")
        )
    except ValueError as e:
        raise e
    except Exception as e:
        logger.error(f"Erro ao buscar info do app (Apple Store) '{package}': {e}")
        raise ValueError(f"App '{package}' não encontrado ou indisponível na App Store.")

def get_reviews(
    package: str,
    lang: str = "pt",
    country: str = "br",
    count: int = 100,
) -> list[ReviewItem]:
    """Busca os reviews do app na App Store usando RSS API."""
    url = f"https://itunes.apple.com/lookup?bundleId={package}&country={country}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("resultCount", 0) == 0:
            raise ValueError(f"App '{package}' não encontrado na App Store.")
        app_id = data["results"][0].get("trackId")
    except Exception as e:
        logger.error(f"Erro ao buscar ID do app '{package}': {e}")
        raise ValueError(f"Não foi possível buscar ID para '{package}' na App Store.")

    reviews = []
    page = 1
    
    # RSS API para reviews tem limite de até 50 reviews por página e máx de 10 páginas (500 reviews)
    while len(reviews) < count and page <= 10:
        rss_url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json"
        
        try:
            r = requests.get(rss_url, timeout=10)
            if r.status_code != 200:
                break
            
            feed = r.json().get("feed", {})
            entries = feed.get("entry", [])
            
            if not entries:
                break
                
            # Muitas vezes o primeiro item em feed['entry'] no RSS de reviews da Apple é o resumo do próprio app (isso acontece historicamente)
            # Vamos tratar apenas onde o autor seja um usuário válido e tenha rating
            for item in entries:
                author_name = item.get("author", {}).get("name", {}).get("label")
                if not author_name or author_name == "iTunes Store":
                    continue
                    
                rating_str = item.get("im:rating", {}).get("label", "0")
                rating = int(rating_str) if rating_str.isdigit() else 3
                
                reviews.append(
                    ReviewItem(
                        review_id=item.get("id", {}).get("label", ""),
                        user_name=author_name,
                        user_image=None,
                        rating=rating,
                        content=item.get("content", {}).get("label", ""),
                        thumbs_up=0,
                        app_version=item.get("im:version", {}).get("label", ""),
                        date=item.get("updated", {}).get("label", ""),
                        reply_content=None, # Não disponível via RSS público
                        reply_date=None,
                    )
                )
                
                if len(reviews) >= count:
                    break
                    
            page += 1
        except Exception as e:
            logger.warning(f"Erro ao buscar a pagina {page} de reviews do app {package}: {e}")
            break

    return reviews[:count]
