from typing import Optional
from src.extractors import YouTubeSubtitleExtractor

def get_clean_subtitles(video_url: str, lang: Optional[str] = None) -> str:
    extractor = YouTubeSubtitleExtractor()
    return extractor.get_clean_subtitles(video_url, lang)
