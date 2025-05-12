**London Theater Show Scraper - Developer Specification**

## **Project Overview**
This script will monitor a list of London theater websites and notify the user via email when new shows are announced or when existing listings are updated (e.g., new sale dates or additional tickets). The script will run daily and compare extracted data against previously stored records to detect changes.

---

## **Technical Requirements**

### **1. Websites to Monitor**
The script will extract show listings from the following websites:

1. [Donmar Warehouse](https://www.donmarwarehouse.com/whats-on)
2. [Bridge Theatre](https://bridgetheatre.co.uk/performances/)
3. [National Theatre](https://www.nationaltheatre.org.uk/whats-on/)
4. [Hampstead Theatre](https://www.hampsteadtheatre.com/whats-on/main-stage/)
5. [Marylebone Theatre](https://www.marylebonetheatre.com/#Whats-On)
6. [Soho Theatre (Dean Street)](https://sohotheatre.com/dean-street/)
7. [Soho Theatre (Walthamstow)](https://sohotheatre.com/walthamstow/)
8. [Royal Shakespeare Company (RSC)](https://www.rsc.org.uk/whats-on/in/london/?from=ql)
9. [Royal Court Theatre](https://royalcourttheatre.com/whats-on/)
10. [Drury Lane Theatre](https://drurylanetheatre.com/)

---

### **2. Data to Extract**
For each show listed on the above websites, extract the following details:
- **Show Title**
- **Venue**
- **Sale Dates** (for members and general public, if available)
- **Performance Dates**
- **Pricing Information** (if listed)
- **Genre or Description**
- **Booking Page Link**

---

### **3. Scraping Approach**
- **Primary Method:** `requests` + `BeautifulSoup` for sites with static HTML.
- **Secondary Method:** `Selenium` for sites with dynamically loaded JavaScript content (e.g., RSC).
- **No Scraping Evasion:** The script will respect `robots.txt` where applicable.

---

### **4. Data Storage**
- **Format:** CSV file.
- **Snapshot-based tracking:** Each daily run captures the latest snapshot of show listings.
- **Change Detection:** Compare the new snapshot against the previously stored file to identify:
  - Newly listed shows.
  - Changes in sale/performance dates.
  - New ticket availability.

---

### **5. Error Handling & Logging**
- **Website Unreachable:** If a site is down, log the error and include it in the daily email.
- **Structure Changes:** If expected elements cannot be found, log the issue and notify the user.
- **Retries:** Implement a retry mechanism with a small delay before failing a request.
- **Logging:** Maintain a daily log file of errors and changes detected.

---

### **6. Notifications & Reporting**
- **Delivery Method:** Daily email report.
- **Email Content:**
  - **New Shows:** List of newly detected shows.
  - **Updated Listings:** Shows with changed dates or new ticket availability.
  - **Unchanged Listings:** Summary of all ongoing shows still on sale.
  - **Errors:** Any failed scrapes or structural changes that need attention.
- **Format:** Simple text-based email.

---

### **7. Testing & Deployment Plan**
#### **Unit Tests**
- Validate extraction logic for each website using sample HTML.
- Test comparison logic for detecting new and updated shows.

#### **Integration Tests**
- Verify end-to-end scraping execution, storage, and email generation.
- Simulate website failures and structural changes to test error handling.

#### **Deployment Considerations**
- **Schedule:** Run daily using a cron job (Linux) or Task Scheduler (Windows).
- **Dependencies:** Ensure required libraries (`requests`, `BeautifulSoup4`, `Selenium`, `pandas`, `smtplib`) are installed.

---

### **Next Steps**
- Develop the script according to this specification.
- Test scraping logic for each website.
- Set up email notifications.
- Deploy the script for automated daily execution.

**End of Specification**

