"""
ClipForge - AI Video Generation System
Main configuration file
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY', '')
STABILITY_API_KEY = os.getenv('STABILITY_API_KEY', '')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')

# Flask Configuration
SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))

# Directory Configuration
OUTPUT_DIR = BASE_DIR / os.getenv('OUTPUT_DIR', 'outputs')
TEMP_DIR = BASE_DIR / os.getenv('TEMP_DIR', 'temp')
VIDEOS_DIR = BASE_DIR / os.getenv('VIDEOS_DIR', 'outputs/videos')
IMAGES_DIR = BASE_DIR / os.getenv('IMAGES_DIR', 'outputs/images')
AUDIO_DIR = BASE_DIR / os.getenv('AUDIO_DIR', 'outputs/audio')

# Video Generation Settings
DEFAULT_FPS = int(os.getenv('DEFAULT_FPS', 30))
DEFAULT_DURATION_PER_IMAGE = int(os.getenv('DEFAULT_DURATION_PER_IMAGE', 5))
IMAGE_COUNT = int(os.getenv('IMAGE_COUNT', 7))
MAX_SCRIPT_LENGTH = int(os.getenv('MAX_SCRIPT_LENGTH', 1500))

# Subtitle Settings
ENABLE_SUBTITLES = os.getenv('ENABLE_SUBTITLES', 'True') == 'True'
SUBTITLE_MODEL = os.getenv('SUBTITLE_MODEL', 'gpt-4o-mini')  # AI model for subtitle segmentation
SUBTITLE_FONT = os.getenv('SUBTITLE_FONT', 'Arial')
SUBTITLE_FONT_SIZE_RATIO = float(os.getenv('SUBTITLE_FONT_SIZE_RATIO', '0.045'))  # 4.5% of video height
SUBTITLE_COLOR = os.getenv('SUBTITLE_COLOR', 'white')
SUBTITLE_STROKE_COLOR = os.getenv('SUBTITLE_STROKE_COLOR', 'black')
SUBTITLE_STROKE_WIDTH = int(os.getenv('SUBTITLE_STROKE_WIDTH', '3'))
SUBTITLE_BOTTOM_PADDING = float(os.getenv('SUBTITLE_BOTTOM_PADDING', '0.20'))  # 20% from bottom

# Video Formats
VIDEO_FORMATS = {
    '9:16': (1080, 1920),  # Vertical (TikTok, Reels)
    '16:9': (1920, 1080),  # Horizontal (YouTube)
    '1:1': (1080, 1080)    # Square (Instagram)
}

# Video Styles
VIDEO_STYLES = [
    'Realistic Action Art',
    'B&W Sketch',
    'Comic Noir',
    'Retro Noir',
    'Medieval Painting',
    'Anime',
    'Warm Fable',
    'Hyper Realistic',
    '3D Cartoon',
    'Caricature'
]

# Voice Types (ElevenLabs voices - from API)
VOICE_TYPES = {
    'Roger': 'CwhRBWXzGAHq8TQ4Fs17',      # Laid-Back, Casual, Resonant (Male)
    'Sarah': 'EXAVITQu4vr4xnSDxMaL',      # Mature, Reassuring, Confident (Female)
    'Shelby': 'EXAVITQu4vr4xnSDxMaL',     # Alias for Sarah (Conversational)
    'Laura': 'FGY2WhTYpPnrIDTdsKH5',      # Enthusiast, Quirky Attitude (Female)
    'Charlie': 'IKne3meq5aSn9XLyUdCD',    # Deep, Confident, Energetic (Male)
    'George': 'JBFqnCBsd6RMkjVDRZzb',     # Warm, Captivating Storyteller (Male)
    'James': 'JBFqnCBsd6RMkjVDRZzb',      # Alias for George (British Professional)
    'Callum': 'N2lVS1w4EtoT3dr4eOWO',     # Husky Trickster (Male)
    'B.Giffen': 'N2lVS1w4EtoT3dr4eOWO',   # Alias for Callum (Audiobook Narrator)
    'River': 'SAz9YHcvj6GT2YYXdXww',      # Relaxed, Neutral, Informative (Neutral)
    'Liam': 'TX3LPaxmHKxFdv7VOQHJ',       # Energetic, Social Media Creator (Male)
    'Alice': 'Xb7hH8MSUJpSbSDYk0k2',      # Clear, Engaging Educator (Female)
    'Matilda': 'XrExE9yKIg1WjnnlVkGX',    # Knowledgable, Professional (Female)
    'Jessica': 'cgSgspJ2msm6clMCkdW9',    # Playful, Bright, Warm (Female)
    'Lulu Lollipop': 'cgSgspJ2msm6clMCkdW9',  # Alias for Jessica (Sweet & Bubbly)
    'Eric': 'cjVigY5qzO86Huf0OWal',       # Smooth, Trustworthy (Male)
    'Chris': 'iP95p4xoKVk53GoZ742B',      # Charming, Down-to-Earth (Male)
    'Brian': 'nPczCjzI2devNBz1zQrb',      # Deep, Resonant and Comforting (Male)
    'Daniel': 'onwK4e9ZLuTAKqWW03F9',     # Steady Broadcaster (Male)
    'Lily': 'pFZP5JQG7iQjIQuC4Bku',       # Velvety Actress (Female)
    'Adam': 'pNInz6obpgDQGcFmaJgB',       # Dominant, Firm (Male)
    'Bill': 'pqHfZKP75CvOlQylNhV4'        # Wise, Mature, Balanced (Male)
}

# Create directories
for directory in [OUTPUT_DIR, TEMP_DIR, VIDEOS_DIR, IMAGES_DIR, AUDIO_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
