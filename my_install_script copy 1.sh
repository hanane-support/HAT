# C:\Python\HATB\my_install_script.sh (Bash Script)
#!/bin/bash

# --- 설정 변수 ---
REPO_URL="https://github.com/hanane-support/HATB.git" # <<<<<< 여기에 실제 GitHub HTTPS 주소를 넣으세요.
PROJECT_DIR="/home/my_hatb_bot"
PYTHON_BIN="$PROJECT_DIR/my_venv/bin/python3"
UVICORN_BIN="$PROJECT_DIR/my_venv/bin/uvicorn"

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
# Vultr에서 root로 실행되므로 권한 설정은 생략

cd $PROJECT_DIR

# 4. Python 가상 환경 설정 및 패키지 설치
python3 -m venv my_venv
source my_venv/bin/activate
pip install -r my_requirements.txt
deactivate # 가상환경 비활성화

# 5. Uvicorn (FastAPI) 서비스 파일 생성
sudo tee /etc/systemd/system/my_hatb_bot.service > /dev/null <<EOF
[Unit]
Description=My HATB FastAPI App Uvicorn
After=network.target

[Service]
User=root
WorkingDirectory=$PROJECT_DIR
# 포트 9000으로 변경
ExecStart=$UVICORN_BIN my_main:my_app --host 127.0.0.1 --port 9000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 6. Caddyfile 설정 적용 (my_Caddyfile을 /etc/caddy/Caddyfile로 복사)
sudo cp $PROJECT_DIR/my_Caddyfile /etc/caddy/Caddyfile 

# 7. 서비스 활성화 및 시작
sudo systemctl daemon-reload
sudo systemctl start my_hatb_bot
sudo systemctl enable my_hatb_bot
sudo systemctl restart caddy 
sudo systemctl enable caddy

# 8. 방화벽 설정 (SSH, HTTP, HTTPS 허용)
# Uvicorn은 127.0.0.1 (내부)에서만 통신하므로 외부에서 9000 포트를 열 필요는 없습니다.
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable -y