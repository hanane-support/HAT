#!/bin/bash

# ----------------------------------------------------
# ⚠️ 사용자 정의 변수: 여기에 정확한 GitHub URL을 입력하세요.
# ----------------------------------------------------
HATB_REPO_URL="YOUR_HATB_REPO_URL"        # 👈 HATB 프로젝트 깃허브 주소
HATBS_REPO_URL="YOUR_HATBS_REPO_URL"      # 👈 HATBS 프로젝트 깃허브 주소 (수정 필요)
# ----------------------------------------------------

HATB_DIR="/home/hatb_bot"
HATBS_DIR="/home/hatbs_generator"
PYTHON_BIN="/usr/bin/python3"

# 1. 서버 업데이트 및 필수 패키지 설치
sudo apt update
sudo apt install -y python3-pip python3-venv git curl debian-keyring debian-archive-keyring apt-transport-https

# 2. Caddy 설치 
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/deb/caddy-stable.list' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy -y

# 3. 프로젝트 클론 및 공통 환경 설정

# 3-1. HATB (봇) 프로젝트 클론 및 설치 (포트 9000)
sudo mkdir -p $HATB_DIR
sudo git clone $HATB_REPO_URL $HATB_DIR
cd $HATB_DIR
python3 -m venv venv_hatb
source venv_hatb/bin/activate
pip install -r requirements.txt 
deactivate

# 3-2. HATBS (생성기) 프로젝트 클론 및 설치 (포트 8000)
sudo mkdir -p $HATBS_DIR
sudo git clone $HATBS_REPO_URL $HATBS_DIR
cd $HATBS_DIR
python3 -m venv venv_hatbs
source venv_hatbs/bin/activate
pip install -r my_requirements.txt 
deactivate

# 4. Systemd 서비스 파일 생성 및 설정 (포트 9000 및 8000 사용)

# 4-1. HATB 서비스 (9000)
sudo tee /etc/systemd/system/hatb_bot.service > /dev/null <<EOF
[Unit]
Description=HATB Bot Service (Port 9000)
After=network.target

[Service]
User=root
WorkingDirectory=$HATB_DIR
ExecStart=$HATB_DIR/venv_hatb/bin/uvicorn my_main:my_app --host 127.0.0.1 --port 9000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 4-2. HATBS 서비스 (8000)
sudo tee /etc/systemd/system/hatbs_generator.service > /dev/null <<EOF
[Unit]
Description=HATBS Generator Service (Port 8000)
After=network.target

[Service]
User=root
WorkingDirectory=$HATBS_DIR
ExecStart=$HATBS_DIR/venv_hatbs/bin/uvicorn my_generator_main:my_app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 5. Caddyfile 설정 적용 (HATBS 폴더에서 복사)
sudo cp $HATBS_DIR/my_Caddyfile /etc/caddy/Caddyfile 

# 6. 서비스 활성화 및 시작
sudo systemctl daemon-reload
sudo systemctl start hatb_bot hatbs_generator
sudo systemctl enable hatb_bot hatbs_generator

# Caddy 재시작 및 활성화
sudo systemctl restart caddy 
sudo systemctl enable caddy

# 7. 방화벽 설정 (UFW)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable -y