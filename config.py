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

# Voice Types (ElevenLabs voices)
VOICE_TYPES = {
    'Zara': 'XB0fDUnXU5powFXDhCwa',      # The Warm, Real-World (Social Media)
    'Shelby': 'EXAVITQu4vr4xnSDxMaL',    # Conversational
    'James': 'ZQe5CZNOzWyzPSCn5a3c',     # British Professional (Informative & Educational)
    'B.Giffen': 'N2lVS1w4EtoT3dr4eOWO',  # Audiobook Narrator (Narrative & Story)
    'Adam': 'pNInz6obpgDQGcFmaJgB',      # Conversational
    'Lulu Lollipop': 'EXAVITQu4vr4xnSDxMaL'  # Sweet & Bubbly (Engaging & Animated)
}

# Create directories
for directory in [OUTPUT_DIR, TEMP_DIR, VIDEOS_DIR, IMAGES_DIR, AUDIO_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
