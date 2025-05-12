Prompt 1: Project Setup and Environment
text
Copy
# Prompt 1: Project Setup and Environment

You are to initialize the London Theater Show Scraper project. Please perform the following tasks:

1. Create a clear folder structure with directories such as:
   - src/ (for application code)
   - tests/ (for unit and integration tests)
   - config/ (for configuration files, if needed)

2. Generate a requirements.txt file that includes:
   - requests
   - beautifulsoup4
   - selenium
   - pandas
   - smtplib (or simply note that this is part of the Python standard library)
   - any other libraries you deem necessary (e.g., logging)

3. Create a basic README.md that describes the project and its purpose.

Provide the file/folder structure and the contents of these files.
Prompt 2: Configuration and Logging Module
text
Copy
# Prompt 2: Configuration and Logging Module

Now, create a configuration module (e.g. config.py) that includes:
- A list of the London theater URLs to monitor.
- Email configuration (SMTP server, port, sender email, recipient email, etc.).
- File paths for the CSV snapshots and log files.

Additionally, implement a logging setup module (e.g. logger.py) that:
- Configures a logging handler to write debug and error messages to a daily log file.
- Ensures that errors (such as network failures) are logged with timestamps.

Ensure that both configuration and logging modules are self-contained and importable in later modules.
Prompt 3: Static Page Scraping with BeautifulSoup
text
Copy
# Prompt 3: Static Page Scraping with BeautifulSoup

Develop a module (e.g. scraper_static.py) that implements the following:
- A generic function that takes a URL and returns the HTML content using the requests library (include retry logic).
- A function that uses BeautifulSoup to parse the HTML and extract show details: Show Title, Venue, Sale Dates, Performance Dates, Pricing Information, Genre/Description, and Booking Page Link.
- Structure the extracted data as a dictionary (or a custom data class) so that it can be easily stored later.

Also, create unit tests in tests/ for this module using sample HTML snippets to ensure the parsing logic works correctly. Those sample HTML pages should be either provided with the prompt or retrieved from the internet.
Prompt 4: Dynamic Page Scraping with Selenium
text
Copy
# Prompt 4: Dynamic Page Scraping with Selenium

Create a module (e.g. scraper_dynamic.py) to handle pages that require JavaScript rendering. This module should:
- Initialize a Selenium WebDriver.
- Load the dynamic webpage (for example, the RSC website) and wait for the required elements to load.
- Extract the same show details (Show Title, Venue, Sale Dates, etc.) as in the static scraper.
- Return the extracted data in the same format as the static scraper for consistency.

Include basic error handling and logging (using the logger module) to handle cases where the page fails to load or elements are not found.
Prompt 5: CSV Storage and Snapshot Comparison Module
text
Copy
# Prompt 5: CSV Storage and Snapshot Comparison Module

Develop a module (e.g. data_storage.py) that handles:
- Saving the current day's snapshot of show listings to a CSV file using pandas.
- Loading the previous snapshot from a CSV file.
- Comparing the current snapshot to the previous one to detect:
  - Newly added shows.
  - Changes in sale/performance dates or ticket availability.
  - Optionally, unchanged listings for reporting purposes.

Include unit tests in tests/ that simulate snapshot files and verify that the comparison logic accurately detects differences.
Prompt 6: Email Notification Module
text
Copy
# Prompt 6: Email Notification Module

Build a module (e.g. notifier.py) that:
- Composes an email report summarizing:
  - Newly detected shows.
  - Updated listings (changed dates or ticket availability).
  - A summary of ongoing unchanged listings.
  - A list of errors or issues encountered during scraping.
- Sends the email using smtplib, with the configuration details from the configuration module.
- Incorporates error handling for SMTP issues (e.g., connection errors).

Also, write tests (in tests/) to simulate email content generation (you may mock the actual sending function).
Prompt 7: Integration – Main Script Assembly
text
Copy
# Prompt 7: Integration – Main Script Assembly

Create the main script (e.g. main.py) that ties all the modules together. The main script should:
- Load configuration and initialize logging.
- Iterate through the list of websites:
  - Decide whether to use the static scraper or dynamic scraper based on the URL or a predefined setting.
  - Collect all show data.
- Save the newly scraped data to a CSV snapshot.
- Load the previous snapshot and perform the change detection.
- Generate an email report detailing:
  - New shows
  - Updated listings
  - Unchanged listings
  - Errors encountered
- Send the email report.
- Log each step of the process for debugging and record-keeping.

Ensure that the main script calls each module in a clear, sequential manner and that integration tests (in tests/) can simulate an end-to-end run.
Prompt 8: Unit and Integration Testing
text
Copy
# Prompt 8: Unit and Integration Testing

Create tests in the tests/ directory that cover:
- **Unit Tests:**
  - For each scraping function (static and dynamic) using sample HTML.
  - For the CSV storage module to ensure correct saving and comparison.
  - For the email module to verify email content generation.
- **Integration Tests:**
  - An end-to-end test that simulates a full run of the main script:
    - Use dummy data to mimic a snapshot.
    - Simulate a change between runs.
    - Confirm that the email content correctly reflects the changes.
  - Simulate error conditions such as unreachable websites or missing HTML elements and ensure proper logging and reporting.

The tests should be written to run automatically (e.g. using pytest) and provide clear outputs on pass/failure.
Prompt 9: Deployment Instructions and Cron Job Setup
text
Copy
# Prompt 9: Deployment Instructions and Cron Job Setup

Provide documentation (e.g. in a DEPLOYMENT.md file) that includes:
- Steps to deploy the script on a Linux machine.
- How to install dependencies and set up the virtual environment.
- Instructions for scheduling the main.py script to run daily using cron:
  - Include a sample cron job entry.
- Any additional deployment considerations (e.g., environment variables, file permissions).

This file should be clear enough that someone unfamiliar with the project can set it up and run it.
