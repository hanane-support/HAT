from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates 

# 템플릿 폴더 경로 설정 (my_templates 폴더를 가리킵니다.)
templates = Jinja2Templates(directory="my_templates")

# FastAPI 애플리케이션 인스턴스
my_app = FastAPI()

# ----------------- 라우팅 정의 -----------------

# 루트 경로 (로그에서 my_index.html을 찾으려던 경로)
@my_app.get("/")
async def root(request: Request):
    # my_templates/my_index.html 파일을 사용합니다.
    return templates.TemplateResponse("my_index.html", {"request": request, "status": "Root Page Active"})

# 관리자 페이지 경로
@my_app.get("/admin")
async def admin_page(request: Request):
    # my_templates/admin.html 파일을 사용합니다.
    return templates.TemplateResponse("admin.html", {"request": request, "title": "AutoBot Admin"})

# -----------------------------------------------

if __name__ == "__main__":
    import uvicorn
    # 로컬 테스트를 위해 127.0.0.1:9000으로 실행
    uvicorn.run("my_main:my_app", host="127.0.0.1", port=9000, reload=True)