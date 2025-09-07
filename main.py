from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from src.agents import YouTubeSummarizerAgent
from src.utils import validate_youtube_url

app = FastAPI(title="YouTube Video Summarizer")


@app.get("/")
async def root():
    return {"message": "Working!.."}


@app.get("/summarize")
async def summarize_youtube_video(url: str):
    try:
        if not validate_youtube_url(url):
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")

        agent = YouTubeSummarizerAgent()
        summary_text = agent.summarize_video(url)
        timestamp = datetime.now().isoformat()

        return JSONResponse(
            content={
                "status": "success",
                "url": url,
                "summary": summary_text,
                "timestamp": timestamp,
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
