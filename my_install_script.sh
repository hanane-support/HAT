#!/bin/bash

#----------------------------------------------------------------------
#Vultr 서버에 HATB (봇)과 HATBS (생성기)를 최초 통합 설치하는 스크립트입니다.
#Caddy를 사용하여 80/443 포트를 9000/8000 포트로 라우팅합니다.
#----------------------------------------------------------------------

#---깃허브 저장소 변수---
HATB_REPO_URL="https://github.com/hanane-support/HATB.git"
HATBS_REPO_URL="YOUR_HATBS_REPO_URL" #👈 HATBS 깃허브 주소를 입력하세요!
#-------------------

#---HATB 설정 변수 (제공해주신 코드와 일치)---
HATB_PROJECT_DIR="/home/my_hatb_bot"
HATB_UVICORN_BIN="$HATB_PROJECT_DIR/my_venv/bin/uvicorn"
ADMIN_IP="61.85.61.62" #👈 사용자님이 직접 설정한 관리자 IP
#---------------------------------------------

#트레이딩뷰 Webhook IP 목록
TV_IPS=(
"52.89.214.238"
"34.212.75.30"
"54.218.53.128"
"52.32.178.7"
)

#1. 서버 업데이트 및 필수 패키지 설치
sudo apt update
sudo apt install -y python3-pip python3-venv git curl debian-keyring debian-archive-keyring apt-transport-https

#2. Caddy 설치 (공식 가이드)
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/deb/caddy-stable.list' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy -y

#======================================================================
# I. HATB (봇) 설치 (포트 9000)
#======================================================================

#3. HATB 프로젝트 파일 다운로드
sudo mkdir -p $HATB_PROJECT_DIR
sudo git clone $HATB_REPO_URL $HATB_PROJECT_DIR
cd $HATB_PROJECT_DIR

#4. Python 가상 환경 설정 및 패키지 설치
python3 -m venv my_venv
source my_venv/bin/activate
pip install -r my_requirements.txt
deactivate

#5. HATB Uvicorn (FastAPI) 서비스 파일 생성
sudo tee /etc/systemd/system/my_hatb_bot.service > /dev/null <<EOF
[Unit]
Description=My HATB FastAPI App Uvicorn
After=network.target

[Service]
User=root
WorkingDirectory=$HATB_PROJECT_DIR
#포트 9000 사용
ExecStart=$HATB_UVICORN_BIN my_main:my_app --host 127.0.0.1 --port 9000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

#======================================================================
# II. HATBS (생성기) 설치 (포트 8000)
#======================================================================

HATBS_DIR="/home/hatbs_generator"

#HATBS 프로젝트 클론 및 설치
sudo mkdir -p $HATBS_DIR
sudo git clone $HATBS_REPO_URL $HATBS_DIR
cd $HATBS_DIR
python3 -m venv venv_hatbs
source venv_hatbs/bin/activate
pip install -r my_requirements.txt
deactivate

#HATBS 서비스 파일 생성
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

#======================================================================
# III. Caddy 및 서비스 활성화
#======================================================================

#6. Caddyfile 설정 적용 (HATBS 폴더에서 복사)
#Caddyfile은 9000 포트와 8000 포트 라우팅이 모두 포함된 버전이어야 합니다.
sudo cp $HATBS_DIR/my_Caddyfile /etc/caddy/Caddyfile

#7. 서비스 활성화 및 시작
sudo systemctl daemon-reload
sudo systemctl start my_hatb_bot hatbs_generator
sudo systemctl enable my_hatb_bot hatbs_generator
sudo systemctl restart caddy
sudo systemctl enable caddy

#======================================================================
# IV. 방화벽 설정 (HATB에서 제공된 강력한 보안 규칙 적용)
#======================================================================

#8. 방화벽 설정 (UFW) - 강력한 보안 적용
sudo ufw default deny incoming
sudo ufw default allow outgoing

#A. SSH (22번 포트) 허용: 오직 관리자 IP에서만 접속 허용
sudo ufw allow proto tcp from $ADMIN_IP to any port 22

#B. HTTP/HTTPS (80/443번 포트) 허용: 관리자 페이지 및 웹훅 수신
#   1. 관리자 IP 웹 접속 허용
sudo ufw allow proto tcp from $ADMIN_IP to any port 80
sudo ufw allow proto tcp from $ADMIN_IP to any port 443

#   2. 트레이딩뷰 IP 목록 (웹훅 수신용) 허용
for ip in "${TV_IPS[@]}"; do
sudo ufw allow proto tcp from $ip to any port 80
sudo ufw allow proto tcp from $ip to any port 443
done

#방화벽 활성화
sudo ufw enable -y















# #!/bin/bash

# # ----------------------------------------------------
# # ⚠️ 사용자 정의 변수: 여기에 정확한 GitHub URL을 입력하세요.
# # ----------------------------------------------------
# HATB_REPO_URL="https://github.com/hanane-support/HATB.git"        # 👈 HATB 프로젝트 깃허브 주소
# HATBS_REPO_URL="https://github.com/hanane-support/HATBS.git"      # 👈 HATBS 프로젝트 깃허브 주소 (수정 필요)
# # ----------------------------------------------------

# HATB_DIR="/home/hatb_bot"
# HATBS_DIR="/home/hatbs_generator"
# PYTHON_BIN="/usr/bin/python3"

# # 1. 서버 업데이트 및 필수 패키지 설치
# sudo apt update
# sudo apt install -y python3-pip python3-venv git curl debian-keyring debian-archive-keyring apt-transport-https

# # 2. Caddy 설치 
# curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
# curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/deb/caddy-stable.list' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
# sudo apt update
# sudo apt install caddy -y

# # 3. 프로젝트 클론 및 공통 환경 설정

# # 3-1. HATB (봇) 프로젝트 클론 및 설치 (포트 9000)
# sudo mkdir -p $HATB_DIR
# sudo git clone $HATB_REPO_URL $HATB_DIR
# cd $HATB_DIR
# python3 -m venv venv_hatb
# source venv_hatb/bin/activate
# pip install -r requirements.txt 
# deactivate

# # 3-2. HATBS (생성기) 프로젝트 클론 및 설치 (포트 8000)
# sudo mkdir -p $HATBS_DIR
# sudo git clone $HATBS_REPO_URL $HATBS_DIR
# cd $HATBS_DIR
# python3 -m venv venv_hatbs
# source venv_hatbs/bin/activate
# pip install -r my_requirements.txt 
# deactivate

# # 4. Systemd 서비스 파일 생성 및 설정 (포트 9000 및 8000 사용)

# # 4-1. HATB 서비스 (9000)
# sudo tee /etc/systemd/system/hatb_bot.service > /dev/null <<EOF
# [Unit]
# Description=HATB Bot Service (Port 9000)
# After=network.target

# [Service]
# User=root
# WorkingDirectory=$HATB_DIR
# ExecStart=$HATB_DIR/venv_hatb/bin/uvicorn my_main:my_app --host 127.0.0.1 --port 9000
# Restart=always

# [Install]
# WantedBy=multi-user.target
# EOF

# # 4-2. HATBS 서비스 (8000)
# sudo tee /etc/systemd/system/hatbs_generator.service > /dev/null <<EOF
# [Unit]
# Description=HATBS Generator Service (Port 8000)
# After=network.target

# [Service]
# User=root
# WorkingDirectory=$HATBS_DIR
# ExecStart=$HATBS_DIR/venv_hatbs/bin/uvicorn my_generator_main:my_app --host 127.0.0.1 --port 8000
# Restart=always

# [Install]
# WantedBy=multi-user.target
# EOF

# # 5. Caddyfile 설정 적용 (HATBS 폴더에서 복사)
# sudo cp $HATBS_DIR/my_Caddyfile /etc/caddy/Caddyfile 

# # 6. 서비스 활성화 및 시작
# sudo systemctl daemon-reload
# sudo systemctl start hatb_bot hatbs_generator
# sudo systemctl enable hatb_bot hatbs_generator

# # Caddy 재시작 및 활성화
# sudo systemctl restart caddy 
# sudo systemctl enable caddy

# # 7. 방화벽 설정 (UFW)
# sudo ufw default deny incoming
# sudo ufw default allow outgoing
# sudo ufw allow 80/tcp
# sudo ufw allow 443/tcp
# sudo ufw allow 22/tcp
# sudo ufw enable -y