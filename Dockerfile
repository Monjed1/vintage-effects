FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV and ffmpeg
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create directories for video storage
RUN mkdir -p temp_videos processed_videos
RUN chmod 777 temp_videos processed_videos

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=5556
ENV PUBLIC_URL_BASE=http://62.171.168.74:5556

# Expose the port
EXPOSE 5556

# Run the application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5556", "wsgi:app"] 