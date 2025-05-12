cat > ~/test_container.sh << 'EOF'
#!/bin/bash
echo "Running test from host at $(date)"
podman exec TheatreScraper bash -c "echo 'Inside container: \$(date)'; echo 'Working dir: \$(pwd)'; ls -la 
/var/home/a/Code/TheatreScraper/theater_scraper.sh; /var/home/a/Code/TheatreScraper/theater_scraper.sh"
EOF
