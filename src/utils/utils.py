import os
import re
from datetime import datetime
from typing import Optional
from src.extractors import YouTubeSubtitleExtractor

def get_clean_subtitles(video_url: str, lang: Optional[str] = None) -> str:
    extractor = YouTubeSubtitleExtractor()
    return extractor.get_clean_subtitles(video_url, lang)


def save_summary_to_file(summary: str, outputs_dir: str = 'outputs') -> str:
    os.makedirs(outputs_dir, exist_ok=True)    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{outputs_dir}/summary_{timestamp}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    return filename


def validate_youtube_url(url: str) -> bool:
    """Validate if the URL is a valid YouTube URL"""
    youtube_pattern = r'https://www\.youtube\.com/watch\?v=[\w-]+'
    return bool(re.match(youtube_pattern, url))