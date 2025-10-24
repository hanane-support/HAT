# my_main.py (my_main.py와 my_app.py 통합 버전)

import subprocess
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# ----------------------------------------------------------------------
# 1. 초기 설정 및 전역 변수
# ----------------------------------------------------------------------

# 템플릿 폴더 경로 설정 (my_templates 폴더는 프로젝트 루트에 있다고 가정)
templates = Jinja2Templates(directory="my_templates")

# FastAPI 애플리케이션 인스턴스
my_app = FastAPI()

# ⚠️ [필수 수정] Caddyfile의 실제 경로 (Vultr 스크립트에서 확인된 경로)
CADDYFILE_PATH = "/etc/caddy/Caddyfile"

# ⚠️ [필수 확인/수정] Caddy 서비스를 강제 재시작하는 명령어
CADDY_RESTART_COMMAND = ["sudo", "systemctl", "restart", "caddy"] 
# (이 명령은 FastAPI 프로세스가 비밀번호 없이 실행할 수 있도록 sudoers 파일에 설정되어야 합니다.)

# Pydantic 모델: 프론트엔드에서 도메인 이름을 받을 때 사용
class DomainUpdate(BaseModel):
    domain: str


# ----------------------------------------------------------------------
# 2. 핵심 로직 함수 (Caddyfile 업데이트 및 서비스 재시작)
# ----------------------------------------------------------------------

def update_my_caddyfile(domain: str):
    """
    Caddyfile을 읽고 도메인 설정을 새 도메인으로 덮어씁니다.
    """
    # Vultr 스크립트에서 설정된 FastAPI 리스너 포트를 8000으로 가정합니다.
    fastapi_port = 8000
    
    # 새 Caddyfile 내용: 도메인에 80/443 포트 자동 적용 및 리버스 프록시 설정
    new_caddyfile_content = f"""
{domain} {{
    reverse_proxy 127.0.0.1:{fastapi_port}
}}
"""
    
    # 파일 쓰기
    with open(CADDYFILE_PATH, "w") as f:
        f.write(new_caddyfile_content.strip())
    
    print(f"Caddyfile 업데이트 완료. 새 도메인: {domain}")


def restart_caddy_service():
    """
    Caddy 서버를 강제 재시작하여 새 설정을 적용하고 인증서 발급을 유도합니다.
    """
    command_str = ' '.join(CADDY_RESTART_COMMAND)
    print(f"Caddy 서비스 강제 재시작 명령 실행 중: {command_str}")
    
    # shell=True를 사용하여 명령 실행 (보안 경고가 적용되는 지점)
    result = subprocess.run(command_str, check=True, capture_output=True, text=True, shell=True)
    
    print(f"Caddy 서비스 재시작 명령 성공. 출력: {result.stdout.strip() if result.stdout else 'No output'}")


# ----------------------------------------------------------------------
# 3. 라우팅 정의
# ----------------------------------------------------------------------

# 3-1. 관리자 페이지 라우트 (GET)

# 소개 페이지
@my_app.get("/admin/intro")
async def intro_page(request: Request):
    return templates.TemplateResponse("my_intro.html", {"request": request, "title": "서비스 소개"})

# 관리자 페이지 (기본 - 웹훅 내역)
@my_app.get("/admin")
async def admin_page(request: Request):
    return templates.TemplateResponse("my_admin.html", {"request": request, "title": "Hanane Auto Trading 관리자 페이지"})

# 도메인 연결 및 보안 페이지 (GET)
@my_app.get("/admin/domain")
async def domain_security_page(request: Request):
    # my_main.py의 기존 GET 경로를 유지합니다.
    return templates.TemplateResponse("my_domain.html", {"request": request, "title": "도메인 연결 및 보안"})
    
# 3-2. 도메인 업데이트 API 라우트 (POST)

@my_app.post("/admin/update-my_domain")
async def update_my_domain_and_caddy_api(data: DomainUpdate):
    """
    도메인 정보를 받아 Caddyfile을 업데이트하고 Caddy 서비스를 재시작하는 API 엔드포인트입니다.
    """
    new_domain = data.domain.strip()

    if not new_domain:
        raise HTTPException(status_code=400, detail="도메인 이름을 입력해야 합니다.")

    # ⚠️ [중요] 여기에 로그인 인증/권한 확인 로직이 추가되어야 합니다.

    try:
        # 1. Caddyfile 내용 업데이트
        update_my_caddyfile(new_domain)

        # 2. Caddy 서비스 재시작 (새 설정 적용 및 인증서 발급 유도)
        restart_caddy_service()

        # 최종 성공 메시지 반환
        return {"message": "Domain update request received"}

    except PermissionError:
        raise HTTPException(status_code=500, detail="**치명적 오류:** Caddyfile 쓰기 또는 서비스 재시작 권한이 부족합니다. 서버 로그와 권한 설정을 확인하세요.")
    except subprocess.CalledProcessError as e:
        error_detail = f"Caddy 재시작 실패. 오류: {e.stderr.strip()}"
        print(f"Caddy 재시작 오류: {error_detail}")
        raise HTTPException(status_code=500, detail=f"Caddy 설정 업데이트 실패. {error_detail}")
    except Exception as e:
        print(f"예상치 못한 서버 오류: {e}")
        raise HTTPException(status_code=500, detail=f"예상치 못한 서버 오류가 발생했습니다. {e}")


# ----------------------------------------------------------------------
# 4. 서버 실행
# ----------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    # 로컬 테스트 및 Vultr 스크립트 실행 환경을 고려하여 9000 포트에서 실행합니다.
    # Vultr 스크립트의 MAIN_APP_PATH="my_main:my_app"에 맞추어 문자열 인수로 실행합니다.
    uvicorn.run("my_main:my_app", host="127.0.0.1", port=9000, reload=True)
