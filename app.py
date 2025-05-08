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
from urllib.parse import urlparse
import werkzeug.serving
from Ventageeffect import (
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

UPLOAD_FOLDER = 'temp_videos'
OUTPUT_FOLDER = 'output_videos'  # For storing output videos that will be served
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Server configuration
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', 5557))
SERVER_BASE_URL = os.environ.get('SERVER_BASE_URL', f'http://{SERVER_HOST}:{SERVER_PORT}')

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

# Helper function to download a video from URL
def download_video(url, output_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Check if the request was successful
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    except Exception as e:
        print(f"Error downloading video from {url}: {str(e)}")
        return False

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

# New API endpoints that work with URLs instead of file uploads
@app.route('/api/url/apply-effect', methods=['POST'])
def apply_effect_url():
    """Apply an effect to a video URL and return a URL to the processed video"""
    data = request.json
    if not data or 'video_url' not in data:
        return jsonify({'error': 'No video URL provided in JSON body'}), 400
    
    video_url = data.get('video_url')
    effect_name = data.get('effect', 'vhs')
    intensity = float(data.get('intensity', 0.5))
    
    # Create unique filenames
    video_id = str(uuid.uuid4())
    temp_input = os.path.join(UPLOAD_FOLDER, f"input_{video_id}.mp4")
    
    # Generate a recognizable output filename
    output_filename = f"{effect_name}_{video_id}.mp4"
    temp_output = os.path.join(UPLOAD_FOLDER, output_filename)
    final_output = os.path.join(OUTPUT_FOLDER, output_filename)
    
    try:
        # Download the video
        if not download_video(video_url, temp_input):
            return jsonify({'error': 'Failed to download video from URL'}), 400
        
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
        
        # Move the output to the served directory
        shutil.copy2(temp_output, final_output)
        
        # Generate a publicly accessible URL
        output_url = f"{SERVER_BASE_URL}/videos/{output_filename}"
        
        return jsonify({
            'success': True,
            'video_url': output_url,
            'effect': effect_name,
            'intensity': intensity
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        # Clean up temp files
        safe_delete(temp_input)
        safe_delete(temp_output)

@app.route('/api/url/combine-effects', methods=['POST'])
def combine_effects_url():
    """Apply multiple effects to a video URL and return a URL to the processed video"""
    data = request.json
    if not data or 'video_url' not in data:
        return jsonify({'error': 'No video URL provided in JSON body'}), 400
    
    video_url = data.get('video_url')
    effects = data.get('effects', [])
    
    if not effects:
        return jsonify({'error': 'No effects specified'}), 400
    
    # Create unique filenames
    video_id = str(uuid.uuid4())
    temp_input = os.path.join(UPLOAD_FOLDER, f"input_{video_id}.mp4")
    
    # Generate a recognizable output filename
    output_filename = f"combined_{video_id}.mp4"
    final_output = os.path.join(OUTPUT_FOLDER, output_filename)
    
    try:
        # Download the video
        if not download_video(video_url, temp_input):
            return jsonify({'error': 'Failed to download video from URL'}), 400
        
        current_file = temp_input
        
        # Process each effect in sequence
        for i, effect_data in enumerate(effects):
            # Handle both string format and dictionary format
            if isinstance(effect_data, str):
                effect_name, intensity = effect_data.split(':') if ':' in effect_data else (effect_data, 0.5)
                intensity = float(intensity)
            else:
                effect_name = effect_data.get('name', 'vhs')
                intensity = float(effect_data.get('intensity', 0.5))
            
            temp_output = os.path.join(UPLOAD_FOLDER, f"step_{i}_{video_id}.mp4")
            
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
        
        # Move the final output to the served directory
        shutil.copy2(current_file, final_output)
        
        # Generate a publicly accessible URL
        output_url = f"{SERVER_BASE_URL}/videos/{output_filename}"
        
        return jsonify({
            'success': True,
            'video_url': output_url,
            'effects': effects
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        # Clean up temp files
        safe_delete(temp_input)
        # Clean up any intermediate files
        for i in range(len(effects)):
            safe_delete(os.path.join(UPLOAD_FOLDER, f"step_{i}_{video_id}.mp4"))

# Route to serve processed videos by URL
@app.route('/videos/<filename>')
def serve_video(filename):
    """Serve a processed video file"""
    video_path = os.path.join(OUTPUT_FOLDER, filename)
    if not os.path.exists(video_path):
        return jsonify({'error': 'Video not found'}), 404
    
    return send_file(video_path, mimetype='video/mp4')

# Add a cleanup function to remove temporary files
@app.after_request
def cleanup_temp_files(response):
    """Cleanup temporary files that might be left over"""
    try:
        # Find files older than 1 hour and delete them
        current_time = time.time()
        for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                # If the file is older than 1 hour (3600 seconds)
                if os.path.isfile(file_path) and os.path.getmtime(file_path) < current_time - 3600:
                    safe_delete(file_path)
    except Exception as e:
        # Don't fail if cleanup doesn't work
        print(f"Error during cleanup: {str(e)}")
    return response

if __name__ == '__main__':
    # Clean up any existing output files on startup
    clean_previous_outputs()
    
    # Run the application on the specified port
    print(f"Starting server on {SERVER_HOST}:{SERVER_PORT}")
    app.run(debug=False, host=SERVER_HOST, port=SERVER_PORT) 