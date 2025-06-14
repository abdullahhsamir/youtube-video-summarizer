import argparse
import os
from datetime import datetime
from src.agents import YouTubeSummarizerAgent
from src.utils.utils import save_summary_to_file

def main():
    parser = argparse.ArgumentParser(description='YouTube Video Summarizer')
    parser.add_argument('-l', '--link', required=True, help='YouTube video URL to summarize')
    parser.add_argument('--save_local', action='store_true', help='Save summary to local outputs directory')
    
    args = parser.parse_args()
    
    try:
        start_time = datetime.now()
        
        agent = YouTubeSummarizerAgent()        
        summary = agent.summarize_video(args.link)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() / 60
        
        print(f"Completed at {end_time.strftime('%Y-%m-%d %H:%M:%S')} (took {duration:.2f} minutes)")
        
        if args.save_local:
            filename = save_summary_to_file(summary)
            print(f"\nSummary saved to: {filename}")
        
    except Exception as e:
        raise


if __name__ == "__main__":

    """
    EXAMPLE USAGE:
    python main.py -l "https://www.youtube.com/watch?v=example_video_id" --save_local
    """
    main()