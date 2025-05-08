# Vintage Video Effects API Usage Guide

This document explains how to use the Vintage Video Effects API with n8n workflows or any other HTTP client.

## API Endpoints

The API provides two main URL-based endpoints:

1. `/api/url/apply-effect` - Apply a single effect to a video URL
2. `/api/url/combine-effects` - Apply multiple effects in sequence to a video URL

Both endpoints accept and return JSON data.

## Base URL

The API base URL will be `http://your-server-ip:5557` after deployment. Replace `your-server-ip` with your VPS IP address or domain name.

## 1. Apply Single Effect

**Endpoint:** `POST /api/url/apply-effect`

**Request Body:**
```json
{
  "video_url": "https://example.com/path/to/video.mp4",
  "effect": "vhs",
  "intensity": 0.7
}
```

- `video_url`: (Required) URL to the video you want to process
- `effect`: (Optional) Effect to apply (defaults to "vhs" if not specified)
- `intensity`: (Optional) Effect intensity from 0.1 to 1.0 (defaults to 0.5)

**Available Effects:**
- `vhs` - VHS glitch overlay effect
- `crt` - CRT scan lines effect
- `film_grain` - 8mm film grain overlay
- `old_movie` - Old movie projector effect
- `light_leak` - Vintage light leak effect
- `sepia` - Sepia tone effect
- `glitch` - Digital glitch effect
- `vintage_color` - Vintage color grading

**Response:**
```json
{
  "success": true,
  "video_url": "http://your-server-ip:5557/videos/vhs_a1b2c3d4-e5f6-7890-abcd-1234567890ab.mp4",
  "effect": "vhs",
  "intensity": 0.7
}
```

The response includes a URL to the processed video that you can use in your n8n workflow.

## 2. Apply Multiple Effects

**Endpoint:** `POST /api/url/combine-effects`

**Request Body:**
```json
{
  "video_url": "https://example.com/path/to/video.mp4",
  "effects": [
    {"name": "film_grain", "intensity": 0.8},
    {"name": "old_movie", "intensity": 0.6},
    {"name": "light_leak", "intensity": 0.3}
  ]
}
```

- `video_url`: (Required) URL to the video you want to process
- `effects`: (Required) Array of effects to apply in sequence

Each effect can be specified in two ways:
1. As an object with `name` and `intensity` properties
2. As a string in the format `"name:intensity"` (e.g., `"vhs:0.7"`)

**Response:**
```json
{
  "success": true,
  "video_url": "http://your-server-ip:5557/videos/combined_a1b2c3d4-e5f6-7890-abcd-1234567890ab.mp4",
  "effects": [
    {"name": "film_grain", "intensity": 0.8},
    {"name": "old_movie", "intensity": 0.6},
    {"name": "light_leak", "intensity": 0.3}
  ]
}
```

## n8n Workflow Example

Here's how to use the API in an n8n workflow:

1. Add an HTTP Request node
2. Configure it as follows:
   - Method: POST
   - URL: `http://your-server-ip:5557/api/url/apply-effect`
   - Headers: `Content-Type: application/json`
   - Body: 
     ```json
     {
       "video_url": "{{$node['Previous Node'].json.videoUrl}}",
       "effect": "vhs",
       "intensity": 0.7
     }
     ```

3. Connect the HTTP Request node to your next node
4. The processed video URL will be available in the output at: `{{$node['HTTP Request'].json.video_url}}`

## Error Handling

If an error occurs, the API will return a JSON response with an `error` field:

```json
{
  "error": "Failed to download video from URL"
}
```

Make sure to handle these errors in your n8n workflow using the "Error" output of the HTTP Request node.

## Processing Time

Video processing times vary depending on:
- Video size and duration
- Number and type of effects applied
- Server resources

For longer videos, your n8n workflow HTTP node might need an increased timeout setting.

## Notes

- Videos are automatically deleted from the server after 1 hour
- The API supports MP4 videos only
- Maximum video size is 50MB

## Testing the API

You can test the API using curl:

```bash
curl -X POST http://your-server-ip:5557/api/url/apply-effect \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://example.com/path/to/video.mp4", "effect": "vhs", "intensity": 0.7}'
```

## Deployment Instructions

To deploy this API on your VPS:

1. Transfer all the files to your VPS:
   ```
   app.py
   Ventageeffect.py
   requirements.txt
   deploy.sh
   templates/index.html
   ```

2. Make the deployment script executable and run it:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. The server will start on port 5557 