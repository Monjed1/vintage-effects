# Vintage Video Effects API

A Python API for applying various vintage video effects to uploaded videos. This project provides a REST API that can apply classic VHS, CRT, film grain, and other nostalgic effects to your videos.

## Features

- Apply individual effects to videos
- Combine multiple effects in sequence
- Adjust effect intensity
- Preserves original audio

## Available Effects

1. **VHS & CRT Effects**
   - VHS Glitch Overlay
   - CRT Scan Lines Effect

2. **Film Grain & Vintage Movie Effects**
   - 8mm Film Grain Overlay
   - Old Movie Projector Effect

3. **Retro Color & Light Leaks**
   - Light Leak Effect
   - Sepia Tone Effect

4. **Glitch & Distortion Effects**
   - Digital Glitch Effect

5. **Vintage Color Grading**
   - Vintage Color Effect

## Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/vintage-video-effects.git
cd vintage-video-effects
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Run the application:
```
python app.py
```

The API will be available at `http://localhost:5000`.

## API Usage

### List Available Effects

```
GET /api/effects
```

Returns a JSON object containing all available effects and their descriptions.

### Apply an Effect

```
POST /api/apply-effect
```

**Form parameters:**
- `video`: The video file to process (multipart/form-data)
- `effect`: The effect to apply (defaults to 'vhs' if not specified)
- `intensity`: A value between 0.0 and 1.0 to control effect strength (defaults to 0.5)

**Example using curl:**
```
curl -F "video=@my_video.mp4" -F "effect=film_grain" -F "intensity=0.7" http://localhost:5000/api/apply-effect -o output.mp4
```

### Apply Multiple Effects

```
POST /api/combine-effects
```

**Form parameters:**
- `video`: The video file to process (multipart/form-data)
- `effects`: A list of effects to apply in sequence (can be provided multiple times in the form)

Each effect can include an intensity value by appending `:` followed by the intensity value.

**Example using curl:**
```
curl -F "video=@my_video.mp4" -F "effects=vhs:0.7" -F "effects=film_grain:0.5" -F "effects=light_leak:0.3" http://localhost:5000/api/combine-effects -o combined_output.mp4
```

## Effect Details

- **vhs**: VHS glitch overlay with RGB shift and noise
- **crt**: CRT scan lines with screen curvature  
- **film_grain**: 8mm film grain with dust and scratches
- **old_movie**: Old movie projector effect with flicker and jitter
- **light_leak**: Vintage light leak effect with warm tones
- **sepia**: Sepia tone with subtle flickering
- **glitch**: Digital glitch effect with artifacts and distortion
- **vintage_color**: Vintage color grading with cross-processing

## Examples

Apply a VHS effect with high intensity:
```
curl -F "video=@my_video.mp4" -F "effect=vhs" -F "intensity=0.9" http://localhost:5000/api/apply-effect -o vhs_video.mp4
```

Create a retro film look by combining effects:
```
curl -F "video=@my_video.mp4" -F "effects=film_grain:0.7" -F "effects=old_movie:0.5" -F "effects=light_leak:0.3" http://localhost:5000/api/combine-effects -o retro_film.mp4
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 