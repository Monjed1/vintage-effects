# Docker Deployment Guide for Vintage Effect Videos API

This guide explains how to deploy the Vintage Effect Videos API using Docker.

## Prerequisites

- Docker installed on your server
- Docker Compose installed on your server
- Basic understanding of Docker commands

## Deployment Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/vintage-effect-videos.git
cd vintage-effect-videos
```

### 2. Configure Environment Variables (Optional)

Edit the `docker-compose.yml` file to update the `PUBLIC_URL_BASE` environment variable:

```yaml
environment:
  - PORT=5556
  - PUBLIC_URL_BASE=http://your-server-ip:5556  # Change this to your server's public URL
```

### 3. Build and Start the Container

```bash
docker-compose up -d --build
```

This will:
- Build the Docker image with all necessary dependencies
- Start the container in detached mode
- Map port 5556 from the container to your host
- Mount the processed_videos directory for persistence

### 4. Verify the Deployment

Check if the container is running:

```bash
docker ps
```

Test the API:

```bash
curl http://localhost:5556/api/effects
```

### 5. View Logs

To view application logs:

```bash
docker-compose logs -f
```

## Production Considerations

### Using HTTPS with Docker

For production environments, you should use HTTPS. The simplest way is to set up a reverse proxy like Nginx or Traefik in front of your Docker container.

#### Example using Nginx as reverse proxy:

1. Install Nginx on your host:
```bash
sudo apt update
sudo apt install -y nginx
```

2. Create an Nginx configuration file:
```bash
sudo nano /etc/nginx/sites-available/vintage-api
```

3. Add the following configuration:
```
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5556;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        client_max_body_size 500M;
    }
}
```

4. Enable the site and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/vintage-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

5. Set up SSL with Let's Encrypt:
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Resource Management

Adjust the resource limits in `docker-compose.yml` based on your server capabilities:

```yaml
deploy:
  resources:
    limits:
      cpus: '2'     # Adjust based on your server's CPU
      memory: 2G    # Adjust based on your server's RAM
```

### Data Persistence

The Docker Compose configuration mounts the `processed_videos` directory from the host to the container to ensure processed videos are persisted even if the container is restarted.

## Updating the Application

To update the application with new changes:

```bash
git pull                    # Pull the latest code
docker-compose down         # Stop the container
docker-compose up -d --build  # Rebuild and restart
```

## Troubleshooting

### Container fails to start

Check the logs:
```bash
docker-compose logs
```

### Performance issues

If processing large videos is slow, consider:
1. Increasing the resource limits in docker-compose.yml
2. Using a more powerful server
3. Implementing a queue system for handling large videos

### API not accessible

1. Verify the container is running: `docker ps`
2. Check if the port is correctly mapped: `docker-compose ps`
3. Make sure your firewall allows traffic on port 5556: `sudo ufw status` 