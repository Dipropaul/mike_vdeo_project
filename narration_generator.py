"""
Narration Generator Module
Handles text-to-speech conversion using ElevenLabs API with OpenAI TTS fallback
"""
import os
from pathlib import Path
try:
    from elevenlabs.client import ElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
import openai
import config


class NarrationGenerator:
    """Generate narration audio from text using ElevenLabs with OpenAI TTS fallback"""
    
    def __init__(self):
        """Initialize the narration generator"""
        self.use_elevenlabs = ELEVENLABS_AVAILABLE and bool(config.ELEVENLABS_API_KEY)
        if self.use_elevenlabs:
            self.elevenlabs_client = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)
        if config.OPENAI_API_KEY:
            openai.api_key = config.OPENAI_API_KEY
        self.voices = config.VOICE_TYPES
    
    def generate_narration(self, script: str, voice_name: str = 'Bella') -> Path:
        """
        Generate narration from script
        
        Args:
            script: The text to convert to speech
            voice_name: Name of the voice to use
            
        Returns:
            Path to the generated audio file
        """
        # Try ElevenLabs first if API key is available
        if self.use_elevenlabs:
            try:
                return self._generate_with_elevenlabs(script, voice_name)
            except Exception as e:
                print(f"ElevenLabs failed: {e}")
                print("Falling back to OpenAI TTS...")
        
        # Fallback to OpenAI TTS
        return self._generate_with_openai(script, voice_name)
    
    def _generate_with_elevenlabs(self, script: str, voice_name: str) -> Path:
        """Generate narration using ElevenLabs"""
        # Get voice ID - use default if voice not found
        if voice_name not in self.voices:
            print(f"Voice '{voice_name}' not found, using default 'Zara'")
            voice_name = 'Zara'
        
        voice_id = self.voices[voice_name]
        
        # Generate audio
        print(f"Generating narration with ElevenLabs ({voice_name} voice, ID: {voice_id})...")
        
        # Use the correct ElevenLabs API method with turbo v2.5 for better quality
        audio = self.elevenlabs_client.text_to_speech.convert(
            voice_id=voice_id,
            text=script,
            model_id="eleven_turbo_v2_5"
        )
        
        # Save audio file
        output_path = config.AUDIO_DIR / f"narration_{voice_name}_elevenlabs.mp3"
        
        # Convert generator to bytes and save
        with open(output_path, 'wb') as f:
            for chunk in audio:
                f.write(chunk)
        
        print(f"Narration saved to {output_path}")
        return output_path
    
    def _generate_with_openai(self, script: str, voice_name: str) -> Path:
        """Generate narration using OpenAI TTS as fallback"""
        # Map voice names to OpenAI voices (6 available: alloy, echo, fable, onyx, nova, shimmer)
        openai_voices = {
            'Zara': 'nova',
            'Shelby': 'shimmer',
            'James': 'onyx',
            'B.Giffen': 'fable',
            'Adam': 'echo',
            'Lulu Lollipop': 'alloy'
        }
        
        openai_voice = openai_voices.get(voice_name, 'nova')
        
        print(f"Generating narration with OpenAI TTS ({openai_voice} voice)...")
        
        response = openai.audio.speech.create(
            model="tts-1",
            voice=openai_voice,
            input=script
        )
        
        # Save audio file
        output_path = config.AUDIO_DIR / f"narration_{voice_name}_openai.mp3"
        response.stream_to_file(str(output_path))
        
        print(f"Narration saved to {output_path}")
        return output_path
    
    def get_available_voices(self) -> list:
        """Get list of available voice names"""
        return list(self.voices.keys())


if __name__ == "__main__":
    # Test the narration generator
    generator = NarrationGenerator()
    test_script = "This is a test narration. ClipForge can generate amazing videos with AI."
    audio_path = generator.generate_narration(test_script)
    print(f"Test narration generated: {audio_path}")
