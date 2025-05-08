# Vintage Video Effects API

An API for applying vintage effects to videos, including VHS, film grain, CRT scanlines, and more.

## Features

- Apply individual effects to videos
- Combine multiple effects in sequence
- Adjust effect intensity
- Preserves original audio
- URL-based API for easy integration

## Available Effects

- VHS Glitch Overlay
- CRT Scan Lines Effect
- 8mm Film Grain Overlay
- Old Movie Projector Effect
- Vintage Light Leak Effect
- Sepia Tone Effect
- Digital Glitch Effect
- Vintage Color Grading

## Getting Started

### Prerequisites

- Python 3.6+
- Required libraries (see requirements.txt)

### Installation

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

The API will be available at `http://localhost:5556`.

## API Usage

### URL-based API

Process a video from a URL and get back a URL to the processed video:

```python
import requests

url = "http://localhost:5556/api/url/apply-effect"
payload = {
    "video_url": "https://example.com/video.mp4",
    "effect": "vhs",
    "intensity": 0.7
}

response = requests.post(url, json=payload)
result = response.json()

print(f"Processed video: {result['video_url']}")
```

### File Upload API

Upload a video and download the processed result:

```
POST /api/apply-effect
```

Form parameters:
- `video`: The video file
- `effect`: Effect name (e.g., "vhs")
- `intensity`: Effect strength (0.1-1.0)

See the documentation for more details.

## Deployment

See [deployment_guide.md](deployment_guide.md) for instructions on deploying to a VPS.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Flask, OpenCV, and NumPy
- Contributors welcome! 