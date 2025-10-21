#!/bin/bash

Vultr User Data 스크립트:

Ubuntu 24.04 LTS에서 FastAPI, Uvicorn, Caddy 및 Git을 자동으로 설치하고

GitHub에서 프로젝트를 복제하여 Systemd 서비스를 설정 및 시작합니다.

이 버전은 설치 후 Caddy를 서버 IP로 즉시 구동합니다.

--- 설정 변수 (사용자 정의 필요) ---

1. 당신의 GitHub 저장소 HTTPS URL로 수정해야 합니다.

GITHUB_REPO="https://github.com/hanane-support/HATB.git"

2. 임시 도메인 설정 (실제 도메인 설정은 웹 관리자 페이지에서 다시 이루어집니다.)

DOMAIN_NAME="your-domain.com"

3. Gunicorn을 실행할 사용자 (Vultr 기본값은 'root'입니다)

RUN_USER="root"

--- 핵심 변수 ---

PROJECT_DIR="/root/tradingview_webhook_server"
FASTAPI_PROXY_URL="127.0.0.1:8000"
SERVICE_NAME="webhook-fastapi"

--- 1. 시스템 업데이트 및 필수 패키지 설치 ---

echo "--- 1. 시스템 업데이트 및 필수 패키지 설치 시작 ---"
apt update -y
apt upgrade -y
apt install -y python3 python3-pip git curl wget

--- 2. Caddy 설치 ---

echo "--- 2. Caddy 설치 시작 ---"
apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
apt update
apt install caddy -y

이전 버전과는 달리, 관리자 페이지 접속을 위해 Caddy를 중지하지 않습니다.

--- 2.5. Caddyfile 자동 생성 및 IP 설정 (새로운 단계) ---

echo "--- 2.5. Caddyfile 자동 생성 (Vultr IP 사용) ---"
SERVER_IP=$(curl -s https://www.google.com/search?q=checkip.amazonaws.com)

서버 IP를 Hostname으로 사용하여 8000 포트의 FastAPI로 요청을 전달합니다.

이 설정으로 이제 바로 http://[IP 주소]/admin 접속이 가능해집니다.

sudo tee /etc/caddy/Caddyfile > /dev/null << EOF
http://${SERVER\_IP} {
reverse\_proxy 127.0.0.1:8000
}
EOF
echo "Caddyfile 생성 완료: Hostname=${SERVER_IP}"

--- 3. 프로젝트 코드 복제 및 의존성 설치 ---

echo "--- 3. 프로젝트 코드 복제 및 의존성 설치 시작 ---"

수정: 불필요한 이스케이프 문자() 제거 및 안정화

mkdir -p ${PROJECT_DIR}
cd ${PROJECT_DIR}
git clone ${GITHUB_REPO} .

Python 의존성 설치

pip3 install -r requirements.txt
echo "Python 의존성 설치 완료."

--- 4. Systemd 서비스 파일 생성 ---

echo "--- 4. Systemd 서비스 파일 생성 시작 ---"

수정: Systemd 구문 ([Unit] 등)의 불필요한 이스케이프 문자 제거 및 안정화

cat << EOF > /etc/systemd/system/${SERVICE_NAME}.service
[Unit]
Description=Uvicorn instance to run FastAPI Webhook Server
After=network.target

[Service]
User=${RUN_USER}
Group=www-data
WorkingDirectory=${PROJECT_DIR}

FastAPI 앱을 Gunicorn 없이 Uvicorn으로 직접 실행합니다.

ExecStart=/usr/bin/python3 -m uvicorn my_server:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

--- 5. 서비스 활성화 및 시작 ---

echo "--- 5. 서비스 활성화 및 시작 ---"
systemctl daemon-reload

수정: 불필요한 이스케이프 문자() 제거 및 안정화

systemctl enable ${SERVICE_NAME}
systemctl start ${SERVICE_NAME}
systemctl status ${SERVICE_NAME} | grep Active

Caddy 서비스도 자동으로 활성화하고 시작합니다. (2.5단계 설정 적용)

systemctl enable caddy
systemctl start caddy
systemctl status caddy | grep Active

--- 6. 방화벽 (UFW) 설정 ---

echo "--- 6. 방화벽 설정 (UFW) ---"
ufw allow 22/tcp  # SSH
ufw allow 80/tcp  # HTTP (관리자 페이지 초기 접속 및 Caddy용)
ufw allow 443/tcp # HTTPS (Caddy 최종 서비스용)
ufw --force enable
echo "UFW 방화벽 활성화 완료."

echo "--- 모든 자동 설치 및 설정 완료 ---"
echo "다음 단계: Vultr 콘솔에 스크립트를 붙여넣어 서버를 생성한 후, http://[서버 IP 주소]/admin 으로 바로 접속하세요."