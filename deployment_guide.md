# Deploying Vintage Video Effects API to a VPS

This guide will help you deploy your Vintage Video Effects API to a Virtual Private Server (VPS) for production use.

## Prerequisites

- A VPS with Ubuntu/Debian (recommended) or other Linux distribution
- Root or sudo access to the server
- Domain name (optional but recommended)

## Step 1: Set Up Your VPS

1. Connect to your VPS via SSH:
```
ssh username@your_server_ip
```

2. Update the system:
```
sudo apt update && sudo apt upgrade -y
```

3. Install required system dependencies:
```
sudo apt install -y python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools python3-venv nginx ffmpeg
```

4. Install additional dependencies for OpenCV:
```
sudo apt install -y libsm6 libxext6 libxrender-dev libglib2.0-0
```

## Step 2: Set Up the Project

1. Create a directory for your application:
```
sudo mkdir -p /var/www/vintage-api
sudo chown $USER:$USER /var/www/vintage-api
```

2. Clone your project (or upload your files) to the server:
```
# If using git:
git clone https://github.com/Monjed1/vintage-effects.git /var/www/vintage-api

# Or copy files directly using SCP:
# scp -r /path/to/your/local/project/* username@your_server_ip:/var/www/vintage-api/
```

3. Create and activate a virtual environment:
```
cd /var/www/vintage-api
python3 -m venv venv
source venv/bin/activate
```

4. Install the Python dependencies:
```
pip install -r requirements.txt
pip install gunicorn  # For production server
```

## Step 3: Configure Gunicorn

1. Create a WSGI entry point. Create a file named `wsgi.py` in your project directory:

```python
from app import app

if __name__ == "__main__":
    app.run()
```

2. Test Gunicorn to make sure it can serve the application:
```
gunicorn --bind 0.0.0.0:5556 wsgi:app
```

3. Create a systemd service file to manage the Gunicorn process:
```
sudo nano /etc/systemd/system/vintage-api.service
```

4. Add the following content:
```
[Unit]
Description=Gunicorn instance to serve Vintage Video Effects API
After=network.target

[Service]
User=<your_username>
Group=www-data
WorkingDirectory=/var/www/vintage-api
Environment="PATH=/var/www/vintage-api/venv/bin"
ExecStart=/var/www/vintage-api/venv/bin/gunicorn --workers 3 --bind unix:vintage-api.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```

Replace `<your_username>` with your actual username.

5. Start and enable the service:
```
sudo systemctl start vintage-api
sudo systemctl enable vintage-api
sudo systemctl status vintage-api  # Check that it's running
```

## Step 4: Configure Nginx

1. Create an Nginx server block:
```
sudo nano /etc/nginx/sites-available/vintage-api
```

2. Add the following configuration:
```
server {
    listen 80;
    server_name your_domain.com www.your_domain.com;  # Or use your server IP

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/vintage-api/vintage-api.sock;
        client_max_body_size 100M;  # Increase max upload size
    }

    # For long-running requests
    proxy_connect_timeout 300s;
    proxy_read_timeout 300s;
    proxy_send_timeout 300s;
}
```

Replace `your_domain.com` with your actual domain or use the server's IP address.

3. Enable the site:
```
sudo ln -s /etc/nginx/sites-available/vintage-api /etc/nginx/sites-enabled
sudo nginx -t  # Test the configuration
sudo systemctl restart nginx
```

## Step 5: Set Up Firewall (Optional but Recommended)

1. Configure UFW to allow Nginx and SSH:
```
sudo ufw allow 'Nginx Full'
sudo ufw allow 'OpenSSH'
sudo ufw enable
```

## Step 6: Set Up SSL with Let's Encrypt (Optional but Recommended)

1. Install Certbot:
```
sudo apt install -y certbot python3-certbot-nginx
```

2. Obtain and install the SSL certificate:
```
sudo certbot --nginx -d your_domain.com -d www.your_domain.com
```

Follow the prompts to configure HTTPS.

## Step 7: Update Application for Production

1. Modify the app.py file to remove debug mode for production:

```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5556)))
```

2. Make sure the temp_videos directory exists and has proper permissions:
```
mkdir -p /var/www/vintage-api/temp_videos
chmod 755 /var/www/vintage-api/temp_videos
```

## Accessing Your API

Your API should now be accessible at:
- http://your_domain.com/api/effects (HTTP)
- https://your_domain.com/api/effects (HTTPS, if SSL is configured)

## Troubleshooting

1. Check the Nginx error logs:
```
sudo tail -f /var/log/nginx/error.log
```

2. Check the Gunicorn service logs:
```
sudo journalctl -u vintage-api
```

3. Check permissions:
```
sudo chown -R <your_username>:www-data /var/www/vintage-api
sudo chmod -R 755 /var/www/vintage-api
```

4. Restart services after changes:
```
sudo systemctl restart vintage-api
sudo systemctl restart nginx
```

## API Usage Examples

### Curl Example for Single Effect
```bash
curl -X POST -F "video=@/path/to/video.mp4" -F "effect=vhs" -F "intensity=0.7" \
     http://your_domain.com/api/apply-effect -o output_video.mp4
```

### Curl Example for Multiple Effects
```bash
curl -X POST -F "video=@/path/to/video.mp4" -F "effects=vhs:0.7" -F "effects=film_grain:0.5" \
     http://your_domain.com/api/combine-effects -o combined_video.mp4
```

### Python Example
```python
import requests

url = "http://your_domain.com/api/apply-effect"
files = {"video": open("video.mp4", "rb")}
data = {"effect": "sepia", "intensity": "0.8"}

response = requests.post(url, files=files, data=data)

with open("processed_video.mp4", "wb") as f:
    f.write(response.content)
```

## Security Considerations

1. Set up a firewall and only expose necessary ports
2. Implement rate limiting to prevent abuse
3. Add API key authentication for additional security
4. Regularly update your server and dependencies
5. Monitor server resources, especially when processing large videos 