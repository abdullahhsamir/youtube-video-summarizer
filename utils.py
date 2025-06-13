import requests
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
import logging



logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("utils")
logger.setLevel(logging.INFO)



def get_clean_subtitles(video_url: str, lang: str = None) -> str:
    """
    Fetches and cleans YouTube subtitles for a given video.

    Args:
        video_url: YouTube video URL
        lang: Language code (default: 'ar' for Arabic)

    Returns:
        Cleaned subtitle text as a single string
    """
    if lang is None:
        logger.info("No language code provided, extracting automatically from the video.")
        video_id = video_url.split("=")[-1]
        for t in YouTubeTranscriptApi().list(video_id):
            lang = t.language_code
            logger.info(f"Using language code: {lang}")
    
    if not lang:
        logger.error("No language code found for the video.")
        raise ValueError("No language code found for the video")
    
        
    with yt_dlp.YoutubeDL({
        "subtitlesformat": "json3",
        "subtitleslangs": [lang],
        "skip_download": True,
        "quiet": True,
    }) as ydl:
        
        logger.info(f"Fetching subtitles for language: {lang}")
        info = ydl.extract_info(video_url, download=False)
        subs = info.get("subtitles", {}).get(lang) or info.get("automatic_captions", {}).get(lang)
        
        if not subs:
            raise ValueError(f"No subtitles found for language: {lang}")

        sub_url = next(s["url"] for s in subs if s["ext"] == "json3")
        logger.info(f"Subtitles URL: {sub_url}")

    response = requests.get(sub_url)
    logger.info("Fetching subtitles from URL...")
    if response.status_code != 200:
        logger.error(f"Failed to fetch subtitles: {response.status_code}")
    
    response.raise_for_status()
    logger.info("Subtitles fetched successfully, cleaning up...")
    return " ".join(
        seg["utf8"]
        for event in response.json().get("events", [])
        for seg in event.get("segs", [])
        if "utf8" in seg
    )


# if __name__ == "__main__":
#     video_url = "https://www.youtube.com/watch?v=5eAS2xEn_D8"
#     try:
#         subtitles = get_clean_subtitles(video_url)
#         print(subtitles)
#     except Exception as e:
#         print(f"Error fetching subtitles: {e}")