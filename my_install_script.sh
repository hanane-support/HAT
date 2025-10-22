#!/bin/bash

# --- 설정 변수 ---
REPO_URL="https://github.com/hanane-support/HATB.git"
PROJECT_DIR="/home/my_hatb_bot"
PYTHON_BIN="$PROJECT_DIR/my_venv/bin/python3"
UVICORN_BIN="$PROJECT_DIR/my_venv/bin/uvicorn"

# --- 허용할 IP 목록 (사용자 IP 자동 삽입) ---
ADMIN_IP="61.85.61.62"

# 2. 트레이딩뷰 Webhook IP 목록
TV_IPS=(
    "52.89.214.238"
    "34.212.75.30"
    "54.218.53.128"
    "52.32.178.7"
)

# 1. 서버 업데이트 및 필수 패키지 설치
sudo apt update
sudo apt install -y python3-pip python3-venv git curl debian-keyring debian-archive-keyring apt-transport-https

# 2. Caddy 설치 (공식 가이드)
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/deb/caddy-stable.list' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy -y

# 3. 프로젝트 파일 다운로드
sudo mkdir -p $PROJECT_DIR
sudo git clone $REPO_URL $PROJECT_DIR
cd $PROJECT_DIR

# 4. Python 가상 환경 설정 및 패키지 설치
python3 -m venv my_venv
source my_venv/bin/activate
pip install -r my_requirements.txt
deactivate

# 5. Uvicorn (FastAPI) 서비스 파일 생성
sudo tee /etc/systemd/system/my_hatb_bot.service > /dev/null <<EOF
[Unit]
Description=My HATB FastAPI App Uvicorn
After=network.target

[Service]
User=root
WorkingDirectory=$PROJECT_DIR
# 포트 9000 사용
ExecStart=$UVICORN_BIN my_main:my_app --host 127.0.0.1 --port 9000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 6. Caddyfile 설정 적용
sudo cp $PROJECT_DIR/my_Caddyfile /etc/caddy/Caddyfile 

# 7. 서비스 활성화 및 시작
sudo systemctl daemon-reload
sudo systemctl start my_hatb_bot
sudo systemctl enable my_hatb_bot
sudo systemctl restart caddy 
sudo systemctl enable caddy

# 8. 방화벽 설정 (UFW) - 강력한 보안 적용
sudo ufw default deny incoming
sudo ufw default allow outgoing

# A. SSH (22번 포트) 허용: 오직 관리자 IP에서만 접속 허용
sudo ufw allow proto tcp from $ADMIN_IP to any port 22

# B. HTTP/HTTPS (80/443번 포트) 허용: 관리자 페이지 및 웹훅 수신
#    1. 관리자 IP (집 IP) 웹 접속 허용
sudo ufw allow proto tcp from $ADMIN_IP to any port 80
sudo ufw allow proto tcp from $ADMIN_IP to any port 443

#    2. 트레이딩뷰 IP 목록 (웹훅 수신용) 허용
for ip in "${TV_IPS[@]}"; do
    sudo ufw allow proto tcp from $ip to any port 80
    sudo ufw allow proto tcp from $ip to any port 443
done

# 방화벽 활성화
sudo ufw enable -y