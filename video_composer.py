"""
Video Composer Module
Combines images and narration into a video with effects
"""
from pathlib import Path
from typing import List
import random
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, TextClip
import numpy as np
from PIL import Image
import config
import textwrap


class VideoComposer:
    """Compose final video from images and audio"""
    
    def __init__(self):
        """Initialize the video composer"""
        self.fps = config.DEFAULT_FPS
    
    def _make_zoom_in_effect(self, duration):
        """Create zoom in effect function"""
        def effect(get_frame, t):
            frame = get_frame(t)
            h, w = frame.shape[:2]
            
            # Calculate zoom factor (1.0 to 1.3)
            progress = t / duration
            zoom = 1.0 + (progress * 0.3)
            
            # Calculate crop coordinates for zoom
            new_h, new_w = int(h / zoom), int(w / zoom)
            y1, x1 = (h - new_h) // 2, (w - new_w) // 2
            y2, x2 = y1 + new_h, x1 + new_w
            
            # Crop and resize back
            cropped = frame[y1:y2, x1:x2]
            img = Image.fromarray(cropped)
            img_resized = img.resize((w, h), Image.Resampling.LANCZOS)
            return np.array(img_resized)
        return effect
    
    def _make_zoom_out_effect(self, duration):
        """Create zoom out effect function"""
        def effect(get_frame, t):
            frame = get_frame(t)
            h, w = frame.shape[:2]
            
            # Calculate zoom factor (1.3 to 1.0)
            progress = t / duration
            zoom = 1.3 - (progress * 0.3)
            
            # Calculate crop coordinates for zoom
            new_h, new_w = int(h / zoom), int(w / zoom)
            y1, x1 = (h - new_h) // 2, (w - new_w) // 2
            y2, x2 = y1 + new_h, x1 + new_w
            
            # Crop and resize back
            cropped = frame[y1:y2, x1:x2]
            img = Image.fromarray(cropped)
            img_resized = img.resize((w, h), Image.Resampling.LANCZOS)
            return np.array(img_resized)
        return effect
    
    def _make_pan_effect(self, duration):
        """Create pan effect function"""
        def effect(get_frame, t):
            frame = get_frame(t)
            h, w = frame.shape[:2]
            
            # Pan horizontally
            progress = t / duration
            shift = int(w * 0.1 * (progress - 0.5))
            
            if shift > 0:
                # Pan right
                frame = np.pad(frame, ((0, 0), (shift, 0), (0, 0)), mode='edge')[:, :w]
            else:
                # Pan left
                frame = np.pad(frame, ((0, 0), (0, -shift), (0, 0)), mode='edge')[:, -w:]
            
            return frame
        return effect
        """Initialize the video composer"""
        self.fps = config.DEFAULT_FPS
    
    def create_video(self, image_paths: List[Path], audio_path: Path,
                     video_format: str = '16:9', 
                     video_title: str = 'output',
                     script: str = '') -> Path:
        """
        Create video from images and audio with subtitles
        
        Args:
            image_paths: List of image file paths
            audio_path: Path to audio file
            video_format: Video aspect ratio (9:16, 16:9, 1:1)
            video_title: Title for output video file
            script: Script text for subtitles
            
        Returns:
            Path to the generated video
        """
        try:
            print(f"Creating video with {len(image_paths)} images...")
            
            # Load audio
            audio = AudioFileClip(str(audio_path))
            total_duration = audio.duration
            
            # Calculate duration per image
            duration_per_image = total_duration / len(image_paths)
            
            # Get video dimensions
            width, height = config.VIDEO_FORMATS[video_format]
            
            # Create video clips with effects
            clips = []
            for i, img_path in enumerate(image_paths):
                print(f"Processing image {i+1}/{len(image_paths)}...")
                
                # Load and resize image using PIL
                img = Image.open(str(img_path))
                img_width, img_height = img.size
                
                # Calculate resize to maintain aspect ratio
                aspect_ratio = img_width / img_height
                target_aspect = width / height
                
                if aspect_ratio > target_aspect:
                    # Image is wider than target
                    new_height = height
                    new_width = int(height * aspect_ratio)
                else:
                    # Image is taller than target
                    new_width = width
                    new_height = int(width / aspect_ratio)
                
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Save resized image temporarily
                temp_img_path = config.TEMP_DIR / f"temp_resized_{i}.png"
                img_resized.save(temp_img_path)
                img.close()
                
                # Create image clip from resized image
                clip = ImageClip(str(temp_img_path), duration=duration_per_image)
                
                # Apply zoom and pan effect
                clip = self._apply_zoom_pan_effect(clip, width, height, duration_per_image)
                
                clips.append(clip)
            
            # Concatenate all clips
            print("Combining clips...")
            final_video = concatenate_videoclips(clips, method="compose")
            
            # Add subtitles if script is provided
            if script:
                print("Adding subtitles...")
                final_video = self._add_subtitles(final_video, script, width, height, total_duration)
            
            # Set audio - use with_audio instead of set_audio for MoviePy 2.x
            try:
                final_video = final_video.with_audio(audio)
            except AttributeError:
                # Fallback for different MoviePy versions
                final_video.audio = audio
            
            # Ensure video matches audio duration exactly
            try:
                final_video = final_video.with_duration(total_duration)
            except AttributeError:
                final_video = final_video.set_duration(total_duration)
            
            # Generate output path
            from slugify import slugify
            safe_title = slugify(video_title)
            output_path = config.VIDEOS_DIR / f"{safe_title}.mp4"
            
            # Write video file
            print(f"Rendering final video to {output_path}...")
            final_video.write_videofile(
                str(output_path),
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=str(config.TEMP_DIR / 'temp_audio.m4a'),
                remove_temp=True,
                threads=4,
                preset='medium'
            )
            
            # Clean up
            audio.close()
            final_video.close()
            for clip in clips:
                clip.close()
            
            print(f"Video created successfully: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error creating video: {e}")
            raise
    
    def _apply_zoom_pan_effect(self, clip, target_width: int, 
                               target_height: int, duration: float):
        """
        Apply dynamic zoom/pan effects and crop to center the clip
        
        Args:
            clip: The video clip
            target_width: Target video width
            target_height: Target video height
            duration: Clip duration
            
        Returns:
            Modified clip with animations cropped to target size
        """
        # Get clip dimensions
        w, h = clip.size
        
        # Calculate center crop coordinates
        x_center = w // 2
        y_center = h // 2
        
        x1 = max(0, x_center - target_width // 2)
        y1 = max(0, y_center - target_height // 2)
        x2 = min(w, x1 + target_width)
        y2 = min(h, y1 + target_height)
        
        # Adjust if crop goes out of bounds
        if x2 - x1 < target_width:
            x1 = max(0, x2 - target_width)
        if y2 - y1 < target_height:
            y1 = max(0, y2 - target_height)
        
        # Manual crop using fl_image for MoviePy 2.x compatibility
        def crop_frame(frame):
            """Crop frame to target dimensions"""
            return frame[y1:y2, x1:x2]
        
        try:
            # Apply crop
            cropped = clip.image_transform(crop_frame)
            
            # Apply random animation effect for reels
            effect_functions = [
                self._make_zoom_in_effect(duration),
                self._make_zoom_out_effect(duration),
                self._make_pan_effect(duration)
            ]
            effect = random.choice(effect_functions)
            
            # Apply the effect using transform
            animated_clip = cropped.transform(effect)
            return animated_clip
            
        except Exception as e:
            print(f"Animation effect failed: {e}, using static crop")
            # Fallback: return cropped clip without animation
            try:
                cropped = clip.image_transform(crop_frame)
                return cropped
            except Exception as e2:
                print(f"Crop also failed: {e2}, returning original clip")
                return clip
    
    def _add_subtitles(self, video_clip, script: str, width: int, height: int, duration: float):
        """
        Add animated subtitles to video
        
        Args:
            video_clip: The video clip to add subtitles to
            script: Full script text
            width: Video width
            height: Video height
            duration: Video duration
            
        Returns:
            Video clip with subtitles
        """
        try:
            # Split script into words for dynamic display
            words = script.split()
            words_per_second = len(words) / duration
            
            # Calculate optimal words per subtitle chunk (3-5 words)
            words_per_chunk = max(3, min(5, int(words_per_second * 2)))
            
            # Create subtitle chunks
            subtitle_clips = []
            chunk_duration = duration / (len(words) / words_per_chunk)
            
            for i in range(0, len(words), words_per_chunk):
                chunk_words = words[i:i + words_per_chunk]
                text = ' '.join(chunk_words)
                
                # Wrap text if too long (use proper newline character)
                wrapped_text = '\n'.join(textwrap.wrap(text, width=35))
                
                # Calculate timing
                start_time = (i / words_per_chunk) * chunk_duration
                end_time = min(start_time + chunk_duration, duration)
                
                # Create text clip with styling for social media
                try:
                    # Calculate font size based on video dimensions (smaller for better fit)
                    font_size = int(height * 0.045)  # 4.5% of video height
                    
                    txt_clip = TextClip(
                        text=wrapped_text,
                        font_size=font_size,
                        color='white',
                        stroke_color='black',
                        stroke_width=3,
                        method='caption',
                        size=(int(width * 0.85), None)  # 85% of video width for margins
                    ).with_start(start_time).with_duration(end_time - start_time)
                    
                    # Position at bottom with safe margin to prevent cutoff
                    # For 9:16 vertical videos, position slightly higher
                    # For 16:9 horizontal videos, keep at bottom
                    if height > width:  # Vertical video (9:16)
                        y_position = int(height * 0.70)  # 70% down
                    else:  # Horizontal or square video
                        y_position = int(height * 0.80)  # 80% down
                    
                    position = ('center', y_position)
                    txt_clip = txt_clip.with_position(position)
                    
                    subtitle_clips.append(txt_clip)
                except Exception as e:
                    print(f"Warning: Could not create subtitle clip: {e}")
                    continue
            
            # Composite video with all subtitle clips
            if subtitle_clips:
                final_clip = CompositeVideoClip([video_clip] + subtitle_clips)
                return final_clip
            else:
                return video_clip
                
        except Exception as e:
            print(f"Error adding subtitles: {e}, returning video without subtitles")
            return video_clip


if __name__ == "__main__":
    # Test the video composer
    print("VideoComposer module ready for testing")
