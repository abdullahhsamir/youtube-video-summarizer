import argparse
import re
from datetime import datetime
from src.agents import YouTubeSummarizerAgent
from src.utils.utils import save_summary_to_file, save_summary_to_notion, parse_time_to_milliseconds




def main():
    parser = argparse.ArgumentParser(description="YouTube Video Summarizer")
    parser.add_argument(
        "-l", "--link", required=True, help="YouTube video URL to summarize"
    )

    parser.add_argument(
        "-t", "--time", 
        help="Time range in YouTube format (e.g., '0:00:00-1:00:00' or '30-90' for seconds)"
    )
    parser.add_argument(
        "--save_local",
        action="store_true",
        help="Save summary to local outputs directory",
    )
    parser.add_argument(
        "--save_notion", action="store_true", help="Save summary to Notion"
    )


    args = parser.parse_args()

    try:
        start_time = datetime.now()

        agent = YouTubeSummarizerAgent()
        
        # Parse time range if provided
        if args.time:
            try:
                start_time_ms, end_time_ms = parse_time_to_milliseconds(args.time)
                print(f"🕒 Processing time range: {start_time_ms/1000:.1f}s to {end_time_ms/1000:.1f}s")
                summary = agent.summarize_video(
                    args.link, 
                    enable_time_range=True,
                    start_time=start_time_ms,
                    end_time=end_time_ms
                )
            except ValueError as e:
                print(f"❌ Error parsing time range: {e}")
                print("💡 Examples: '30-90', '0:30-1:30', '0:00:30-0:01:30'")
                return
        else:
            summary = agent.summarize_video(args.link)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() / 60

        print(
            f"Completed at {end_time.strftime('%Y-%m-%d %H:%M:%S')} (took {duration:.2f} minutes)"
        )

        if args.save_local:
            filename = save_summary_to_file(summary)
            print(f"\nSummary saved to: {filename}")

        if args.save_notion:
            filename = save_summary_to_file(summary)
            message = save_summary_to_notion(filename, args.link)
            print(message)

    except Exception:
        raise


if __name__ == "__main__":
    """
    EXAMPLE USAGE:
    python app.py -l "https://www.youtube.com/watch?v=5eAS2xEn_D8" --save_local
    python app.py -l "https://www.youtube.com/watch?v=5eAS2xEn_D8" --save_notion
    python app.py -l "https://www.youtube.com/watch?v=5eAS2xEn_D8" -t "30-120" --save_local
    python app.py -l "https://www.youtube.com/watch?v=5GEoaC_g-Wk" -t "0:00:00-1:00:00" --save_notion
    """
    main()
