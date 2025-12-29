"""
Video Composer Module
Combines images and narration into a video with effects
"""
from pathlib import Path
from typing import List, Dict
import random
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, TextClip
import numpy as np
from PIL import Image, ImageFont, ImageDraw
import config
import textwrap
import math
from subtitle_generator import SubtitleGenerator


class VideoComposer:
    """Compose final video from images and audio"""
    
    def __init__(self):
        """Initialize the video composer"""
        self.fps = config.DEFAULT_FPS
        self.subtitle_gen = SubtitleGenerator()
    
    def _make_zoom_in_effect(self, duration):
        """Create smooth zoom in effect function with enhanced easing"""
        def effect(get_frame, t):
            frame = get_frame(t)
            h, w = frame.shape[:2]
            
            # Calculate zoom factor with smooth easing (1.0 to 1.35) - more dynamic
            progress = t / duration
            # Apply quartic ease-in-out for ultra smooth cinematic motion
            if progress < 0.5:
                eased_progress = 8 * progress * progress * progress * progress
            else:
                eased_progress = 1 - pow(-2 * progress + 2, 4) / 2
            zoom = 1.0 + (eased_progress * 0.35)  # Increased to 35% for more impact
            
            # Calculate crop coordinates for zoom
            new_h, new_w = int(h / zoom), int(w / zoom)
            y1, x1 = (h - new_h) // 2, (w - new_w) // 2
            y2, x2 = y1 + new_h, x1 + new_w
            
            # Crop and resize back with high quality
            cropped = frame[y1:y2, x1:x2]
            img = Image.fromarray(cropped)
            img_resized = img.resize((w, h), Image.Resampling.LANCZOS)
            return np.array(img_resized)
        return effect
    
    def _make_zoom_out_effect(self, duration):
        """Create smooth zoom out effect function with enhanced easing"""
        def effect(get_frame, t):
            frame = get_frame(t)
            h, w = frame.shape[:2]
            
            # Calculate zoom factor (1.35 to 1.0) with smooth easing - more dynamic
            progress = t / duration
            # Apply quartic ease-in-out for ultra smooth cinematic motion
            if progress < 0.5:
                eased_progress = 8 * progress * progress * progress * progress
            else:
                eased_progress = 1 - pow(-2 * progress + 2, 4) / 2
            zoom = 1.35 - (eased_progress * 0.35)  # Increased to 35% for more impact
            
            # Calculate crop coordinates for zoom
            new_h, new_w = int(h / zoom), int(w / zoom)
            y1, x1 = (h - new_h) // 2, (w - new_w) // 2
            y2, x2 = y1 + new_h, x1 + new_w
            
            # Crop and resize back with high quality
            cropped = frame[y1:y2, x1:x2]
            img = Image.fromarray(cropped)
            img_resized = img.resize((w, h), Image.Resampling.LANCZOS)
            return np.array(img_resized)
        return effect
    
    def _make_pan_effect(self, duration):
        """Create smooth diagonal pan effect function with enhanced motion"""
        def effect(get_frame, t):
            frame = get_frame(t)
            h, w = frame.shape[:2]
            
            # Diagonal pan with quartic easing - ultra smooth cinematic motion
            progress = t / duration
            # Apply quartic ease-in-out
            if progress < 0.5:
                eased_progress = 8 * progress * progress * progress * progress
            else:
                eased_progress = 1 - pow(-2 * progress + 2, 4) / 2
            
            # Horizontal shift (increased to 18%)
            h_shift = int(w * 0.18 * (eased_progress - 0.5))
            # Vertical shift for diagonal effect (8%)
            v_shift = int(h * 0.08 * (eased_progress - 0.5))
            
            # Apply horizontal pan
            if h_shift > 0:
                frame = np.pad(frame, ((0, 0), (h_shift, 0), (0, 0)), mode='edge')[:, :w]
            elif h_shift < 0:
                frame = np.pad(frame, ((0, 0), (0, -h_shift), (0, 0)), mode='edge')[:, -w:]
            
            # Apply vertical pan
            if v_shift > 0:
                frame = np.pad(frame, ((v_shift, 0), (0, 0), (0, 0)), mode='edge')[:h, :]
            elif v_shift < 0:
                frame = np.pad(frame, ((0, -v_shift), (0, 0), (0, 0)), mode='edge')[-h:, :]
            
            return frame
        return effect
    
    def _make_rotate_zoom_effect(self, duration):
        """Create smooth rotate + zoom effect for cinematic feel"""
        def effect(get_frame, t):
            frame = get_frame(t)
            h, w = frame.shape[:2]
            
            # Progress with quartic easing
            progress = t / duration
            if progress < 0.5:
                eased = 8 * progress * progress * progress * progress
            else:
                eased = 1 - pow(-2 * progress + 2, 4) / 2
            
            # Subtle rotation (-2° to +2°) + zoom (1.0 to 1.25)
            angle = (eased - 0.5) * 4  # -2 to +2 degrees
            zoom = 1.0 + (eased * 0.25)
            
            # Use PIL for rotation and zoom
            img = Image.fromarray(frame)
            
            # Calculate new dimensions after zoom
            new_w, new_h = int(w * zoom), int(h * zoom)
            
            # Zoom first
            img_zoomed = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # Rotate with expand to prevent cropping
            img_rotated = img_zoomed.rotate(angle, resample=Image.Resampling.BICUBIC, expand=False, fillcolor=(0, 0, 0))
            
            # Crop back to original size (center crop)
            left = (img_rotated.width - w) // 2
            top = (img_rotated.height - h) // 2
            img_cropped = img_rotated.crop((left, top, left + w, top + h))
            
            return np.array(img_cropped)
        return effect
    
    def __init__(self):
        """Initialize the video composer"""
        self.fps = config.DEFAULT_FPS
        self.subtitle_gen = SubtitleGenerator()
    
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
            
            # Concatenate all clips with smooth transitions
            print("Combining clips...")
            final_video = concatenate_videoclips(clips, method="compose")
            
            # Add AI-powered subtitles
            if script and config.ENABLE_SUBTITLES:
                print("Generating AI-powered subtitles...")
                final_video = self._add_ai_subtitles(final_video, script, width, height, total_duration, len(image_paths))
            
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
            
            # Apply random animation effect for reels with varied intensity
            effect_functions = [
                self._make_zoom_in_effect(duration),
                self._make_zoom_out_effect(duration),
                self._make_pan_effect(duration),
                self._make_rotate_zoom_effect(duration),
                # Add zoom in twice for higher probability of zoom effects
                self._make_zoom_in_effect(duration),
            ]
            effect = random.choice(effect_functions)
            
            # Apply slight speed variation (0.95x to 1.05x) for organic feel
            speed_factor = random.uniform(0.95, 1.05)
            
            # Apply the effect using transform
            animated_clip = cropped.transform(effect)
            
            # Apply speed variation
            try:
                if speed_factor != 1.0:
                    animated_clip = animated_clip.with_fps(self.fps * speed_factor)
            except:
                pass  # Skip speed variation if it fails
            
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
    
    def _add_ai_subtitles(self, video_clip, script: str, width: int, 
                          height: int, duration: float, num_images: int):
        """
        Add AI-generated subtitles to video with professional styling
        
        Args:
            video_clip: The video clip to add subtitles to
            script: The video script
            width: Video width
            height: Video height
            duration: Video duration
            num_images: Number of images/scenes
            
        Returns:
            Video clip with subtitles
        """
        try:
            # Generate subtitle segments using AI
            subtitle_segments = self.subtitle_gen.generate_subtitle_segments(
                script, duration, num_images
            )
            
            if not subtitle_segments:
                print("No subtitle segments generated")
                return video_clip
            
            # Export SRT file for reference
            srt_path = config.TEMP_DIR / "subtitles.srt"
            self.subtitle_gen.export_srt(subtitle_segments, str(srt_path))
            
            # Create subtitle clips with professional styling
            subtitle_clips = []
            
            for segment in subtitle_segments:
                text = segment['text']
                start_time = segment['start_time']
                end_time = segment['end_time']
                duration_seg = end_time - start_time
                
                if duration_seg <= 0:
                    continue
                
                # Create subtitle clip with enhanced styling
                txt_clip = self._create_styled_subtitle(
                    text, width, height, duration_seg, start_time
                )
                
                if txt_clip:
                    subtitle_clips.append(txt_clip)
            
            # Composite subtitles onto video
            if subtitle_clips:
                print(f"Adding {len(subtitle_clips)} subtitle segments to video...")
                video_with_subs = CompositeVideoClip([video_clip] + subtitle_clips)
                return video_with_subs
            else:
                print("No subtitle clips were created successfully, proceeding without subtitles...")
                return video_clip
                
        except Exception as e:
            print(f"Error adding AI subtitles: {e}")
            import traceback
            traceback.print_exc()
            return video_clip
    
    def _create_styled_subtitle(self, text: str, video_width: int, 
                                video_height: int, duration: float, 
                                start_time: float):
        """
        Create a professionally styled subtitle clip
        
        Args:
            text: Subtitle text
            video_width: Video width
            video_height: Video height
            duration: Subtitle duration
            start_time: When subtitle appears
            
        Returns:
            Styled TextClip or None
        """
        try:
            # Calculate font size based on video height
            font_size = int(video_height * config.SUBTITLE_FONT_SIZE_RATIO)
            
            # Wrap text to fit screen width (80% of width)
            max_chars_per_line = int(video_width * 0.8 / (font_size * 0.6))
            wrapped_text = textwrap.fill(text, width=max_chars_per_line)
            
            # Try creating text clip with label method (more compatible)
            try:
                txt_clip = TextClip(
                    text=wrapped_text,
                    font_size=font_size,
                    color=config.SUBTITLE_COLOR,
                    stroke_color=config.SUBTITLE_STROKE_COLOR,
                    stroke_width=config.SUBTITLE_STROKE_WIDTH,
                    method='label',
                    size=(int(video_width * 0.9), None)
                )
            except Exception as e1:
                print(f"Label method failed: {e1}, trying caption method...")
                # Fallback to caption without font specification
                try:
                    txt_clip = TextClip(
                        text=wrapped_text,
                        font_size=font_size,
                        color=config.SUBTITLE_COLOR,
                        method='caption',
                        size=(int(video_width * 0.9), None),
                        text_align='center'
                    )
                except Exception as e2:
                    print(f"Caption method failed: {e2}")
                    return None
            
            if txt_clip is None:
                return None
            
            # Set duration and start time
            txt_clip = txt_clip.with_duration(duration).with_start(start_time)
            
            # Position subtitle at bottom with padding (ensure it's visible)
            padding_pixels = int(video_height * config.SUBTITLE_BOTTOM_PADDING)
            y_position = max(video_height - txt_clip.size[1] - padding_pixels, int(video_height * 0.6))
            txt_clip = txt_clip.with_position(('center', y_position))
            
            # Add fade in/out effects for smooth appearance (if available)
            fade_duration = min(0.3, duration / 4)
            try:
                txt_clip = txt_clip.fadein(fade_duration).fadeout(fade_duration)
            except AttributeError:
                # Fade methods not available, skip fade effects
                pass
            
            return txt_clip
            
        except Exception as e:
            print(f"Error creating subtitle clip: {e}")
            return None


if __name__ == "__main__":
    # Test the video composer
    print("VideoComposer module ready for testing")
