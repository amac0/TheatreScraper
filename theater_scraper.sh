#!/bin/bash

# theater_scraper.sh - Wrapper script for the London Theater Show Scraper

# Store script start time
SCRIPT_START_TIME=$(date +"%Y-%m-%d %H:%M:%S")
echo "Theater Scraper started at $SCRIPT_START_TIME"

# Change to the project directory
# Replace with the actual path to your TheatreScraper installation
SCRAPER_DIR="/var/home/a/Code/TheatreScraper"
cd "$SCRAPER_DIR" || { echo "Error: Failed to change to $SCRAPER_DIR directory"; exit 1; }

# Load environment variables if .env file exists
if [ -f .env ]; then
    # This properly handles variables with spaces in their values
    while IFS= read -r line || [ -n "$line" ]; do
        # Skip comments and empty lines
        if [[ ! "$line" =~ ^# && -n "$line" ]]; then
            # Extract variable name and value
            var_name="${line%%=*}"
            var_value="${line#*=}"
            # Export the variable, preserving spaces
            export "$var_name"="$var_value"
        fi
    done < .env
    echo "Loaded environment variables from .env file"
else
    echo "Warning: .env file not found. Email functionality may not work."
fi

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Activated virtual environment"
else
    echo "Warning: Virtual environment not found at venv/. Using system Python."
fi

# Run the scraper
echo "Running Theater Scraper..."
python main.py
SCRAPER_EXIT_CODE=$?

if [ $SCRAPER_EXIT_CODE -eq 0 ]; then
    echo "Theater Scraper completed successfully"
else
    echo "Theater Scraper failed with exit code $SCRAPER_EXIT_CODE"
fi

# Deactivate virtual environment (if activated)
if [ -d "venv" ]; then
    deactivate
    echo "Deactivated virtual environment"
fi

# Store script end time and calculate runtime
SCRIPT_END_TIME=$(date +"%Y-%m-%d %H:%M:%S")
SCRIPT_RUNTIME=$(($(date -d "$SCRIPT_END_TIME" +%s) - $(date -d "$SCRIPT_START_TIME" +%s)))
echo "Theater Scraper finished at $SCRIPT_END_TIME"
echo "Total runtime: $SCRIPT_RUNTIME seconds"

exit $SCRAPER_EXIT_CODE