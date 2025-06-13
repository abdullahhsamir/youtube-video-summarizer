from src.agents import YouTubeSummarizerAgent




if __name__ == "__main__":
    try:
        agent = YouTubeSummarizerAgent()        
        test_video_url = "https://www.youtube.com/watch?v=5eAS2xEn_D8"
        
        summary = agent.summarize_video(test_video_url)
        

        print("\n" + "="*80)
        print("SUMMARY:")
        print("="*80)
        print(summary)
        print("="*80)
        
    except Exception as e:
        raise