# URL-based Video Effects API Usage Guide

This guide explains how to use the Vintage Video Effects API with URL-based inputs and outputs instead of direct file uploads.

## API Endpoints

The API provides two main URL-based endpoints:

1. `/api/url/apply-effect` - Apply a single effect to a video
2. `/api/url/combine-effects` - Apply multiple effects in sequence

## Using the Single Effect Endpoint

### Request Format

Make a POST request to `/api/url/apply-effect` with a JSON body:

```json
{
  "video_url": "https://example.com/path/to/your/video.mp4",
  "effect": "vhs",
  "intensity": 0.7
}
```

Parameters:
- `video_url` (required): URL of the video to process
- `effect` (optional): The effect to apply (defaults to "vhs")
- `intensity` (optional): Intensity of the effect from 0.1 to 1.0 (defaults to 0.5)

### Response Format

The API will respond with a JSON object:

```json
{
  "success": true,
  "message": "Successfully applied vhs effect",
  "video_url": "http://your-server.com/video/vhs_a1b2c3d4.mp4"
}
```

### Example Using cURL

```bash
curl -X POST \
  http://localhost:5556/api/url/apply-effect \
  -H 'Content-Type: application/json' \
  -d '{
    "video_url": "https://example.com/video.mp4",
    "effect": "film_grain",
    "intensity": 0.8
  }'
```

### Example Using Python

```python
import requests
import json

url = "http://localhost:5556/api/url/apply-effect"
payload = {
    "video_url": "https://example.com/video.mp4",
    "effect": "sepia",
    "intensity": 0.6
}
headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
result = response.json()

if result.get("success"):
    print(f"Processed video available at: {result['video_url']}")
else:
    print(f"Error: {result.get('error')}")
```

## Using the Multiple Effects Endpoint

### Request Format

Make a POST request to `/api/url/combine-effects` with a JSON body:

```json
{
  "video_url": "https://example.com/path/to/your/video.mp4",
  "effects": [
    {"name": "vhs", "intensity": 0.7},
    {"name": "film_grain", "intensity": 0.5},
    {"name": "light_leak", "intensity": 0.3}
  ]
}
```

Alternatively, you can use a simpler string format for effects:

```json
{
  "video_url": "https://example.com/path/to/your/video.mp4",
  "effects": ["vhs:0.7", "film_grain:0.5", "light_leak:0.3"]
}
```

Parameters:
- `video_url` (required): URL of the video to process
- `effects` (required): Array of effects to apply in sequence

### Response Format

The API will respond with a JSON object:

```json
{
  "success": true,
  "message": "Successfully applied combined effects",
  "video_url": "http://your-server.com/video/combined_a1b2c3d4.mp4"
}
```

### Example Using cURL

```bash
curl -X POST \
  http://localhost:5556/api/url/combine-effects \
  -H 'Content-Type: application/json' \
  -d '{
    "video_url": "https://example.com/video.mp4",
    "effects": [
      {"name": "old_movie", "intensity": 0.8},
      {"name": "light_leak", "intensity": 0.4}
    ]
  }'
```

### Example Using Python

```python
import requests
import json

url = "http://localhost:5556/api/url/combine-effects"
payload = {
    "video_url": "https://example.com/video.mp4",
    "effects": [
        {"name": "vhs", "intensity": 0.7},
        {"name": "film_grain", "intensity": 0.5}
    ]
}
headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
result = response.json()

if result.get("success"):
    print(f"Processed video available at: {result['video_url']}")
else:
    print(f"Error: {result.get('error')}")
```

## Available Effects

- `vhs`: VHS glitch overlay effect
- `crt`: CRT scan lines effect
- `film_grain`: 8mm film grain overlay
- `old_movie`: Old movie projector effect
- `light_leak`: Vintage light leak effect
- `sepia`: Sepia tone effect
- `glitch`: Digital glitch effect
- `vintage_color`: Vintage color grading

## Error Handling

If an error occurs, the API will respond with a JSON object:

```json
{
  "error": "Error message details"
}
```

## Important Notes

1. The video at the provided URL must be publicly accessible
2. Processed videos are stored on the server for 24 hours before automatic cleanup
3. The `PUBLIC_URL_BASE` environment variable can be set to change the base URL in the response 