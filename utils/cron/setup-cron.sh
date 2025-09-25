echo "0 2 * * * /scripts/backup.sh" > /tmp/crontab
echo "0 */6 * * * /scripts/backup.sh" >> /tmp/crontab  # Every 6 hours
crontab /tmp/crontab
cron -f