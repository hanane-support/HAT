from flask import Flask, render_template
from flask_admin import Admin, BaseView, expose

# --- 기본 설정 ---

# Flask 애플리케이션 인스턴스 생성
app = Flask(__name__)

# Flask-Admin의 보안 및 세션 관리를 위해 SECRET_KEY는 필수입니다.
app.config['SECRET_KEY'] = 'your_super_secret_key_for_admin'

# ⭐ 수정된 부분: FLASK_ADMIN_SWATCH를 'darkly'로 설정
# 'darkly' 외에도 'cyborg', 'slate', 'superhero' 등을 시도해 볼 수 있습니다.
app.config['FLASK_ADMIN_SWATCH'] = 'darkly' 


# --- 관리자 페이지 뷰 설정 ---

# 대시보드 뷰
class AdminDashboardView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/master.html', name='Admin Dashboard')

# 웹훅 수신 기록 관리 페이지
class WebhookLogView(BaseView):
    def is_visible(self):
        return True
    
    @expose('/')
    def index(self):
        log_data = ["웹훅 수신 기록 1", "웹훅 수신 기록 2"]
        return self.render('admin/list.html', data=log_data, title="웹훅 수신 기록")


# --- Flask-Admin 초기화 및 뷰 추가 ---

# ⭐ 수정된 부분: template_mode를 'bootstrap4'로 명시적으로 지정
admin = Admin(
    app, 
    name='HAT AutoBot Admin', 
    template_mode='bootstrap4', # Bootstrap 4를 사용해 다크 테마 ('darkly') 호환성 확보
    url='/admin' 
)

admin.add_view(AdminDashboardView(name='대시보드', endpoint='dashboard'))
admin.add_view(WebhookLogView(name='웹훅 기록', endpoint='webhooklog'))


# --- 일반 Flask 라우트 설정 ---

@app.route('/')
def home():
    # templates/index.html 파일을 렌더링합니다.
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook_receiver():
    return {"status": "ok", "message": "Webhook received (Dummy)"}, 200

# --- 애플리케이션 실행 (로컬 테스트용) ---

if __name__ == '__main__':
    print(f"관리자 페이지: http://127.0.0.1:5000/admin")
    app.run(debug=True)