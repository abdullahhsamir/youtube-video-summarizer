import os
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from dotenv import load_dotenv
from src.utils import get_clean_subtitles

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


@dataclass
class SummarizerConfig:
    model_name: str = "gemini-2.0-flash"
    temperature: float = 0.1
    max_tokens: int = 8192
    timeout: Optional[int] = None
    max_retries: int = 2


class AgentGraphState(TypedDict):
    start_link: str
    summarized_text: str


class YouTubeSummarizerAgent:    
    def __init__(self, config: Optional[SummarizerConfig] = None):
        self.config = config or SummarizerConfig()
        self._initialize_llm()
        self.graph = self._build_graph()
    
    def _initialize_llm(self) -> None:
        load_dotenv('.env')
        
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        self.llm = ChatGoogleGenerativeAI(
            model=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries,
            google_api_key=api_key
        )
        logger.info(f"LLM initialized with model: {self.config.model_name}")
    
    def _summarize_node(self, state: AgentGraphState) -> Dict[str, Any]:
        if 'start_link' not in state or not state['start_link']:
            raise ValueError("State must contain a valid 'start_link' with the YouTube video URL")
        
        try:
            logger.info("Starting extraction and summarization process")

            start_link = state['start_link']
            logger.info(f"Processing video: {start_link}")
            
            subtitle = get_clean_subtitles(start_link)
            if not subtitle:
                raise ValueError("Failed to extract subtitles from the video")
            
            logger.info("Subtitles extracted successfully")
            
            summarize_prompt = self._create_summarization_prompt(subtitle)
            logger.info("Sending subtitles to LLM for summarization")
            
            response = self.llm.invoke(summarize_prompt)
            summarized_text = response.content
            
            if not summarized_text:
                raise ValueError("LLM returned empty summary")
            
            logger.info("Summarization completed successfully")
            
            state['summarized_text'] = summarized_text
            return state
            
        except Exception as e:
            logger.error(f"Error during summarization: {str(e)}")
            raise
    
    def _create_summarization_prompt(self, subtitle: str) -> str:
        return f"""
        Summarize the following YouTube video transcript into a well-structured article.
        Maintain the original language of the content and ensure the summary is comprehensive yet concise.

        DON'T SAY SOMETHING LIKE "Here is the summary of the video" or "The video is about". Just write the article directly.
        
        Instructions:
        - Create clear headings and sections
        - Preserve key points and important details
        - Maintain the original tone and context
        - Structure the content in a readable format
        - Don't summarize it too much, make it as an article!
        
        Transcript:
        {subtitle}
        """
    
    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentGraphState)
        graph.add_node('summarize', self._summarize_node)
        graph.add_edge(START, 'summarize')
        graph.add_edge('summarize', END)
        
        compiled_graph = graph.compile()
        logger.info("Summarization graph compiled successfully")
        
        return compiled_graph
    
    def summarize_video(self, video_url: str) -> str:
        if not video_url or not isinstance(video_url, str):
            raise ValueError("A valid YouTube video URL is required")
        
        try:
            state = {'start_link': video_url}
            result = self.graph.invoke(state)
            return result['summarized_text']
            
        except Exception as e:
            logger.error(f"Failed to summarize video {video_url}: {str(e)}")
            raise



# if __name__ == "__main__":
#     try:
#         agent = YouTubeSummarizerAgent()
#         logger.info("YouTube Summarizer Agent initialized successfully")
        
#         test_video_url = "https://www.youtube.com/watch?v=5eAS2xEn_D8"
        
#         logger.info(f"Processing video: {test_video_url}")
#         summary = agent.summarize_video(test_video_url)
        
#         logger.info("Summarization completed successfully")
#         print("\n" + "="*80)
#         print("SUMMARY:")
#         print("="*80)
#         print(summary)
#         print("="*80)
        
#     except Exception as e:
#         logger.error(f"Application error: {str(e)}")
#         raise