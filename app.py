"""
ClipForge - AI Video Generation Web Application
Main FastAPI application
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from pathlib import Path
import config
from pipeline import VideoGeneratorPipeline
import uuid
import threading
from typing import Optional

app = FastAPI(title="ClipForge", description="AI Video Generation System", version="1.0.0")

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:*",
        "http://127.0.0.1:*",
        "http://0.0.0.0:*",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "*"  # Allow all for development
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    print(f"Validation error: {errors}")
    error_messages = []
    for error in errors:
        field = ' -> '.join(str(x) for x in error['loc'])
        message = error['msg']
        error_messages.append(f"{field}: {message}")
    
    return JSONResponse(
        status_code=400,
        content={
            "error": "Validation failed",
            "details": error_messages,
            "body": exc.body
        }
    )

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Initialize pipeline
pipeline = VideoGeneratorPipeline()

# Store for tracking video generation jobs
jobs = {}


# Pydantic models
class VideoRequest(BaseModel):
    title: str
    category: str
    format: str
    style: str
    voice: str
    script: str
    keywords: Optional[str] = ''
    negative_keywords: Optional[str] = ''


@app.get("/")
async def index(request: Request):
    """Render main page"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "video_formats": list(config.VIDEO_FORMATS.keys()),
        "video_styles": config.VIDEO_STYLES,
        "voice_types": list(config.VOICE_TYPES.keys())
    })


@app.get("/videos")
async def videos_page(request: Request):
    """Render all videos page"""
    videos = pipeline.get_all_videos()
    return templates.TemplateResponse("videos.html", {
        "request": request,
        "videos": videos,
        "video_count": len(videos)
    })


@app.post("/api/create-video")
async def create_video(video_data: VideoRequest, background_tasks: BackgroundTasks):
    """Create a new video from request data"""
    try:
        # Log incoming request
        print(f"Received video request: {video_data.dict()}")
        print(f"Script length: {len(video_data.script)}, Max allowed: {config.MAX_SCRIPT_LENGTH}")
        
        # Validate script length
        if len(video_data.script) > config.MAX_SCRIPT_LENGTH:
            print(f"Script too long! {len(video_data.script)} > {config.MAX_SCRIPT_LENGTH}")
            raise HTTPException(
                status_code=400,
                detail=f'Script too long. Maximum {config.MAX_SCRIPT_LENGTH} characters'
            )
        
        # Create job ID
        job_id = str(uuid.uuid4())
        jobs[job_id] = {
            'status': 'processing',
            'progress': 0,
            'message': 'Starting video generation...'
        }
        
        # Start video generation in background thread
        def generate_video_async():
            try:
                jobs[job_id]['message'] = 'Generating narration...'
                jobs[job_id]['progress'] = 10
                
                result = pipeline.generate_video(video_data.dict())
                
                jobs[job_id]['status'] = 'completed'
                jobs[job_id]['progress'] = 100
                jobs[job_id]['message'] = 'Video generation complete!'
                jobs[job_id]['video'] = result
                
            except Exception as e:
                jobs[job_id]['status'] = 'failed'
                jobs[job_id]['message'] = f'Error: {str(e)}'
        
        thread = threading.Thread(target=generate_video_async)
        thread.daemon = True
        thread.start()
        
        return JSONResponse(
            content={'job_id': job_id, 'message': 'Video generation started'},
            status_code=202
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/job-status/{job_id}')
async def job_status(job_id: str):
    """Check status of a video generation job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail='Job not found')
    
    return JSONResponse(content=jobs[job_id])


@app.get('/api/all-videos')
async def all_videos():
    """Get all generated videos"""
    videos = pipeline.get_all_videos()
    return JSONResponse(content=videos)


@app.get('/api/video/{video_id}')
async def get_video(video_id: int):
    """Get specific video by ID"""
    video = pipeline.db.get_video(video_id)
    
    if not video:
        raise HTTPException(status_code=404, detail='Video not found')
    
    return JSONResponse(content=video)


@app.delete('/api/video/{video_id}')
async def delete_video(video_id: int):
    """Delete a video by ID"""
    video = pipeline.db.get_video(video_id)
    
    if not video:
        raise HTTPException(status_code=404, detail='Video not found')
    
    # Delete video file
    video_path = Path(video['path'])
    if video_path.exists():
        video_path.unlink()
    
    # Delete from database
    pipeline.db.delete_video(video_id)
    
    return JSONResponse(content={'message': 'Video deleted successfully'})


@app.get('/api/download/{video_id}')
async def download_video(video_id: int):
    """Download video file"""
    videos = pipeline.get_all_videos()
    video = next((v for v in videos if v['id'] == video_id), None)
    
    if not video:
        raise HTTPException(status_code=404, detail='Video not found')
    
    video_path = Path(video['path'])
    if not video_path.exists():
        raise HTTPException(status_code=404, detail='Video file not found')
    
    return FileResponse(
        path=video_path,
        media_type='video/mp4',
        filename=video_path.name
    )


@app.get('/api/config')
async def get_config():
    """
    Get Application Configuration
    
    Returns all available options for video generation including:
    - Video formats (9:16, 16:9, 1:1)
    - Video styles (art styles for image generation)
    - Voice types (available AI voices)
    - Configuration limits
    """
    return JSONResponse(content={
        'video_formats': list(config.VIDEO_FORMATS.keys()),
        'video_styles': config.VIDEO_STYLES,
        'voice_types': list(config.VOICE_TYPES.keys()),
        'max_script_length': config.MAX_SCRIPT_LENGTH,
        'image_count': config.IMAGE_COUNT
    })


@app.get('/api/styles', 
    summary="Get Available Video Styles",
    description="Returns a list of all available video styles for image generation",
    response_description="List of style names",
    tags=["Configuration"]
)
async def get_styles():
    """
    Get Available Video Styles
    
    Returns all available art styles that can be used for video generation.
    These styles determine the visual appearance of generated images.
    
    **Returns:**
    - List of style names (e.g., "Realistic Action Art", "Modern Abstract", etc.)
    """
    return JSONResponse(content={
        'styles': config.VIDEO_STYLES,
        'count': len(config.VIDEO_STYLES)
    })


@app.get('/api/voices',
    summary="Get Available AI Voices",
    description="Returns a list of all available AI voices for narration",
    response_description="Dictionary of voice names and their IDs",
    tags=["Configuration"]
)
async def get_voices():
    """
    Get Available AI Voices
    
    Returns all available AI voices that can be used for video narration.
    Includes both ElevenLabs voice IDs and OpenAI TTS fallback voices.
    
    **Voice Types:**
    - Male voices: Roger, Charlie, George, James, Callum, etc.
    - Female voices: Sarah, Laura, Jessica, Matilda, Alice, etc.
    - Neutral voices: River
    
    **Returns:**
    - Dictionary with voice names as keys and ElevenLabs voice IDs as values
    - Total count of available voices
    """
    return JSONResponse(content={
        'voices': list(config.VOICE_TYPES.keys()),
        'voice_details': config.VOICE_TYPES,
        'count': len(config.VOICE_TYPES)
    })


@app.get('/api/formats',
    summary="Get Available Video Formats",
    description="Returns all supported video aspect ratios",
    response_description="Dictionary of format names and dimensions",
    tags=["Configuration"]
)
async def get_formats():
    """
    Get Available Video Formats
    
    Returns all supported video aspect ratios and their dimensions.
    
    **Available Formats:**
    - 9:16 (1080x1920) - Vertical format for TikTok, Instagram Reels, YouTube Shorts
    - 16:9 (1920x1080) - Horizontal format for YouTube, traditional videos
    - 1:1 (1080x1080) - Square format for Instagram posts, Facebook
    
    **Returns:**
    - Dictionary with format names as keys and (width, height) tuples as values
    """
    return JSONResponse(content={
        'formats': {k: {'width': v[0], 'height': v[1]} for k, v in config.VIDEO_FORMATS.items()},
        'count': len(config.VIDEO_FORMATS)
    })


if __name__ == '__main__':
    import uvicorn
    print(f"\n{'='*60}")
    print(f"ClipForge - AI Video Generation System (FastAPI)")
    print(f"{'='*60}")
    print(f"Server starting on http://{config.HOST}:{config.PORT}")
    print(f"API docs available at http://{config.HOST}:{config.PORT}/docs")
    print(f"{'='*60}\n")
    
    uvicorn.run(
        "app:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG
    )
