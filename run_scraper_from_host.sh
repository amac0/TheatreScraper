#\!/bin/bash

# This script runs the theater scraper from the host system
CONTAINER_NAME="TheatreScraper"
LOG_FILE="/var/home/a/theater-scraper-systemd.log"

# Clear log file
echo "Starting TheatreScraper at $(date)" > "$LOG_FILE"

# Run the script in the container
podman exec "$CONTAINER_NAME" /var/home/a/Code/TheatreScraper/theater_scraper.sh >> "$LOG_FILE" 2>&1
