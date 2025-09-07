import os
import re
from datetime import datetime
from typing import Optional
from src.extractors import YouTubeSubtitleExtractor
from src.notion_integration.noiton_saver import NotionSaver


def get_clean_subtitles(
    video_url: str,
    lang: Optional[str] = None,
    enable_time_range: bool = False,
    start_time: int = 0,
    end_time: int = 0,
) -> str:
    extractor = YouTubeSubtitleExtractor()
    return extractor.get_clean_subtitles(video_url, lang, enable_time_range, start_time, end_time)


def save_summary_to_file(summary: str, outputs_dir: str = "outputs") -> str:
    os.makedirs(outputs_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{outputs_dir}/summary_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(summary)

    return filename


def validate_youtube_url(url: str) -> bool:
    """Validate if the URL is a valid YouTube URL"""
    youtube_pattern = r"https://www\.youtube\.com/watch\?v=[\w-]+"
    return bool(re.match(youtube_pattern, url))


def save_summary_to_notion(
    file_path: str,
    video_url: str,
) -> str:
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


def parse_time_to_milliseconds(time_str):
    """
    Parse time string to milliseconds.
    Supports formats:
    - '30-90' (seconds)
    - '0:30-1:30' (minutes:seconds)
    - '0:00:30-0:01:30' (hours:minutes:seconds)
    
    Args:
        time_str (str): Time range string
        
    Returns:
        tuple: (start_time_ms, end_time_ms)
    """
    if '-' not in time_str:
        raise ValueError("Time range must contain '-' separator (e.g., '30-90' or '0:30-1:30')")
    
    start_str, end_str = time_str.split('-', 1)
    
    def time_to_milliseconds(t):
        # Remove whitespace
        t = t.strip()
        
        # Check if it's just seconds (number only)
        if t.isdigit():
            return int(t) * 1000
        
        # Parse time format (supports H:M:S, M:S, or S)
        parts = t.split(':')
        
        if len(parts) == 1:  # Just seconds
            return int(parts[0]) * 1000
        elif len(parts) == 2:  # M:S
            minutes, seconds = parts
            return (int(minutes) * 60 + int(seconds)) * 1000
        elif len(parts) == 3:  # H:M:S
            hours, minutes, seconds = parts
            return (int(hours) * 3600 + int(minutes) * 60 + int(seconds)) * 1000
        else:
            raise ValueError(f"Invalid time format: {t}")
    
    start_ms = time_to_milliseconds(start_str)
    end_ms = time_to_milliseconds(end_str)
    
    if start_ms >= end_ms:
        raise ValueError("Start time must be less than end time")
    
    return start_ms, end_ms