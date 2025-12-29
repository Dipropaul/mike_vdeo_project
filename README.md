# ClipForge - AI Video Generation System

![ClipForge](https://img.shields.io/badge/AI-Video%20Generation-purple)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)

ClipForge is an AI-powered video generation system that creates professional videos from text scripts using AI narration, AI-generated images, and automated video composition with cinematic effects.

## Features

✨ **6-Step Automated Video Generation Process:**

1. **Generate Narration** - Convert script to speech using ElevenLabs AI voices (with OpenAI TTS fallback)
2. **Create Image Prompts** - Generate 7 detailed image prompts using GPT-4
3. **Generate Images** - Create images using DALL-E 3 API
4. **Combine Media** - Merge images and narration in sequence
5. **Apply Effects** - Add random zoom and pan effects for cinematic feel
6. **Save Video** - Add completed video to the videos library

🎨 **Multiple Video Styles:**
- Modern Abstract
- Ink Sketch
- Comic Book
- Retro Anime
- Cyberpunk
- And more!

📐 **Multiple Video Formats:**
- 9:16 (Vertical - TikTok, Reels)
- 16:9 (Horizontal - YouTube)
- 1:1 (Square - Instagram)

🎙️ **Multiple AI Voices:**
- Bella (Expressive Narrator)
- Rachel (Calm)
- Josh (Deep)
- Antoni (Well-rounded)
- Elli (Energetic)

## Requirements

- Python 3.8 or higher
- OpenAI API key (for GPT-4 and DALL-E 3)
- ElevenLabs API key (for text-to-speech)
- FFmpeg (for video processing)

## Installation

### Windows

1. **Clone or download this repository**

2. **Create virtual environment FIRST:**
   ```powershell
   # Using PowerShell
   .\create_venv.ps1
   
   # Or using Command Prompt
   create_venv.bat
   
   # Or manually
   python -m venv venv
   ```

3. **Activate virtual environment:**
   ```powershell
   # PowerShell
   .\venv\Scripts\Activate.ps1
   
   # Command Prompt
   venv\Scripts\activate
   ```

4. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Edit the .env file and add your API keys:**
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here  # Optional - will use OpenAI TTS if not provided
   ```

6. **Install FFmpeg:**
   - Download from: https://ffmpeg.org/download.html
   - Add to system PATH

## Usage

1. **Activate virtual environment (if not already activated):**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

2. **Start the FastAPI application:**
   ```powershell
   python app.py
   
   # Or use uvicorn directly
   uvicorn app:app --reload --host 0.0.0.0 --port 5000
   ```

3. **Open your browser to:**
   ```
   http://localhost:5000
   ```

4. **View API documentation at:**
   ```
   http://localhost:5000/docs
   ```

3. **Create your video:**
   - Enter video title and category
   - Select video format (9:16, 16:9, or 1:1)
   - Choose visual style
   - Select AI voice
   - Paste your script (max 800 characters)
   - Click "CREATE NEW VIDEO"

4. **Wait for generation** (5-10 minutes)

5. **Download your video** from the All Videos list

## Project Structure

```
video_mike/
├── app.py                    # Flask web application
├── config.py                 # Configuration settings
├── pipeline.py               # Main video generation pipeline
├── narration_generator.py    # Text-to-speech module
├── prompt_generator.py       # Image prompt generation
├── image_generator.py        # Image generation using DALL-E
├── video_composer.py         # Video composition and effects
├── requirements.txt          # Python dependencies
├── setup.ps1                 # Setup script
├── .env.example             # Environment variables template
├── templates/               # HTML templates
│   └── index.html
├── static/                  # CSS and JavaScript
│   ├── style.css
│   └── script.js
└── outputs/                 # Generated content
    ├── videos/
    ├── images/
    └── audio/
```

## API Endpoints

- `GET /` - Main page
- `POST /api/create-video` - Create new video
- `GET /api/job-status/<job_id>` - Check video generation status
- `GET /api/all-videos` - Get all generated videos
- `GET /api/video/<video_id>` - Get specific video details
- `GET /api/download/<video_id>` - Download video file
- `GET /api/config` - Get application configuration

## Configuration

Edit `.env` file to customize:

```env
# API Keys
OPENAI_API_KEY=your_key_here
ELEVENLABS_API_KEY=your_key_here

# Server Settings
DEBUG=True
HOST=0.0.0.0
PORT=5000

# Video Settings
DEFAULT_FPS=30
DEFAULT_DURATION_PER_IMAGE=5
IMAGE_COUNT=7
MAX_SCRIPT_LENGTH=800
```

## Troubleshooting

**Video generation fails:**
- Check API keys in `.env` file
- Ensure you have sufficient API credits
- Check internet connection

**FFmpeg errors:**
- Install FFmpeg and, DALL-E 3, and TTS (fallback narration)
- **ElevenLabs** - Text-to-speech AI (primary narration)
- **MoviePy** - Video editing
- **FastAPI** - Modern wund:**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

## License

This project is provided as-is for educational purposes.

## Credits

- **OpenAI** - GPT-4 and DALL-E 3
- **ElevenLabs** - Text-to-speech AI
- **MoviePy** - Video editing
- **Flask** - Web framework

## Support

For issues and questions, please check:
- OpenAI API documentation: https://platform.openai.com/docs
- ElevenLabs documentation: https://elevenlabs.io/docs
- MoviePy documentation: https://zulko.github.io/moviepy/

---

**Made with ❤️ using AI**
