#!/usr/bin/env bash
# ==============================================================================
# TOEIC ADAPTIVE COACH - AUTOMATED UBUNTU SERVER VM PROVISIONING SCRIPT
# ==============================================================================
# Hỗ trợ: Ubuntu Server 22.04 LTS / 24.04 LTS trên Proxmox VE (100% Local Storage)
# Sử dụng:
#   chmod +x scripts/setup_ubuntu_server.sh
#   sudo ./scripts/setup_ubuntu_server.sh
# ==============================================================================

set -e

echo "=========================================================="
echo "  BẮT ĐẦU THIẾT LẬP MÁY CHỦ UBUNTU SERVER CHO DỰ ÁN TOEIC "
echo "=========================================================="

if [ "$EUID" -ne 0 ]; then
  echo "[ERROR] Vui lòng chạy script với quyền root (sudo ./scripts/setup_ubuntu_server.sh)!"
  exit 1
fi

CURRENT_USER="${SUDO_USER:-$USER}"
APP_DIR="/opt/toeic"
CONTAINER_GID="1001" # GID của user nextjs trong toeic-web Docker container

# 1. CẬP NHẬT HỆ THỐNG VÀ CÀI ĐẶT CÁC GÓI BẮT BUỘC
echo -e "\n[*] 1/6. Cập nhật hệ thống và cài đặt công cụ cần thiết (ffmpeg, samba, git)..."
apt-get update -y
apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    ffmpeg \
    samba \
    htop \
    ufw \
    python3 \
    python3-pip \
    python3-venv

# 2. CÀI ĐẶT DOCKER & DOCKER COMPOSE CHÍNH THỨC
echo -e "\n[*] 2/6. Cài đặt Docker Engine & Docker Compose Plugin..."
if ! command -v docker &> /dev/null; then
    mkdir -m 0755 -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    usermod -aG docker "$CURRENT_USER"
    systemctl enable docker
    systemctl start docker
    echo "  [✓] Đã cài đặt Docker thành công!"
else
    echo "  [✓] Docker đã được cài đặt sẵn."
fi

# 3. THIẾT LẬP THƯ MỤC DỮ LIỆU THỐNG NHẤT (/opt/toeic/data) & PHÂN QUYỀN UID 1001
echo -e "\n[*] 3/6. Chuẩn bị thư mục dữ liệu thống nhất tại $APP_DIR/data..."
mkdir -p \
    "$APP_DIR/data/raw" \
    "$APP_DIR/data/exams" \
    "$APP_DIR/data/media/audio" \
    "$APP_DIR/data/media/images" \
    "$APP_DIR/data/user" \
    "$APP_DIR/backups"

chown -R "$CURRENT_USER:$CURRENT_USER" "$APP_DIR"
# Cho phép container toeic-web (UID/GID 1001) và user Ubuntu cùng ghi an toàn vào data/user & data/raw
chown -R "$CURRENT_USER:$CONTAINER_GID" "$APP_DIR/data/user" "$APP_DIR/data/raw"
chmod -R 2775 "$APP_DIR/data/user" "$APP_DIR/data/raw"
chmod -R a+rX "$APP_DIR/data/exams" "$APP_DIR/data/media"
chmod +x "$APP_DIR/crawler/run_crawler.sh" "$APP_DIR/scripts/backup_data.sh" 2>/dev/null || true

# 4. CẤU HÌNH SAMBA SHARE CHO MÁY WINDOWS KÉO THẢ ĐỀ THI (data/raw)
echo -e "\n[*] 4/6. Cấu hình Samba Share (\\<IP>\toeic-tests -> $APP_DIR/data/raw)..."
SMB_CONF="/etc/samba/smb.conf"
if ! grep -q "\[toeic-tests\]" "$SMB_CONF"; then
    cat <<EOF >> "$SMB_CONF"

# TOEIC Raw Data Share for Windows Fast Copy
[toeic-tests]
   comment = TOEIC Raw Materials Folder
   path = $APP_DIR/data/raw
   browseable = yes
   read only = no
   guest ok = yes
   create mask = 0664
   directory mask = 2775
   force user = $CURRENT_USER
   force group = $CONTAINER_GID
EOF
    systemctl restart smbd
    echo "  [✓] Đã cấu hình và kích hoạt Samba Share!"
else
    sed -i "s|path = $APP_DIR/crawler/raw_data|path = $APP_DIR/data/raw|g" "$SMB_CONF"
    systemctl restart smbd
    echo "  [✓] Đã cập nhật đường dẫn Samba Share sang $APP_DIR/data/raw."
fi

# 5. CẤU HÌNH PYTHON VENV CHO PIPELINE CÀO ĐỀ TRÊN HOST
echo -e "\n[*] 5/6. Thiết lập môi trường Python venv cho Crawler..."
VENV_DIR="$APP_DIR/venv"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
"$VENV_DIR/bin/pip" install --upgrade pip
if [ -f "$APP_DIR/crawler/requirements.txt" ]; then
    "$VENV_DIR/bin/pip" install -r "$APP_DIR/crawler/requirements.txt"
fi
chown -R "$CURRENT_USER:$CURRENT_USER" "$VENV_DIR"
echo "  [✓] Môi trường Python venv đã sẵn sàng!"

# 6. MỞ TƯỜNG LỬA (UFW)
echo -e "\n[*] 6/6. Cấu hình tường lửa UFW..."
ufw allow 22/tcp     comment "SSH"
ufw allow 80/tcp     comment "TOEIC Web App HTTP"
ufw allow 443/tcp    comment "HTTPS"
ufw allow 139/tcp    comment "Samba NetBIOS"
ufw allow 445/tcp    comment "Samba SMB"
ufw --force enable

SERVER_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "=========================================================="
echo "       ✓ THIẾT LẬP MÁY CHỦ UBUNTU HOÀN TẤT THÀNH CÔNG!     "
echo "=========================================================="
echo "1. Địa chỉ truy cập Web: http://$SERVER_IP"
echo "2. Khởi chạy Docker Compose:"
echo "   cd $APP_DIR && docker compose up -d --build"
echo ""
echo "3. Kéo thả đề thi mới từ Windows:"
echo "   \\\\$SERVER_IP\\toeic-tests (lưu vào $APP_DIR/data/raw)"
echo ""
echo "4. Chạy Crawler bóc tách đề mới (xong chỉ cần F5 Web, không cần restart Docker):"
echo "   cd $APP_DIR && ./crawler/run_crawler.sh \"data/raw/TEST 5 - ETS 2023\""
echo ""
echo "5. Backup dữ liệu học tập cá nhân (data/user):"
echo "   cd $APP_DIR && ./scripts/backup_data.sh"
echo "=========================================================="
