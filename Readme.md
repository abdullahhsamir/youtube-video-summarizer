# YouTube Video Summarizer

A Python application that extracts subtitles from YouTube videos and generates comprehensive summaries using Google's Gemini AI model.

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
   ```

## Getting Your Google API Key

1. Go to the [Google AI Studio](https://aistudio.google.com/)
2. Click "Create API Key"
3. Copy the generated API key and add it to your `.env` file

## Usage

### Basic Usage
Summarize a YouTube video and display the result in the terminal:
```bash
python main.py -l "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Save Summary Locally
Summarize a video and save the result to the `outputs` directory:
```bash
python main.py -l "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --save_local
```

### Command Line Arguments
- `-l, --link` (required): YouTube video URL to summarize
- `--save_local` (optional): Save summary to local outputs directory with timestamp

## Output Format

When using the `--save_local` flag, summaries are saved to:
- **Directory**: `outputs/`
- **Filename format**: `summary_YYYYMMDD_HHMMSS.txt`
- **Encoding**: UTF-8
