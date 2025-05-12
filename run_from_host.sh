#\!/bin/bash

# This script runs the theater scraper from the host system
# It handles entering the toolbox and executing the script

# Set the container name
CONTAINER_NAME="TheatreScraper"

# Log output file
LOG_FILE="/var/home/a/theater-scraper-systemd.log"

# Clear log file
echo "Starting TheatreScraper at $(date)" > "$LOG_FILE"

# Check if container exists and is running
if \! podman container exists "$CONTAINER_NAME"; then
    echo "Error: Container $CONTAINER_NAME does not exist" >> "$LOG_FILE"
    exit 1
fi

# Execute the script in the toolbox
echo "Executing in toolbox..." >> "$LOG_FILE"
podman exec "$CONTAINER_NAME" /var/home/a/Code/TheatreScraper/theater_scraper.sh >> "$LOG_FILE" 2>&1

# Check exit status
if [ $? -eq 0 ]; then
    echo "Theater scraper completed successfully at $(date)" >> "$LOG_FILE"
else
    echo "Theater scraper failed at $(date)" >> "$LOG_FILE"
fi
