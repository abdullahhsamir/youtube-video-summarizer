import os
import re
from datetime import datetime
from typing import Optional
from src.extractors import YouTubeSubtitleExtractor
from src.notion_integration.noiton_saver import NotionSaver 

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

def save_summary_to_notion(file_path: str, video_url: str, ) -> str:
    """
    Save the summary to Notion using the NotionSaver class.
    :param file_path: Path to the summary file.
    :param video_url: URL of the YouTube video.
    :return: str
    A message indicating the success of the operation.
    """

    notion = NotionSaver.from_env()
    if notion.process_file(file_path, video_url):
        os.remove(file_path)  # Remove the file after processing
        return "Summary saved to Notion successfully."

    return "Failed to save summary to Notion."
