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
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/carrom_backup_${DATE}.sql"
RETENTION_DAYS=7

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a ${BACKUP_DIR}/backup.log
}

# Perform backup
log_message "Starting backup of database: $DB_NAME"

# Wait for database to be ready
until mysqladmin ping -h"$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD" --silent; do
    log_message "Waiting for database connection..."
    sleep 2
done

# Create backup
if mysqldump -h"$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD" \
    --single-transaction \
    --routines \
    --triggers \
    --events \
    --add-drop-database \
    --databases $DB_NAME > $BACKUP_FILE; then
    
    # Compress backup
    gzip $BACKUP_FILE
    BACKUP_FILE="${BACKUP_FILE}.gz"
    
    log_message "Backup completed successfully: $(basename $BACKUP_FILE)"
    log_message "Backup size: $(du -h $BACKUP_FILE | cut -f1)"
    
    # Remove old backups
    find $BACKUP_DIR -name "carrom_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete
    log_message "Old backups cleaned up (retention: $RETENTION_DAYS days)"
    
else
    log_message "ERROR: Backup failed!"
    exit 1
fi

log_message "Backup process completed"