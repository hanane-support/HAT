#!/bin/bash

# 1. 시스템 업데이트 및 Python 설치
apt update -y
apt upgrade -y
apt install -y python3-pip python3-venv git

# 2. 프로젝트 클론 및 가상 환경 설정
PROJECT_DIR="HAT"
REPO_URL="YOUR_GITHUB_REPO_URL" # ⭐여기에 당신의 GitHub HTTPS 주소를 넣어주세요.
USER="ubuntu" 

mkdir -p /home/$USER/$PROJECT_DIR
cd /home/$USER/$PROJECT_DIR
git clone ${REPO_URL} .

python3 -m venv venv
source venv/bin/activate

# 3. 종속성 설치
/home/$USER/$PROJECT_DIR/venv/bin/pip install -r my_requirements.txt
/home/$USER/$PROJECT_DIR/venv/bin/pip install gunicorn

# 4. Systemd 서비스 파일 생성
SERVICE_FILE="/etc/systemd/system/hat_fastapi.service"

# my_main.py의 PORT 변수는 config.py의 초기값(8000)을 사용합니다.
echo "[Unit]
Description=HAT FastAPI Bot Service
After=network.target

[Service]
User=$USER
Group=$USER
Environment=\"PATH=/home/$USER/$PROJECT_DIR/venv/bin\"
WorkingDirectory=/home/$USER/$PROJECT_DIR
# my_main:app 을 실행하도록 지정합니다.
ExecStart=/home/$USER/$PROJECT_DIR/venv/bin/gunicorn my_main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target" | tee $SERVICE_FILE

# 5. 서비스 활성화 및 시작
systemctl daemon-reload
systemctl enable hat_fastapi.service
systemctl start hat_fastapi.service

# 6. 방화벽 설정 (UFW)
ufw allow 22/tcp
ufw allow 8000/tcp
ufw enable -y

echo "✅ HAT FastAPI Project deployed and running."
echo "✅ Admin panel is accessible at http://YOUR_VULTR_IP:8000/admin"