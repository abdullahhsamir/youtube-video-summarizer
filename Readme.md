# YouTube Video Summarizer

A Python application that extracts subtitles from YouTube videos and generates comprehensive summaries using Google's Gemini AI model. The application provides both command-line interface (CLI) and FastAPI web API options.

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd youtube-video-summarizer
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   NOTION_TOKEN=your_notion_integration_token_here
   NOTION_PARENT_PAGE_ID=your_notion_parent_page_id_here
   ```

## Getting Your API Keys

### Google API Key
1. Go to the [Google AI Studio](https://aistudio.google.com/)
2. Click "Create API Key"
3. Copy the generated API key and add it to your `.env` file

### Notion Integration Setup
To use the Notion integration feature, you need to set up a Notion integration:

1. **Create Notion Integration**:
   - Go to [Notion Integrations](https://www.notion.so/my-integrations)
   - Click "New integration"
   - Give it a name (e.g., "YouTube Summarizer")
   - Select the workspace where you want to use it
   - Copy the "Internal Integration Token"

2. **Create Parent Page**:
   - Create a new page in your Notion workspace (e.g., "YouTube Summaries")
   - Share this page with your integration:
     - Click "Share" on the page
     - Click "Invite" and select your integration
     - Give it "Edit" permissions

3. **Get Page ID**:
   - Copy the page URL from your browser
   - Extract the page ID from the URL (the long string after the last `/` and before any `?`)
   - Example: `https://notion.so/My-Page-1234567890abcdef` → Page ID: `1234567890abcdef`

4. **Add to Environment**:
   ```env
   NOTION_TOKEN=your_integration_token_here
   NOTION_PARENT_PAGE_ID=your_page_id_here
   ```

## Usage Options

You have two ways to run the YouTube Video Summarizer:

### Option 1: Command Line Interface (CLI)

Use the [`app.py`](app.py) script for direct command-line usage:

#### Basic Usage
Summarize a YouTube video and display the result in the terminal:
```bash
python app.py -l "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

#### Save Summary Locally
Summarize a video and save the result to the `outputs` directory:
```bash
python app.py -l "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --save_local
```

#### Save Summary to Notion
Summarize a video and save it directly to your Notion workspace:
```bash
python app.py -l "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --save_notion
```

#### Time Range Extraction
Summarize only a specific time range of a video:
```bash
python app.py -l "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -t "30-120" --save_local
python app.py -l "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -t "1:30-3:45" --save_notion
```

#### Command Line Arguments
- `-l, --link` (required): YouTube video URL to summarize
- `-t, --time` (optional): Time range to extract (e.g., '30-90', '1:30-3:45', '0:00:30-0:01:30')
- `--save_local` (optional): Save summary to local outputs directory with timestamp
- `--save_notion` (optional): Save summary to Notion (requires Notion setup)

### Option 2: FastAPI Web Server

Use the [`main.py`](main.py) script to run a web API server:

#### Start the Server
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### API Endpoints

Once the server is running (by default at `http://localhost:8000`):

- **Health Check**: `GET /`
  ```
  http://localhost:8000/
  ```

- **Summarize Video**: `GET /summarize`
  ```
  http://localhost:8000/summarize?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ
  ```

#### API Response Format
```json
{
  "status": "success",
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "summary": "Generated summary text...",
  "timestamp": "2025-01-15T10:30:00.123456"
}
```

## Notion Integration Features

When using the `--save_notion` option, the application will:

1. **Automatic Title Extraction**: Uses the first `#` heading in the summary as the Notion page title
2. **YouTube Video Embed**: Embeds the original YouTube video at the top of the page
3. **Formatted Content**: Converts the summary to properly formatted Notion blocks with headings and paragraphs
4. **Organized Storage**: Creates child pages under your specified parent page for easy organization

### Notion Page Structure
Each generated Notion page includes:
- **Title**: Extracted from the summary's first `#` heading (fallback to filename)
- **YouTube Embed**: The original video embedded for easy reference
- **Formatted Summary**: The AI-generated summary with proper headings and formatting

## Output Format

### Local Files
When using the CLI with `--save_local` flag, summaries are saved to:
- **Directory**: `outputs/`
- **Filename format**: `summary_YYYYMMDD_HHMMSS.txt`
- **Encoding**: UTF-8

## Requirements

- Python 3.8+
- Google API Key (for Gemini AI)
- Notion Integration Token (optional, for Notion features)
