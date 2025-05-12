# London Theater Show Scraper - Deployment Guide

This guide provides instructions for deploying the London Theater Show Scraper on a Linux machine, including dependency installation, environment setup, and scheduling.

## System Requirements

- Linux-based operating system (Debian/Ubuntu recommended)
- Python 3.8 or higher
- Internet access to reach theater websites and send emails
- Sufficient disk space for logs and snapshots

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/TheatreScraper.git
cd TheatreScraper
```

### 2. Set Up a Virtual Environment

Create and activate a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

For security, configure email credentials and other sensitive information as environment variables. Create a file named `.env` in the project directory with the following content (adjust as needed):

```
THEATER_SMTP_SERVER=smtp.gmail.com
THEATER_SMTP_PORT=587
THEATER_SMTP_TLS=True
THEATER_SENDER_EMAIL=your-email@gmail.com
THEATER_SENDER_PASSWORD=your-app-password
THEATER_RECIPIENT_EMAIL=recipient@example.com
```

For Gmail, you'll need to use an App Password rather than your regular account password. You can generate one in your Google Account settings.

To load these variables automatically, add the following to your `.bashrc` or create a script to source before running the scraper:

```bash
#!/bin/bash
export $(cat /path/to/TheatreScraper/.env | grep -v '^#' | xargs)
```

### 5. Prepare Directories

Ensure data directories exist and have proper permissions:

```bash
mkdir -p data/snapshots
mkdir -p data/logs
chmod -R 755 data
```

### 6. Test the Application

Run a test execution to verify everything works:

```bash
python main.py --no-email
```

Check the logs for any errors:

```bash
cat data/logs/theater_scraper_$(date +%Y%m%d).log
```

## Setting Up a Cron Job

To run the scraper automatically on a schedule, set up a cron job.

### Create a Wrapper Script

First, create a wrapper script that activates the virtual environment and runs the scraper:

```bash
#!/bin/bash

# theater_scraper.sh - Wrapper script for the London Theater Show Scraper

# Change to the project directory
cd /path/to/TheatreScraper

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Activate virtual environment
source venv/bin/activate

# Run the scraper
python main.py

# Deactivate virtual environment
deactivate
```

Save this as `theater_scraper.sh` in the project directory and make it executable:

```bash
chmod +x theater_scraper.sh
```

### Add a Cron Job

Edit the crontab to schedule the scraper to run daily:

```bash
crontab -e
```

Add the following line to run the scraper every day at 8:00 AM:

```
0 8 * * * /path/to/TheatreScraper/theater_scraper.sh >> /path/to/TheatreScraper/cron.log 2>&1
```

To run it at a different time, adjust the cron schedule accordingly:

- `0 8 * * *` = Run at 8:00 AM every day
- `0 */6 * * *` = Run every 6 hours
- `0 8 * * 1-5` = Run at 8:00 AM on weekdays only (Monday to Friday)

## Monitoring

### Log Rotation

The logs are automatically rotated daily. To prevent disk space issues, set up log rotation using logrotate:

Create a file `/etc/logrotate.d/theater_scraper` with the following content:

```
/path/to/TheatreScraper/data/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 yourusername yourusername
}
```

### Email Notifications

The scraper sends email notifications by default. If you want to disable email notifications for specific runs (e.g., testing), use the `--no-email` flag:

```bash
python main.py --no-email
```

### Filter by Theater

To scrape only specific theaters, use the `--theaters` flag:

```bash
python main.py --theaters national donmar bridge
```

## Troubleshooting

### Check Logs

If the scraper doesn't work as expected, check the logs:

```bash
cat data/logs/theater_scraper_$(date +%Y%m%d).log
```

### Run in Debug Mode

For more detailed logs, run the scraper in debug mode:

```bash
python main.py --debug
```

### Permissions Issues

If you encounter permission issues, ensure the user running the cron job has read/write access to the project directory:

```bash
sudo chown -R yourusername:yourusername /path/to/TheatreScraper
```

### Email Problems

If emails aren't being sent, check:
- SMTP server configuration
- Firewall settings (port 587 for TLS should be open)
- Email credentials
- For Gmail, make sure you're using an App Password and not your regular account password

## Updating the Scraper

To update the scraper to the latest version:

```bash
cd /path/to/TheatreScraper
git pull
source venv/bin/activate
pip install -r requirements.txt
```

## Security Considerations

- Store the `.env` file outside the repository directory or add it to `.gitignore` to avoid accidentally committing credentials
- Restrict access to the project directory and the `.env` file
- Use a dedicated email account for sending notifications
- Don't run the scraper as root