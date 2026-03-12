from pydantic import BaseModel
from typing import Optional, List

class AppInfo(BaseModel):
    package: str
    title: str
    version: str
    score: Optional[float] = None
    ratings: Optional[int] = None
    reviews_count: Optional[int] = None
    installs: Optional[str] = None
    developer: str
    developer_email: Optional[str] = None
    genre: Optional[str] = None
    released: Optional[str] = None
    updated: Optional[str] = None
    description_short: Optional[str] = None
    icon_url: Optional[str] = None
    url: str

class ReviewItem(BaseModel):
    review_id: str
    user_name: str
    user_image: Optional[str] = None
    rating: int
    content: str
    thumbs_up: int = 0
    app_version: Optional[str] = None
    date: Optional[str] = None
    reply_content: Optional[str] = None
    reply_date: Optional[str] = None

class ScrapeRequest(BaseModel):
    package: str
    store: str = "google_play"
    lang: str = "pt"
    country: str = "br"
    count: int = 100

class ScrapeResponse(BaseModel):
    app_info: AppInfo
    reviews: List[ReviewItem]
    total: int
    lang: str
    country: str
    store: str

