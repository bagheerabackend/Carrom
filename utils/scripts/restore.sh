#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Load environment variables
source "${PROJECT_ROOT}/.env" 2>/dev/null || true

# Configuration
DB_HOST=${MYSQL_HOST}
DB_NAME=${MYSQL_DATABASE}
DB_USER=${MYSQL_USER}
DB_PASSWORD=${MYSQL_PASSWORD}
BACKUP_DIR="/backups"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Check if backup file is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file>"
    echo "Available backups:"
    ls -la $BACKUP_DIR/carrom_backup_*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$BACKUP_DIR/$1"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    log_message "ERROR: Backup file not found: $BACKUP_FILE"
    exit 1
fi

log_message "Starting restore from: $(basename $BACKUP_FILE)"

# Wait for database to be ready
until mysqladmin ping -h"$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD" --silent; do
    log_message "Waiting for database connection..."
    sleep 2
done

# Restore backup
if zcat $BACKUP_FILE | mysql -h"$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD"; then
    log_message "Restore completed successfully"
else
    log_message "ERROR: Restore failed!"
    exit 1
fi