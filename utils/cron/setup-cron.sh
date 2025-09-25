if ! command -v crontab &> /dev/null; then
    echo "Installing cron..."
    sudo update && sudo install -y cron
fi

# Setup cron job for automated backups
echo "0 2 * * * /BagheeraCarrom/scripts/backup.sh" > /tmp/crontab
echo "0 */6 * * * /BagheeraCarrom/scripts/backup.sh" >> /tmp/crontab  # Every 6 hours

# Install crontab
crontab /tmp/crontab

# Start cron daemon
service cron start

# Keep container running
tail -f /var/log/cron.log