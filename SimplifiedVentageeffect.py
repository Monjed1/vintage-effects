import os
import cv2
import numpy as np
import random
import tempfile
from moviepy.editor import VideoFileClip, concatenate_videoclips
from skimage.util import random_noise

def process_video_frames(input_path, output_path, effect_function, intensity=0.5, audio=True):
    """
    Simplified function for applying effects to videos
    """
    try:
        # Just call the effect function directly
        effect_function(input_path, output_path, intensity)
    except Exception as e:
        raise Exception(f"Error processing video: {str(e)}")

# VHS Effect
def apply_vhs_effect(input_path, output_path, intensity=0.5):
    try:
        # Load the video
        clip = VideoFileClip(input_path)
        
        # Process frames using a simple lambda that doesn't use the fl_image method
        # This avoids the attribute error
        frames = []
        duration = clip.duration
        fps = clip.fps
        
        # Extract frames at specific times and process them
        for t in np.arange(0, duration, 1/fps):
            if t > duration:
                break
            
            # Get the frame at time t
            frame = clip.get_frame(t)
            
            # Apply VHS effect
            frame_float = frame.astype(np.float32) / 255.0
            
            # RGB shift
            height, width = frame.shape[:2]
            shift_amount = int(7 * intensity)
            
            # Create result frame
            result = frame_float.copy()
            
            # Apply red shift
            if shift_amount > 0:
                result[:, shift_amount:, 0] = frame_float[:, :-shift_amount, 0]
            
            # Apply blue shift
            if shift_amount > 0:
                result[:, :-shift_amount, 2] = frame_float[:, shift_amount:, 2]
            
            # Add noise
            noise_level = 0.08 * intensity
            noise = np.random.normal(0, noise_level, frame_float.shape)
            result = np.clip(result + noise, 0, 1)
            
            # Convert back to uint8
            processed_frame = (result * 255).astype(np.uint8)
            frames.append(processed_frame)
        
        # Create a new clip from the processed frames
        from moviepy.editor import ImageSequenceClip
        processed_clip = ImageSequenceClip(frames, fps=fps)
        
        # Write output
        if clip.audio is not None and audio:
            processed_clip = processed_clip.set_audio(clip.audio)
            
        processed_clip.write_videofile(output_path, codec='libx264')
        
        # Clean up
        clip.close()
        processed_clip.close()
        
    except Exception as e:
        raise Exception(f"Error in VHS effect: {str(e)}")

# Film Grain Effect - Simplified
def apply_film_grain(input_path, output_path, intensity=0.5):
    try:
        # Load the video
        clip = VideoFileClip(input_path)
        
        frames = []
        duration = clip.duration
        fps = clip.fps
        
        # Extract frames at specific times and process them
        for t in np.arange(0, duration, 1/fps):
            if t > duration:
                break
            
            # Get the frame at time t
            frame = clip.get_frame(t)
            
            # Apply film grain effect
            frame_float = frame.astype(np.float32) / 255.0
            
            # Add film grain noise
            grain_intensity = 0.2 * intensity
            grain = random_noise(frame_float, mode='gaussian', var=grain_intensity**2)
            
            # Convert back to uint8
            processed_frame = (grain * 255).astype(np.uint8)
            frames.append(processed_frame)
        
        # Create a new clip from the processed frames
        from moviepy.editor import ImageSequenceClip
        processed_clip = ImageSequenceClip(frames, fps=fps)
        
        # Write output
        if clip.audio is not None:
            processed_clip = processed_clip.set_audio(clip.audio)
            
        processed_clip.write_videofile(output_path, codec='libx264')
        
        # Clean up
        clip.close()
        processed_clip.close()
        
    except Exception as e:
        raise Exception(f"Error in Film Grain effect: {str(e)}")

# Light Leak Effect - Simplified
def apply_light_leak(input_path, output_path, intensity=0.5):
    try:
        # Load the video
        clip = VideoFileClip(input_path)
        
        frames = []
        duration = clip.duration
        fps = clip.fps
        
        # Extract frames at specific times and process them
        for t in np.arange(0, duration, 1/fps):
            if t > duration:
                break
            
            # Get the frame at time t
            frame = clip.get_frame(t)
            
            # Apply light leak effect
            h, w = frame.shape[:2]
            frame_float = frame.astype(np.float32) / 255.0
            
            # Create a simple light leak (just a red/yellow overlay in the corner)
            mask = np.zeros((h, w), dtype=np.float32)
            center_x, center_y = int(w * 0.7), int(h * 0.3)  # Top right area
            for y in range(h):
                for x in range(w):
                    dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                    mask[y, x] = max(0, 1 - dist / (w * 0.5))
            
            # Apply the colored light leak
            result = frame_float.copy()
            result[:, :, 0] += mask * 0.1 * intensity  # Blue - slight
            result[:, :, 1] += mask * 0.3 * intensity  # Green - medium
            result[:, :, 2] += mask * 0.5 * intensity  # Red - strongest
            
            # Ensure values are in valid range
            result = np.clip(result, 0, 1)
            
            # Convert back to uint8
            processed_frame = (result * 255).astype(np.uint8)
            frames.append(processed_frame)
        
        # Create a new clip from the processed frames
        from moviepy.editor import ImageSequenceClip
        processed_clip = ImageSequenceClip(frames, fps=fps)
        
        # Write output
        if clip.audio is not None:
            processed_clip = processed_clip.set_audio(clip.audio)
            
        processed_clip.write_videofile(output_path, codec='libx264')
        
        # Clean up
        clip.close()
        processed_clip.close()
        
    except Exception as e:
        raise Exception(f"Error in Light Leak effect: {str(e)}")

# Old Movie Effect (Simplified)
def apply_old_movie(input_path, output_path, intensity=0.5):
    apply_sepia(input_path, output_path, intensity)

# Sepia Tone Effect
def apply_sepia(input_path, output_path, intensity=0.5):
    try:
        # Load the video
        clip = VideoFileClip(input_path)
        
        frames = []
        duration = clip.duration
        fps = clip.fps
        
        # Extract frames at specific times and process them
        for t in np.arange(0, duration, 1/fps):
            if t > duration:
                break
            
            # Get the frame at time t
            frame = clip.get_frame(t)
            
            # Apply sepia effect
            # Original colors in RGB (MoviePy uses RGB)
            original = frame.astype(np.float32) / 255.0
            
            # Create sepia tone (RGB order)
            sepia = np.zeros_like(original)
            sepia[:, :, 0] = (original[:, :, 0] * 0.393 + original[:, :, 1] * 0.769 + original[:, :, 2] * 0.189)  # R
            sepia[:, :, 1] = (original[:, :, 0] * 0.349 + original[:, :, 1] * 0.686 + original[:, :, 2] * 0.168)  # G
            sepia[:, :, 2] = (original[:, :, 0] * 0.272 + original[:, :, 1] * 0.534 + original[:, :, 2] * 0.131)  # B
            
            # Blend original and sepia based on intensity
            result = original * (1 - intensity) + sepia * intensity
            
            # Convert back to uint8
            processed_frame = (result * 255).astype(np.uint8)
            frames.append(processed_frame)
        
        # Create a new clip from the processed frames
        from moviepy.editor import ImageSequenceClip
        processed_clip = ImageSequenceClip(frames, fps=fps)
        
        # Write output
        if clip.audio is not None:
            processed_clip = processed_clip.set_audio(clip.audio)
            
        processed_clip.write_videofile(output_path, codec='libx264')
        
        # Clean up
        clip.close()
        processed_clip.close()
        
    except Exception as e:
        raise Exception(f"Error in Sepia effect: {str(e)}")

# CRT Scanlines, Vintage Color, and Glitch Effect
# For simplicity, just redirect these to simpler effects
def apply_crt_scanlines(input_path, output_path, intensity=0.5):
    apply_film_grain(input_path, output_path, intensity)

def apply_vintage_color(input_path, output_path, intensity=0.5):
    apply_sepia(input_path, output_path, intensity)

def apply_glitch(input_path, output_path, intensity=0.5):
    apply_vhs_effect(input_path, output_path, intensity) 