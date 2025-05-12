# London Theater Show Scraper

⚠️ **Warning**: This was mostly coded with AI. I wrote about what I did here:
https://www.bricoleur.org/2025/05/claude-code-theater-scraper.html
Please don't rely on it for anything.

## Project Overview
The London Theater Show Scraper is an automated tool that monitors London theater websites daily for new shows and updates to existing listings. It extracts show details, compares them against previous records, and sends email notifications about changes.

## Features
- **Daily Monitoring**: Automatically scrapes theater websites on a daily schedule
- **Change Detection**: Identifies new shows and updates to existing listings
- **Email Notifications**: Sends detailed email reports of changes and current listings
- **Error Handling**: Gracefully handles website changes and connectivity issues

## Monitored Websites
The scraper monitors several London theater websites including:
- Donmar Warehouse
- Bridge Theatre
- National Theatre
- Hampstead Theatre
- Marylebone Theatre
- Soho Theatre (Dean Street & Walthamstow)
- Royal Shakespeare Company (RSC)
- Royal Court Theatre
- Drury Lane Theatre

## Extracted Data
For each show, the scraper extracts:
- Show Title
- Venue
- Sale Dates (for members and general public)
- Performance Dates
- Pricing Information
- Genre/Description
- Booking Page Link

## Technical Details
- Built with Python using requests, BeautifulSoup, and Selenium
- Stores data in CSV format for tracking changes
- Sends notifications via email using smtplib
- Includes comprehensive error handling and logging

## Setup and Installation
1. Clone this repository
2. Install the required dependencies with `pip install -r requirements.txt`
3. Configure the settings in the `config` directory
4. Run the script manually or set up a daily cron job (see DEPLOYMENT.md)

## Usage
Once installed and configured, the scraper can be scheduled to run daily using cron (Linux) or Task Scheduler (Windows).

## Project Structure
```
london-theater-scraper/
├── config/                 # Configuration files
├── src/                    # Source code
├── tests/                  # Test files
│   ├── fixtures/           # Test data and fixtures
├── data/                   # For storing CSV snapshots
│   ├── snapshots/          # Daily snapshots
│   ├── logs/               # Log files
├── requirements.txt        # Project dependencies
├── README.md               # Project documentation
├── main.py                 # Entry point script
```
