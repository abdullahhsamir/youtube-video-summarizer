import logging
from typing import Optional, Dict, Any, List
import requests
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound


class YouTubeSubtitleExtractor:
    
    def __init__(self, log_level: int = logging.INFO):
        self.logger = self._setup_logger(log_level)
        self.ydl_opts = {
            "subtitlesformat": "json3",
            "skip_download": True,
            "quiet": True,
        }
    
    def _setup_logger(self, level: int) -> logging.Logger:
        logger = logging.getLogger(__name__)
        logger.setLevel(level)
        
        # Prevent duplicate handlers
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.propagate = False
        
        return logger
    
    def _extract_video_id(self, video_url: str) -> str:
        try:
            if "watch?v=" in video_url:
                return video_url.split("watch?v=")[-1].split("&")[0]
            elif "youtu.be/" in video_url:
                return video_url.split("youtu.be/")[-1].split("?")[0]
            else:
                raise ValueError("Invalid YouTube URL format")
        except Exception as e:
            raise ValueError(f"Failed to extract video ID: {e}")
    
    def _detect_language(self, video_url: str) -> Optional[str]:
        try:
            video_id = self._extract_video_id(video_url)
            self.logger.info(f"Detecting language for video ID: {video_id}")
            transcripts = YouTubeTranscriptApi().list(video_id = video_id)
            
            for transcript in transcripts:
                self.logger.info(f"Found transcript in language: {transcript.language_code}")
                return transcript.language_code
                
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            self.logger.warning(f"No transcripts available: {e}")
        except Exception as e:
            self.logger.error(f"Error detecting language: {e}")
        
        return None
    
    def _get_subtitle_url(self, video_url: str, lang: str) -> str:
        ydl_opts = {**self.ydl_opts, "subtitleslangs": [lang]}
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(video_url, download=False)
                subtitles = info.get("subtitles", {}).get(lang)
                auto_captions = info.get("automatic_captions", {}).get(lang)
                
                subs = subtitles or auto_captions
                
                if not subs:
                    raise ValueError(f"No subtitles found for language: {lang}")
                
                # Note: yt-dlp may return multiple formats, I prefer json3 for cleaning
                for sub in subs:
                    if sub.get("ext") == "json3":
                        return sub["url"]
                
                raise ValueError(f"No JSON3 format subtitles found for language: {lang}")
                
            except Exception as e:
                raise ValueError(f"Failed to extract subtitle info: {e}")
    
    def _fetch_and_clean_subtitles(self, subtitle_url: str) -> str:
        try:
            response = requests.get(subtitle_url, timeout=30)
            response.raise_for_status()
            
            subtitle_data = response.json()
            events = subtitle_data.get("events", [])
            
            text_segments = []
            for event in events:
                for segment in event.get("segs", []):
                    if "utf8" in segment:
                        text_segments.append(segment["utf8"])
            
            return " ".join(text_segments).strip()
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch subtitles: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error processing subtitle data: {e}")
            raise ValueError(f"Failed to process subtitle data: {e}")
    
    def get_clean_subtitles(self, video_url: str, lang: Optional[str] = None) -> str:
        self.logger.info(f"Processing video: {video_url}")
        
        # Auto-detect language if not provided which means you can use any language that has subtitles
        if lang is None:
            self.logger.info("Auto-detecting subtitle language...")
            lang = self._detect_language(video_url)
            
            if not lang:
                raise ValueError("No subtitle language could be detected")
        
        self.logger.info(f"Using language code: {lang}")
        
        subtitle_url = self._get_subtitle_url(video_url, lang)
        self.logger.info("Subtitle URL obtained successfully")
        self.logger.info("Fetching and cleaning subtitles...")
        cleaned_text = self._fetch_and_clean_subtitles(subtitle_url)
        
        self.logger.info(f"Successfully extracted {len(cleaned_text)} characters of subtitle text")
        return cleaned_text

