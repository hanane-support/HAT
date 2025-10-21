from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import subprocess
import re
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# --- 전역 상태 및 경로 ---
CADDYFILE_PATH = "/etc/caddy/Caddyfile"
FASTAPI_PROXY_URL = "127.0.0.1:8000"

# 인메모리 설정 상태 (서버 재시작 시 초기화됨)
settings_status = {
    "domain_name": "",
    "domain_linked": False,
    "security_applied": False,
    "last_saved_time": None
}

# TradingView IP 목록 (2024년 10월 기준)
TRADINGVIEW_IPS = [
    "52.89.214.238", "34.212.75.30", 
    "54.218.53.128", "52.32.178.7"
]

class DomainInput(BaseModel):
    domain: str

class SecurityInput(BaseModel):
    local_ip: str

# --- Caddy 관리 함수 ---

def execute_caddy_command(command: str):
    """Caddy 명령어를 실행하고 오류를 처리합니다."""
    try:
        # Caddyfile 관리는 root 권한이 필요하므로 sudo를 사용합니다.
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        logger.info(f"Caddy command success: {command}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Caddy command failed: {command}\n{e.stderr}")
        error_detail = f"Caddy 명령어 실행 실패: {e.stderr.strip() or '알 수 없는 오류'}"
        # 사용자에게 Caddyfile 구문 오류를 전달
        raise HTTPException(status_code=500, detail=error_detail)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Caddy 실행 파일을 찾을 수 없습니다. 설치를 확인하세요.")

def write_caddyfile(content: str):
    """Caddyfile을 덮어쓰기 합니다. (sudo tee 사용)"""
    escaped_content = content.strip().replace('"', '\\"').replace('\n', '\\n')
    command = f'echo -e "{escaped_content}" | sudo tee {CADDYFILE_PATH}'
    
    try:
        execute_caddy_command(command)
    except HTTPException:
        # 이미 execute_caddy_command에서 예외 처리됨
        raise

# --- API 엔드포인트 ---

@router.get("/api/status")
async def get_status():
    """현재 설정 상태를 반환합니다."""
    return settings_status

@router.post("/api/link_domain")
async def link_domain(input: DomainInput):
    """도메인을 Caddyfile에 등록하고 서비스를 다시 로드합니다."""
    domain = input.domain.strip().lower() 
    if not re.match(r"^[a-z0-9.-]+\.[a-z]{2,}$", domain):
        raise HTTPException(status_code=400, detail="유효하지 않은 도메인 형식입니다.")

    # 1. Caddyfile 생성 (HTTPS 인증서 발급을 위한 최소 설정)
    caddyfile_content = f"""
{domain} {{
    # 리버스 프록시 설정
    reverse_proxy {FASTAPI_PROXY_URL}
}}
"""
    write_caddyfile(caddyfile_content)
    
    # 2. Caddy 서비스 활성화 및 재시작 (새로운 Caddyfile 로드 및 인증서 발급 시도)
    execute_caddy_command("sudo systemctl enable caddy")
    execute_caddy_command("sudo systemctl restart caddy") 

    # 3. 상태 업데이트
    settings_status["domain_name"] = domain
    settings_status["domain_linked"] = True
    settings_status["security_applied"] = False
    settings_status["last_saved_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return {"status": "success", "message": f"'{domain}' 도메인 연동 성공. HTTPS 인증서 발급이 완료되었는지 확인하세요."}

@router.post("/api/apply_security")
async def apply_security(input: SecurityInput):
    """트레이딩뷰 IP 및 로컬 IP를 추가하여 보안을 적용합니다."""
    
    if not settings_status["domain_linked"]:
        raise HTTPException(status_code=400, detail="도메인 연동이 먼저 필요합니다.")
        
    domain = settings_status["domain_name"]
    local_ip = input.local_ip.strip()
    
    # IP 유효성 검사
    if local_ip and not re.match(r"^(\d{1,3}\.){3}\d{1,3}$", local_ip):
         raise HTTPException(status_code=400, detail="유효하지 않은 로컬 IP 형식입니다.")

    # IP 목록 정리 (TradingView IP + Local Admin IP)
    allowed_ips = TRADINGVIEW_IPS.copy()
    if local_ip:
        allowed_ips.append(local_ip)
    
    ip_list_str = " ".join(allowed_ips)

    # 1. 보안이 적용된 Caddyfile 생성 (remote_ip 필터링)
    caddyfile_content = f"""
{domain} {{
    # 허용된 IP 목록 정의 (TradingView IP와 관리자 로컬 IP)
    @allowed {{
        remote_ip {ip_list_str}
    }}

    # 허용되지 않은 IP는 403 Forbidden 반환
    handle not @allowed {{
        respond "403 Forbidden - Access Denied" 403
    }}
    
    # 허용된 IP에 대해서만 FastAPI로 리버스 프록시
    reverse_proxy @allowed {FASTAPI_PROXY_URL}
}}
"""
    write_caddyfile(caddyfile_content)

    # 2. Caddy 서비스 재시작하여 변경 사항 적용
    execute_caddy_command("sudo systemctl restart caddy")

    # 3. 상태 업데이트
    settings_status["security_applied"] = True
    settings_status["last_saved_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {"status": "success", "message": f"보안 적용 완료. 총 허용 IP: {len(allowed_ips)}개."}

@router.post("/api/save_settings")
async def save_settings():
    """현재 상태를 저장합니다. (현재는 인메모리 상태 업데이트만 수행)"""
    settings_status["last_saved_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"status": "success", "message": "설정이 저장되었습니다."}
