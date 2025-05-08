import os
import cv2
import numpy as np
import random
import tempfile
from moviepy.editor import VideoFileClip, ImageSequenceClip, CompositeVideoClip, vfx, clips_array
from skimage.util import random_noise

def process_video_frames(input_path, output_path, process_frame_func, audio=True, **kwargs):
    """
    Generic function for processing video frames with a given effect function
    """
    try:
        # Load the video
        clip = VideoFileClip(input_path)
        
        # Create a wrapper function that only takes the frame argument
        def process_frame(frame):
            return process_frame_func(frame, **kwargs)
        
        # Process each frame manually instead of using fl_image
        frames = []
        for frame in clip.iter_frames():
            processed_frame = process_frame(frame)
            frames.append(processed_frame)
        
        # Create a new clip from processed frames
        fps = clip.fps
        processed_clip = ImageSequenceClip(frames, fps=fps)
        
        # Write the result to the output file
        if audio and clip.audio is not None:
            processed_clip = processed_clip.set_audio(clip.audio)
        
        processed_clip.write_videofile(output_path, codec='libx264', audio_codec='aac' if audio else None)
        
        # Close the clips to release resources
        clip.close()
        processed_clip.close()
        
    except Exception as e:
        raise Exception(f"Error processing video: {str(e)}")

# VHS Effect
def apply_vhs_effect(input_path, output_path, intensity=0.5):
    def vhs_process(frame, intensity=0.5):
        # Convert to float for processing
        frame_float = frame.astype(np.float32) / 255.0
        
        # RGB shift
        height, width = frame.shape[:2]
        shift_amount = int(7 * intensity)
        
        # Red channel shift left
        red_shifted = np.zeros_like(frame_float)
        red_shifted[:, :width-shift_amount, 0] = frame_float[:, shift_amount:, 0]
        
        # Blue channel shift right
        blue_shifted = np.zeros_like(frame_float)
        blue_shifted[:, shift_amount:, 2] = frame_float[:, :width-shift_amount, 2]
        
        # Green stays centered
        green = frame_float[:, :, 1]
        
        # Combine the channels
        result = frame_float.copy()
        result[:, :, 0] = red_shifted[:, :, 0]
        result[:, :, 2] = blue_shifted[:, :, 2]
        
        # Add some noise
        noise_level = 0.08 * intensity
        noise = np.random.normal(0, noise_level, frame_float.shape)
        result = np.clip(result + noise, 0, 1)
        
        # Add tracking lines randomly
        if random.random() < 0.2 * intensity:
            line_pos = random.randint(0, height - 1)
            line_height = random.randint(1, max(1, int(5 * intensity)))
            result[line_pos:line_pos+line_height, :, :] = np.random.uniform(0.7, 1.0)
        
        # Convert back to uint8
        return (result * 255).astype(np.uint8)
    
    process_video_frames(input_path, output_path, vhs_process, intensity=intensity)

# CRT Scanlines Effect
def apply_crt_scanlines(input_path, output_path, intensity=0.5):
    def crt_process(frame, intensity=0.5):
        h, w = frame.shape[:2]
        
        # Create scanlines
        scanlines = np.ones_like(frame)
        scanline_intensity = 0.7 - (0.3 * intensity)
        
        # Every other line is darkened
        scanlines[::2, :, :] = scanline_intensity
        
        # Apply scanlines to the frame
        result = frame.astype(np.float32) / 255.0
        result = result * scanlines
        
        # Add slight RGB shift for CRT effect
        if intensity > 0.3:
            shift = max(1, int(3 * intensity))
            # Slight RGB fringing
            result[:-shift, :, 0] = result[shift:, :, 0]  # Red channel
            result[:, :-shift, 2] = result[:, shift:, 2]  # Blue channel
        
        # Add slight curvature/distortion
        if intensity > 0.6:
            # Simple barrel distortion (not physically accurate but gives the impression)
            center_x, center_y = w // 2, h // 2
            dist_x = np.tile(np.arange(w) - center_x, (h, 1))
            dist_y = np.tile(np.arange(h) - center_y, (w, 1)).T
            dist = np.sqrt(dist_x**2 + dist_y**2)
            
            # Normalize distance to 0-1 range
            dist = dist / (np.sqrt(center_x**2 + center_y**2) * 1.1)
            
            # Create bulge effect (outward bulge)
            distortion = 0.2 * intensity * (dist**2)
            map_x = np.clip(dist_x * (1 + distortion) + center_x, 0, w - 1).astype(np.float32)
            map_y = np.clip(dist_y * (1 + distortion) + center_y, 0, h - 1).astype(np.float32)
            
            # Remap the image
            result = cv2.remap(result, map_x, map_y, cv2.INTER_LINEAR)
        
        # Convert back to uint8
        return (result * 255).astype(np.uint8)
    
    process_video_frames(input_path, output_path, crt_process, intensity=intensity)

# Film Grain Effect
def apply_film_grain(input_path, output_path, intensity=0.5):
    def film_grain_process(frame, intensity=0.5):
        # Convert to float32
        frame_float = frame.astype(np.float32) / 255.0
        
        # Add film grain noise
        grain_intensity = 0.2 * intensity
        grain = random_noise(frame_float, mode='gaussian', var=grain_intensity**2)
        
        # Add dust and scratches
        if random.random() < 0.3 * intensity:
            # Random vertical scratches
            scratch_count = int(random.uniform(1, 5) * intensity)
            for _ in range(scratch_count):
                x = random.randint(0, frame.shape[1] - 1)
                width = random.randint(1, max(1, int(3 * intensity)))
                length = random.randint(int(frame.shape[0] * 0.3), frame.shape[0])
                y_start = random.randint(0, frame.shape[0] - length)
                
                # White scratch
                grain[y_start:y_start+length, x:x+width, :] = 1.0
        
        # Random dust spots
        dust_intensity = intensity * 30
        dust_count = int(dust_intensity)
        for _ in range(dust_count):
            x = random.randint(0, frame.shape[1] - 1)
            y = random.randint(0, frame.shape[0] - 1)
            radius = random.randint(1, max(1, int(4 * intensity)))
            color = random.choice([0.0, 1.0])  # Black or white dust spots
            
            cv2.circle(grain, (x, y), radius, (color, color, color), -1)
        
        # Apply a soft contrast enhancement typical of film
        grain = np.clip((grain - 0.5) * (1 + 0.2 * intensity) + 0.5, 0, 1)
        
        # Convert back to uint8
        return (grain * 255).astype(np.uint8)
    
    process_video_frames(input_path, output_path, film_grain_process, intensity=intensity)

# Old Movie Projector Effect
def apply_old_movie(input_path, output_path, intensity=0.5):
    def old_movie_process(frame, intensity=0.5, frame_count=0):
        # Convert to grayscale with sepia tone
        sepia = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        sepia = cv2.cvtColor(sepia, cv2.COLOR_GRAY2BGR)
        
        # Add sepia tone
        sepia = sepia.astype(np.float32) / 255.0
        sepia[:, :, 0] *= 0.85  # Blue channel
        sepia[:, :, 1] *= 0.95  # Green channel
        sepia[:, :, 2] *= 1.05  # Red channel
        sepia = np.clip(sepia, 0, 1)
        
        # Add film grain
        grain_intensity = 0.15 * intensity
        sepia = random_noise(sepia, mode='gaussian', var=grain_intensity**2)
        
        # Add projector flicker - varies brightness
        flicker_intensity = 0.15 * intensity
        if random.random() < 0.1 * intensity:
            flicker = np.random.uniform(1.0 - flicker_intensity, 1.0 + flicker_intensity)
            sepia = np.clip(sepia * flicker, 0, 1)
        
        # Add frame jitter
        if random.random() < 0.2 * intensity:
            shift_y = random.randint(-int(10 * intensity), int(10 * intensity))
            M = np.float32([[1, 0, 0], [0, 1, shift_y]])
            sepia = cv2.warpAffine(sepia, M, (frame.shape[1], frame.shape[0]))
        
        # Add vignette (darkening around edges)
        h, w = frame.shape[:2]
        vignette = np.ones((h, w))
        center = (w // 2, h // 2)
        radius = min(center[0], center[1])
        
        # Create circular vignette
        Y, X = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((X - center[0])**2 + (Y - center[1])**2)
        vignette = np.clip(1 - dist_from_center / radius * 0.6 * intensity, 0.6, 1)
        
        # Apply vignette
        for i in range(3):
            sepia[:, :, i] = sepia[:, :, i] * vignette
        
        # Convert back to uint8
        return (sepia * 255).astype(np.uint8)
    
    process_video_frames(input_path, output_path, old_movie_process, intensity=intensity)

# Light Leak Effect
def apply_light_leak(input_path, output_path, intensity=0.5):
    def light_leak_process(frame, intensity=0.5, frame_count=0):
        h, w = frame.shape[:2]
        result = frame.astype(np.float32) / 255.0
        
        # Create light leak effect - we'll simulate light streaks
        leak_mask = np.zeros((h, w), dtype=np.float32)
        
        # Create a few random light leaks that stay in place during the video
        random.seed(1)  # Use fixed seed for consistent light leaks across frames
        leak_count = max(1, int(3 * intensity))
        
        for i in range(leak_count):
            # Determine leak type
            leak_type = random.choice(['edge', 'spot', 'streak'])
            
            if leak_type == 'edge':
                # Light coming from an edge
                edge = random.choice(['top', 'bottom', 'left', 'right'])
                
                if edge == 'top':
                    start_y, start_x = 0, random.randint(0, w-1)
                    end_y, end_x = random.randint(int(h * 0.3), int(h * 0.7)), random.randint(0, w-1)
                elif edge == 'bottom':
                    start_y, start_x = h-1, random.randint(0, w-1)
                    end_y, end_x = random.randint(int(h * 0.3), int(h * 0.7)), random.randint(0, w-1)
                elif edge == 'left':
                    start_y, start_x = random.randint(0, h-1), 0
                    end_y, end_x = random.randint(0, h-1), random.randint(int(w * 0.3), int(w * 0.7))
                else:  # right
                    start_y, start_x = random.randint(0, h-1), w-1
                    end_y, end_x = random.randint(0, h-1), random.randint(int(w * 0.3), int(w * 0.7))
                
                # Create gradient
                Y, X = np.ogrid[:h, :w]
                distances = np.sqrt((X - start_x)**2 + (Y - start_y)**2)
                max_distance = np.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
                gradient = np.clip(1 - distances / max_distance, 0, 1)
                
                leak_mask = np.maximum(leak_mask, gradient * random.uniform(0.3, 0.7) * intensity)
                
            elif leak_type == 'spot':
                # Spot of light
                center_x = random.randint(0, w-1)
                center_y = random.randint(0, h-1)
                radius = random.randint(int(min(h, w) * 0.1), int(min(h, w) * 0.3))
                
                Y, X = np.ogrid[:h, :w]
                dist_from_center = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
                spot = np.clip(1 - dist_from_center / radius, 0, 1)
                
                leak_mask = np.maximum(leak_mask, spot * random.uniform(0.4, 0.8) * intensity)
                
            else:  # streak
                # Light streak
                start_x = random.randint(0, w-1)
                start_y = random.randint(0, h-1)
                angle = random.uniform(0, 2 * np.pi)
                length = random.randint(int(min(h, w) * 0.3), int(min(h, w) * 0.7))
                width = random.randint(10, 50)
                
                end_x = int(start_x + length * np.cos(angle))
                end_y = int(start_y + length * np.sin(angle))
                
                # Create line mask
                Y, X = np.ogrid[:h, :w]
                # Use distance from line formula
                numerator = np.abs((end_y - start_y)*X - (end_x - start_x)*Y + end_x*start_y - end_y*start_x)
                denominator = np.sqrt((end_y - start_y)**2 + (end_x - start_x)**2)
                distances = numerator / denominator
                streak = np.clip(1 - distances / width, 0, 1)
                
                leak_mask = np.maximum(leak_mask, streak * random.uniform(0.3, 0.6) * intensity)
        
        # Create colored light leaks (warm tones)
        color_matrix = np.zeros((h, w, 3), dtype=np.float32)
        color_matrix[:, :, 0] = leak_mask * 0.5  # Blue channel - less
        color_matrix[:, :, 1] = leak_mask * 0.8  # Green channel - medium
        color_matrix[:, :, 2] = leak_mask        # Red channel - full
        
        # Apply the light leak
        result = np.clip(result + color_matrix, 0, 1)
        
        # Add a slight overall warm tone to the image
        result[:, :, 2] = np.clip(result[:, :, 2] * (1 + 0.1 * intensity), 0, 1)  # Increase red
        
        # Convert back to uint8
        return (result * 255).astype(np.uint8)
    
    process_video_frames(input_path, output_path, light_leak_process, intensity=intensity)

# Sepia Tone Effect
def apply_sepia(input_path, output_path, intensity=0.5):
    def sepia_process(frame, intensity=0.5):
        # Original colors in BGR
        original = frame.astype(np.float32) / 255.0
        
        # Create sepia tone
        sepia = np.zeros_like(original)
        sepia[:, :, 0] = (original[:, :, 0] * 0.272 + original[:, :, 1] * 0.534 + original[:, :, 2] * 0.131)  # B
        sepia[:, :, 1] = (original[:, :, 0] * 0.349 + original[:, :, 1] * 0.686 + original[:, :, 2] * 0.168)  # G
        sepia[:, :, 2] = (original[:, :, 0] * 0.393 + original[:, :, 1] * 0.769 + original[:, :, 2] * 0.189)  # R
        
        # Add random flickering
        if random.random() < 0.15 * intensity:
            flicker = np.random.uniform(0.85, 1.15)
            sepia = np.clip(sepia * flicker, 0, 1)
        
        # Blend original and sepia based on intensity
        result = cv2.addWeighted(original, 1 - intensity, sepia, intensity, 0)
        
        # Add slight grain
        grain_intensity = 0.03 * intensity
        if grain_intensity > 0:
            grain = random_noise(result, mode='gaussian', var=grain_intensity**2)
            result = grain
        
        # Convert back to uint8
        return (result * 255).astype(np.uint8)
    
    process_video_frames(input_path, output_path, sepia_process, intensity=intensity)

# Glitch Effect
def apply_glitch(input_path, output_path, intensity=0.5):
    def glitch_process(frame, intensity=0.5, frame_count=0):
        h, w = frame.shape[:2]
        result = frame.copy()
        
        # Apply glitch only on some frames
        if random.random() < 0.3 * intensity:
            # Determine how many glitch blocks to create
            num_glitches = int(15 * intensity)
            
            for _ in range(num_glitches):
                # Select random block
                block_height = random.randint(10, max(10, int(h * 0.1)))
                y_start = random.randint(0, h - block_height - 1)
                
                # Select random effect
                effect_type = random.choice(['shift', 'color_shift', 'repeat', 'corrupt'])
                
                if effect_type == 'shift':
                    # Horizontal shift
                    shift_amount = random.randint(5, int(w * 0.2))
                    direction = random.choice([-1, 1])
                    
                    block = result[y_start:y_start+block_height, :].copy()
                    if direction > 0:  # Shift right
                        block[:, shift_amount:] = block[:, :-shift_amount]
                    else:  # Shift left
                        block[:, :-shift_amount] = block[:, shift_amount:]
                        
                    result[y_start:y_start+block_height, :] = block
                    
                elif effect_type == 'color_shift':
                    # RGB channel shift
                    shift_amount = random.randint(5, int(w * 0.1))
                    
                    block = result[y_start:y_start+block_height, :].copy()
                    # Shift red channel
                    if random.random() < 0.5:
                        if random.random() < 0.5:  # Right shift
                            block[:, shift_amount:, 2] = block[:, :-shift_amount, 2]
                        else:  # Left shift
                            block[:, :-shift_amount, 2] = block[:, shift_amount:, 2]
                    
                    # Shift green channel
                    if random.random() < 0.5:
                        if random.random() < 0.5:  # Right shift
                            block[:, shift_amount:, 1] = block[:, :-shift_amount, 1]
                        else:  # Left shift
                            block[:, :-shift_amount, 1] = block[:, shift_amount:, 1]
                            
                    # Shift blue channel
                    if random.random() < 0.5:
                        if random.random() < 0.5:  # Right shift
                            block[:, shift_amount:, 0] = block[:, :-shift_amount, 0]
                        else:  # Left shift
                            block[:, :-shift_amount, 0] = block[:, shift_amount:, 0]
                            
                    result[y_start:y_start+block_height, :] = block
                    
                elif effect_type == 'repeat':
                    # Repeat a block multiple times
                    repeat_lines = min(5, block_height)
                    for i in range(block_height):
                        source_line = y_start + (i % repeat_lines)
                        result[y_start + i, :] = result[source_line, :]
                        
                else:  # corrupt
                    # Add random noise/corruption
                    block = result[y_start:y_start+block_height, :].astype(np.float32) / 255.0
                    noise = np.random.uniform(-0.5, 0.5, block.shape) * intensity
                    block = np.clip(block + noise, 0, 1)
                    result[y_start:y_start+block_height, :] = (block * 255).astype(np.uint8)
            
            # Add random digital artifacts (pixelation) to parts of the image
            if random.random() < 0.2 * intensity:
                pixel_size = random.randint(5, 20)
                area_width = random.randint(int(w * 0.1), int(w * 0.3))
                area_height = random.randint(int(h * 0.1), int(h * 0.3))
                x_start = random.randint(0, w - area_width - 1)
                y_start = random.randint(0, h - area_height - 1)
                
                area = result[y_start:y_start+area_height, x_start:x_start+area_width].copy()
                
                # Pixelate by resizing down and up
                small = cv2.resize(area, (area_width // pixel_size, area_height // pixel_size), 
                                   interpolation=cv2.INTER_LINEAR)
                pixelated = cv2.resize(small, (area_width, area_height), 
                                       interpolation=cv2.INTER_NEAREST)
                
                result[y_start:y_start+area_height, x_start:x_start+area_width] = pixelated
        
        return result
    
    process_video_frames(input_path, output_path, glitch_process, intensity=intensity)

# Vintage Color Effect
def apply_vintage_color(input_path, output_path, intensity=0.5):
    def vintage_color_process(frame, intensity=0.5):
        # Convert to float for processing
        frame_float = frame.astype(np.float32) / 255.0
        
        # Create vintage look with color adjustments
        # Increase contrast slightly
        contrast = 1.2 * intensity + (1 - intensity)
        frame_float = (frame_float - 0.5) * contrast + 0.5
        
        # Cross-process effect (common in vintage photos)
        # Boost blue in shadows, yellow-green in highlights
        shadows = frame_float * frame_float  # Square to target shadows
        highlights = 1 - ((1 - frame_float) * (1 - frame_float))  # Target highlights
        
        # Blue in shadows
        shadows_strength = 0.1 * intensity
        frame_float[:, :, 0] += shadows[:, :, 0] * shadows_strength  # Blue channel
        
        # Yellow-green in highlights
        highlights_strength = 0.1 * intensity
        frame_float[:, :, 1] += highlights[:, :, 1] * highlights_strength  # Green
        frame_float[:, :, 2] += highlights[:, :, 2] * highlights_strength  # Red
        
        # Adjust color balance for vintage look
        # The original color matrix application was causing broadcasting issues
        # Instead of matrix multiplication, we'll apply channel adjustments directly
        
        # Apply color balance adjustments directly to each channel
        frame_float[:, :, 0] *= (1 - 0.1 * intensity)  # Reduce blue channel
        frame_float[:, :, 1] *= (1 + 0.05 * intensity)  # Slightly boost green channel
        frame_float[:, :, 2] *= (1 + 0.15 * intensity)  # Boost red channel more
        
        # Add slight vignette
        h, w = frame.shape[:2]
        center_x, center_y = w // 2, h // 2
        Y, X = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
        max_dist = np.sqrt(center_x**2 + center_y**2)
        vignette = 1 - dist_from_center / max_dist * 0.3 * intensity
        vignette = np.clip(vignette, 0.7, 1.0)
        
        # Apply vignette
        for i in range(3):
            frame_float[:, :, i] = frame_float[:, :, i] * vignette
        
        # Add grain
        if intensity > 0.3:
            grain_intensity = 0.05 * intensity
            grain = random_noise(frame_float, mode='gaussian', var=grain_intensity**2)
            frame_float = grain
        
        # Clip values to valid range and convert back to uint8
        frame_float = np.clip(frame_float, 0, 1)
        return (frame_float * 255).astype(np.uint8)
    
    process_video_frames(input_path, output_path, vintage_color_process, intensity=intensity) 