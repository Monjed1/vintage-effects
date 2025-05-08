import os
from flask import Flask, request, jsonify, send_file, render_template, g, session, url_for
import tempfile
import cv2
import numpy as np
import time
import shutil
import glob
import uuid
import requests
from werkzeug.utils import secure_filename
from urllib.parse import urlparse
from effects import (
    apply_vhs_effect, 
    apply_crt_scanlines, 
    apply_film_grain, 
    apply_old_movie, 
    apply_light_leak,
    apply_sepia, 
    apply_glitch, 
    apply_vintage_color
)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload
app.secret_key = os.urandom(24)  # For session management

# Configuration
UPLOAD_FOLDER = 'temp_videos'
PROCESSED_FOLDER = 'processed_videos'  # Folder to store processed videos
PUBLIC_URL_BASE = os.environ.get('PUBLIC_URL_BASE', 'http://localhost:5556')  # Base URL for accessing processed videos

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Helper function to safely delete a file
def safe_delete(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted: {file_path}")
    except Exception as e:
        print(f"Could not delete {file_path}: {str(e)}")
        # File is still in use, will be cleaned up later

# Helper function to clean all previous output files
def clean_previous_outputs():
    try:
        # Get all output files in the temp directory
        output_files = glob.glob(os.path.join(UPLOAD_FOLDER, "output_*.mp4"))
        output_files.extend(glob.glob(os.path.join(UPLOAD_FOLDER, "step_*.mp4")))
        
        # Delete each one
        for file_path in output_files:
            safe_delete(file_path)
            
        print(f"Cleaned {len(output_files)} previous output files")
    except Exception as e:
        print(f"Error cleaning previous outputs: {str(e)}")

# Helper function to download a video from a URL
def download_video(url):
    try:
        # Create a temporary file to download the video
        video_id = uuid.uuid4().hex
        temp_path = os.path.join(UPLOAD_FOLDER, f"download_{video_id}.mp4")
        
        # Download the video
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return temp_path
    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        raise e

# Create URL for a processed video
def create_video_url(filename):
    # Create a public URL for the processed video
    return f"{PUBLIC_URL_BASE}/video/{filename}"

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/effects', methods=['GET'])
def list_effects():
    """List all available video effects"""
    effects = {
        "vhs": "VHS glitch overlay effect",
        "crt": "CRT scan lines effect",
        "film_grain": "8mm film grain overlay",
        "old_movie": "Old movie projector effect",
        "light_leak": "Vintage light leak effect",
        "sepia": "Sepia tone effect",
        "glitch": "Digital glitch effect",
        "vintage_color": "Vintage color grading"
    }
    return jsonify(effects)

# Route to serve processed videos
@app.route('/video/<filename>')
def serve_video(filename):
    """Serve a processed video"""
    return send_file(os.path.join(PROCESSED_FOLDER, filename))

@app.route('/api/url/apply-effect', methods=['POST'])
def apply_effect_url():
    """Apply selected effect to a video from a URL"""
    # Clean previous output files when a new process starts
    clean_previous_outputs()
    
    data = request.json
    if not data or 'video_url' not in data:
        return jsonify({'error': 'No video URL provided in the request JSON'}), 400
    
    video_url = data['video_url']
    effect_name = data.get('effect', 'vhs')
    intensity = float(data.get('intensity', 0.5))
    
    try:
        # Download the video
        temp_input = download_video(video_url)
        
        # Generate a unique output filename
        output_filename = f"{effect_name}_{uuid.uuid4().hex}.mp4"
        temp_output = os.path.join(UPLOAD_FOLDER, f"output_{uuid.uuid4().hex}.mp4")
        final_output = os.path.join(PROCESSED_FOLDER, output_filename)
        
        # Apply the requested effect
        if effect_name == 'vhs':
            apply_vhs_effect(temp_input, temp_output, intensity)
        elif effect_name == 'crt':
            apply_crt_scanlines(temp_input, temp_output, intensity)
        elif effect_name == 'film_grain':
            apply_film_grain(temp_input, temp_output, intensity)
        elif effect_name == 'old_movie':
            apply_old_movie(temp_input, temp_output, intensity)
        elif effect_name == 'light_leak':
            apply_light_leak(temp_input, temp_output, intensity)
        elif effect_name == 'sepia':
            apply_sepia(temp_input, temp_output, intensity)
        elif effect_name == 'glitch':
            apply_glitch(temp_input, temp_output, intensity)
        elif effect_name == 'vintage_color':
            apply_vintage_color(temp_input, temp_output, intensity)
        else:
            return jsonify({'error': f'Unknown effect: {effect_name}'}), 400
        
        # Move the output file to the processed folder
        shutil.move(temp_output, final_output)
        
        # Return the URL of the processed video
        video_url = create_video_url(output_filename)
        
        return jsonify({
            'success': True,
            'message': f'Successfully applied {effect_name} effect',
            'video_url': video_url
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        # Clean up temp files
        safe_delete(temp_input)

@app.route('/api/url/combine-effects', methods=['POST'])
def combine_effects_url():
    """Apply multiple effects in sequence to a video from a URL"""
    # Clean previous output files when a new process starts
    clean_previous_outputs()
    
    data = request.json
    if not data or 'video_url' not in data:
        return jsonify({'error': 'No video URL provided in the request JSON'}), 400
    
    video_url = data['video_url']
    effects = data.get('effects', [])
    
    if not effects:
        return jsonify({'error': 'No effects specified'}), 400
    
    try:
        # Download the video
        temp_input = download_video(video_url)
        current_file = temp_input
        
        for i, effect_data in enumerate(effects):
            # Extract effect name and intensity
            if isinstance(effect_data, dict):
                effect_name = effect_data.get('name')
                intensity = float(effect_data.get('intensity', 0.5))
            elif isinstance(effect_data, str):
                parts = effect_data.split(':')
                effect_name = parts[0]
                intensity = float(parts[1]) if len(parts) > 1 else 0.5
            else:
                return jsonify({'error': 'Invalid effect format'}), 400
            
            temp_output = os.path.join(UPLOAD_FOLDER, f"step_{i}_{uuid.uuid4().hex}.mp4")
            
            # Apply the current effect
            if effect_name == 'vhs':
                apply_vhs_effect(current_file, temp_output, intensity)
            elif effect_name == 'crt':
                apply_crt_scanlines(current_file, temp_output, intensity)
            elif effect_name == 'film_grain':
                apply_film_grain(current_file, temp_output, intensity)
            elif effect_name == 'old_movie':
                apply_old_movie(current_file, temp_output, intensity)
            elif effect_name == 'light_leak':
                apply_light_leak(current_file, temp_output, intensity)
            elif effect_name == 'sepia':
                apply_sepia(current_file, temp_output, intensity)
            elif effect_name == 'glitch':
                apply_glitch(current_file, temp_output, intensity)
            elif effect_name == 'vintage_color':
                apply_vintage_color(current_file, temp_output, intensity)
            else:
                return jsonify({'error': f'Unknown effect: {effect_name}'}), 400
            
            # Cleanup previous step if not the original
            if current_file != temp_input:
                safe_delete(current_file)
                
            current_file = temp_output
        
        # Create final output file
        output_filename = f"combined_{uuid.uuid4().hex}.mp4"
        final_output = os.path.join(PROCESSED_FOLDER, output_filename)
        
        # Move the processed file to the final location
        shutil.move(current_file, final_output)
        
        # Return the URL of the processed video
        video_url = create_video_url(output_filename)
        
        return jsonify({
            'success': True,
            'message': 'Successfully applied combined effects',
            'video_url': video_url
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        # Clean up the original temp file
        safe_delete(temp_input)

# Keeping the original file upload endpoints for backward compatibility
@app.route('/api/apply-effect', methods=['POST'])
def apply_effect():
    """Apply selected effect to uploaded video"""
    # Clean previous output files when a new process starts
    clean_previous_outputs()
    
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    video_file = request.files['video']
    effect_name = request.form.get('effect', 'vhs')
    intensity = float(request.form.get('intensity', 0.5))
    
    # Save uploaded video temporarily
    temp_input = os.path.join(UPLOAD_FOLDER, f"input_{os.urandom(8).hex()}.mp4")
    video_file.save(temp_input)
    
    # Output path
    temp_output = os.path.join(UPLOAD_FOLDER, f"output_{os.urandom(8).hex()}.mp4")
    
    # Apply the requested effect
    try:
        if effect_name == 'vhs':
            apply_vhs_effect(temp_input, temp_output, intensity)
        elif effect_name == 'crt':
            apply_crt_scanlines(temp_input, temp_output, intensity)
        elif effect_name == 'film_grain':
            apply_film_grain(temp_input, temp_output, intensity)
        elif effect_name == 'old_movie':
            apply_old_movie(temp_input, temp_output, intensity)
        elif effect_name == 'light_leak':
            apply_light_leak(temp_input, temp_output, intensity)
        elif effect_name == 'sepia':
            apply_sepia(temp_input, temp_output, intensity)
        elif effect_name == 'glitch':
            apply_glitch(temp_input, temp_output, intensity)
        elif effect_name == 'vintage_color':
            apply_vintage_color(temp_input, temp_output, intensity)
        else:
            return jsonify({'error': f'Unknown effect: {effect_name}'}), 400
        
        # Return the processed video
        return send_file(temp_output, as_attachment=True, 
                         download_name=f"{effect_name}_video.mp4", 
                         mimetype='video/mp4')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        # Clean up temp files - use safe delete to avoid errors
        safe_delete(temp_input)
        # We don't remove output here because it's being sent

@app.route('/api/combine-effects', methods=['POST'])
def combine_effects():
    """Apply multiple effects in sequence"""
    # Clean previous output files when a new process starts
    clean_previous_outputs()
    
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    video_file = request.files['video']
    effects = request.form.getlist('effects')
    
    if not effects:
        return jsonify({'error': 'No effects specified'}), 400
    
    # Save uploaded video temporarily
    temp_input = os.path.join(UPLOAD_FOLDER, f"input_{os.urandom(8).hex()}.mp4")
    video_file.save(temp_input)
    
    current_file = temp_input
    
    try:
        for i, effect in enumerate(effects):
            effect_name, intensity = effect.split(':') if ':' in effect else (effect, 0.5)
            intensity = float(intensity)
            
            temp_output = os.path.join(UPLOAD_FOLDER, f"step_{i}_{os.urandom(8).hex()}.mp4")
            
            # Apply the current effect
            if effect_name == 'vhs':
                apply_vhs_effect(current_file, temp_output, intensity)
            elif effect_name == 'crt':
                apply_crt_scanlines(current_file, temp_output, intensity)
            elif effect_name == 'film_grain':
                apply_film_grain(current_file, temp_output, intensity)
            elif effect_name == 'old_movie':
                apply_old_movie(current_file, temp_output, intensity)
            elif effect_name == 'light_leak':
                apply_light_leak(current_file, temp_output, intensity)
            elif effect_name == 'sepia':
                apply_sepia(current_file, temp_output, intensity)
            elif effect_name == 'glitch':
                apply_glitch(current_file, temp_output, intensity)
            elif effect_name == 'vintage_color':
                apply_vintage_color(current_file, temp_output, intensity)
            else:
                return jsonify({'error': f'Unknown effect: {effect_name}'}), 400
            
            # Cleanup previous step if not the original
            if current_file != temp_input:
                safe_delete(current_file)
                
            current_file = temp_output
        
        # Return the final processed video
        return send_file(current_file, as_attachment=True, 
                         download_name="combined_effects_video.mp4", 
                         mimetype='video/mp4')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        # Clean up the original temp file
        safe_delete(temp_input)
        # Other temp files are cleaned up during processing

# Add a cleanup function to remove temporary files
@app.after_request
def cleanup_temp_files(response):
    """Cleanup temporary files that might be left over"""
    try:
        # Find files older than 1 hour and delete them
        current_time = time.time()
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            # If the file is older than 1 hour (3600 seconds)
            if os.path.isfile(file_path) and os.path.getmtime(file_path) < current_time - 3600:
                safe_delete(file_path)
                
        # Also clean up old processed videos (after 24 hours)
        for filename in os.listdir(PROCESSED_FOLDER):
            file_path = os.path.join(PROCESSED_FOLDER, filename)
            # If the file is older than 24 hours
            if os.path.isfile(file_path) and os.path.getmtime(file_path) < current_time - 86400:
                safe_delete(file_path)
    except Exception as e:
        # Don't fail if cleanup doesn't work
        print(f"Error during cleanup: {str(e)}")
    return response

if __name__ == '__main__':
    # Clean up any existing output files on startup
    clean_previous_outputs()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5556))) 