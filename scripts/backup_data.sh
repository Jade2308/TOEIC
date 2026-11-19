#!/usr/bin/env bash
# ==============================================================================
# TOEIC Adaptive Coach - Personal User Data Backup Script
# Đóng gói toàn bộ data/user/ (mistakes, vocab_srs, progress) và tự giữ 14 bản gần nhất
# Có thể gắn crontab hàng ngày lúc 02:00:
#   0 2 * * * /opt/toeic/scripts/backup_data.sh
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"
USER_DATA_DIR="$APP_DIR/data/user"
BACKUP_DIR="$APP_DIR/backups"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
ARCHIVE="$BACKUP_DIR/toeic-user-data-$TIMESTAMP.tar.gz"

mkdir -p "$BACKUP_DIR"

if [ ! -d "$USER_DATA_DIR" ]; then
    echo "[WARN] Không tìm thấy thư mục $USER_DATA_DIR"
    exit 1
fi

tar -czf "$ARCHIVE" -C "$APP_DIR/data" user
echo "[✓] Đã tạo bản sao lưu: $ARCHIVE"

# Giữ tối đa 14 bản backup gần nhất
ls -1t "$BACKUP_DIR"/toeic-user-data-*.tar.gz 2>/dev/null | tail -n +15 | xargs -r rm -f
