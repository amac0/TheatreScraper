# Setting Up Systemd Timer for Theater Scraper in Silverblue

This guide explains how to set up a systemd timer to run the Theater Scraper automatically at 7 AM each morning on Fedora Silverblue.

## Prerequisites

- You have Fedora Silverblue installed
- You have a toolbox (e.g., named "theater-toolbox") with the Theater Scraper installed
- The Theater Scraper is located at `/var/home/a/Code/TheatreScraper`
- Your username is 'a' (adjust path as needed if different)

## Step 1: Create Required Directories (On Host System, Not In Toolbox)

First, make sure you have the directory for user systemd units:

```bash
# Run this on the host system (not in toolbox)
mkdir -p ~/.config/systemd/user/
```

## Step 2: Create the Service File (On Host System)

Create a systemd service file that will define how to run the script:

```bash
# Run this on the host system (not in toolbox)
nano ~/.config/systemd/user/theater-scraper.service
```

Add the following content to the file, changing the toolbox name if needed:

```ini
[Unit]
Description=London Theater Scraper Service
After=network.target

[Service]
Type=oneshot
# Replace 'theater-toolbox' with the name of your toolbox if different
ExecStart=/usr/bin/toolbox enter -c theater-toolbox /var/home/a/Code/TheatreScraper/theater_scraper.sh
WorkingDirectory=/var/home/a/Code/TheatreScraper

[Install]
WantedBy=multi-user.target
```

Save the file and exit (Ctrl+O, Enter, Ctrl+X in nano).

## Step 3: Create the Timer File (On Host System)

Now create a timer file that schedules when to run the service:

```bash
# Run this on the host system (not in toolbox)
nano ~/.config/systemd/user/theater-scraper.timer
```

Add the following content to run the script at 7 AM every day:

```ini
[Unit]
Description=Run Theater Scraper daily at 7AM

[Timer]
OnCalendar=*-*-* 07:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Save the file and exit.

## Step 4: Enable and Start the Timer (On Host System)

After creating both files, enable and start the timer:

```bash
# Run this on the host system (not in toolbox)
systemctl --user daemon-reload
systemctl --user enable theater-scraper.timer
systemctl --user start theater-scraper.timer
```

## Step 5: Verify the Timer (On Host System)

Verify that the timer is correctly set up:

```bash
# Run this on the host system (not in toolbox)
systemctl --user list-timers theater-scraper.timer
```

You should see information about when the timer will next run.

## Step 6: Make Sure Theater Scraper Script is Executable (Inside Toolbox)

Ensure the theater_scraper.sh script is executable:

```bash
# Run this inside the toolbox
toolbox enter theater-toolbox
cd /var/home/a/Code/TheatreScraper
chmod +x theater_scraper.sh
exit
```

## Monitoring and Troubleshooting

### Check Timer Status

```bash
# Run this on the host system (not in toolbox)
systemctl --user status theater-scraper.timer
```

### Check Service Status (after a run)

```bash
# Run this on the host system (not in toolbox)
systemctl --user status theater-scraper.service
```

### View Logs

```bash
# Run this on the host system (not in toolbox)
journalctl --user -u theater-scraper.service
```

### Manual Run for Testing

To test the service without waiting for the timer:

```bash
# Run this on the host system (not in toolbox)
systemctl --user start theater-scraper.service
```

## Important Notes

1. The service runs on the host system but executes the script inside the toolbox.
2. The timer runs in your user's context, so it will only run when you are logged in.
3. If you want it to run regardless of whether you're logged in, you need to enable lingering for your user:

```bash
# Run this on the host system as root (not in toolbox)
sudo loginctl enable-linger $USER
```

4. If you update the Theater Scraper code, you don't need to restart the timer - it will use the updated code on the next run.

5. If you change the timer or service files, you need to reload:

```bash
# Run this on the host system (not in toolbox)
systemctl --user daemon-reload
```