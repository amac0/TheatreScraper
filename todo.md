# London Theater Show Scraper - TODO Checklist

This checklist outlines every major task and subtask required to complete the London Theater Show Scraper project. Use this as a guide to track progress through setup, development, testing, and deployment.

---

## 1. Project Setup & Infrastructure
- [ ] **Create Folder Structure**
  - [ ] Create the project root directory.
  - [ ] Create subdirectories:
    - `src/` - Application source code.
    - `tests/` - Unit and integration tests.
    - `config/` (optional) - Configuration files.
- [ ] **Environment Setup**
  - [ ] Set up a Python virtual environment.
  - [ ] Create a `requirements.txt` including:
    - `requests`
    - `beautifulsoup4`
    - `selenium`
    - `pandas`
    - (Note: `smtplib` is part of the standard library)
    - (Include any additional required libraries.)
- [ ] **Documentation**
  - [ ] Create a `README.md` that describes:
    - The project overview.
    - Technical specifications.
    - Installation and usage instructions.

---

## 2. Configuration & Logging
- [ ] **Configuration Module (`config.py`)**
  - [ ] Define a list of London theater URLs to monitor.
  - [ ] Add email configuration settings:
    - SMTP server, port, sender, and recipient details.
  - [ ] Define file paths for:
    - CSV snapshot storage.
    - Log files.
- [ ] **Logging Module (`logger.py`)**
  - [ ] Set up a logging configuration:
    - Log file creation with daily rotation if needed.
    - Log levels (INFO, DEBUG, ERROR).
  - [ ] Integrate timestamps and error message formatting.

---

## 3. Scraping Modules
### Static Scraping with BeautifulSoup
- [ ] **Static Scraper Module (`scraper_static.py`)**
  - [ ] Implement a function to fetch HTML content from a URL using `requests`.
    - [ ] Add retry logic for network failures.
  - [ ] Implement a parser function using `BeautifulSoup`:
    - [ ] Extract details: Show Title, Venue, Sale Dates, Performance Dates, Pricing, Genre/Description, Booking Link.
    - [ ] Structure data as a dictionary or custom data class.
- [ ] **Unit Tests for Static Scraper**
  - [ ] Create tests in `tests/` using sample HTML to verify parsing accuracy.

### Dynamic Scraping with Selenium
- [ ] **Dynamic Scraper Module (`scraper_dynamic.py`)**
  - [ ] Initialize and configure Selenium WebDriver.
  - [ ] Load dynamic webpages (e.g., RSC) and wait for elements.
  - [ ] Extract the same show details as in the static scraper.
  - [ ] Implement error handling and logging for page load or element failures.
- [ ] **Unit Tests for Dynamic Scraper**
  - [ ] Write tests to simulate dynamic page 
