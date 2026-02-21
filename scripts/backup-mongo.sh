#!/bin/bash
# ============================================================
# MongoDB Backup Script
# Usage: bash scripts/backup-mongo.sh
# Creates a gzipped mongodump in ./backups/
# ============================================================

set -euo pipefail

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
ARCHIVE_NAME="mongo-backup-${TIMESTAMP}.gz"

mkdir -p "${BACKUP_DIR}"

echo "📦 Starting MongoDB backup..."
docker exec genai-mongo mongodump --archive="/tmp/${ARCHIVE_NAME}" --gzip

echo "📥 Copying archive to ${BACKUP_DIR}/${ARCHIVE_NAME}..."
docker cp "genai-mongo:/tmp/${ARCHIVE_NAME}" "${BACKUP_DIR}/${ARCHIVE_NAME}"

# Cleanup inside container
docker exec genai-mongo rm -f "/tmp/${ARCHIVE_NAME}"

SIZE=$(ls -lh "${BACKUP_DIR}/${ARCHIVE_NAME}" | awk '{print $5}')
echo "✅ Backup complete: ${BACKUP_DIR}/${ARCHIVE_NAME} (${SIZE})"
