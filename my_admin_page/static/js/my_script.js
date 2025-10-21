// my_admin_page/static/js/my_script.js

const API_BASE_URL = window.location.protocol + "//" + window.location.host + "/api/v1";

/**
 * 봇의 현재 상태를 API에서 가져와 업데이트합니다.
 */
async function fetchBotStatus() {
    const statusBox = document.getElementById('bot-status');
    const statusDetail = document.getElementById('status-detail');
    statusBox.textContent = "상태 확인 중...";
    statusBox.className = 'my_status_box';
    statusDetail.textContent = '';

    try {
        const response = await axios.get(`${API_BASE_URL}/status`);
        const data = response.data;

        const isRunning = data.is_core_running;
        statusBox.textContent = isRunning ? "✅ 봇 작동 중 (RUNNING)" : "❌ 봇 정지됨 (STOPPED)";
        statusBox.className = isRunning ? 'my_status_box running' : 'my_status_box stopped';
        statusDetail.innerHTML = `
            <strong>마지막 매매 시간:</strong> ${new Date(data.last_trade_time).toLocaleString()}<br>
            <strong>잔고:</strong> ${data.current_balance ? data.current_balance.toFixed(2) : 'N/A'}<br>
            <em>${data.message}</em>
        `;
    } catch (error) {
        console.error("Error fetching bot status:", error);
        statusBox.textContent = "🚨 상태 확인 실패 (API Error)";
        statusBox.className = 'my_status_box stopped';
        statusDetail.textContent = '서버 또는 코어 프로세스를 확인하세요.';
    }
}

/**
 * 봇 설정을 API에서 가져와 폼에 채웁니다.
 */
async function fetchSettings() {
    try {
        const response = await axios.get(`${API_BASE_URL}/settings`);
        const settings = response.data;
        
        document.getElementById('api_key').value = settings.exchange_api_key;
        document.getElementById('secret_key').value = settings.exchange_secret_key;
        document.getElementById('strategy_name').value = settings.strategy_name;
        document.getElementById('risk_per_trade').value = settings.risk_per_trade;
        document.getElementById('is_active').checked = settings.is_active;

    } catch (error) {
        if (error.response && error.response.status === 404) {
            console.log("Settings not initialized. Using default form values.");
        } else {
            console.error("Error fetching settings:", error);
        }
    }
}

/**
 * 폼 데이터를 API로 보내 봇 설정을 업데이트합니다.
 */
document.getElementById('settings-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    
    const formData = {
        exchange_api_key: document.getElementById('api_key').value,
        exchange_secret_key: document.getElementById('secret_key').value,
        strategy_name: document.getElementById('strategy_name').value,
        risk_per_trade: parseFloat(document.getElementById('risk_per_trade').value),
        is_active: document.getElementById('is_active').checked
    };

    try {
        const response = await axios.post(`${API_BASE_URL}/settings`, formData);
        alert("✅ 설정이 성공적으로 저장되었습니다!");
        fetchBotStatus(); // 설정 변경 후 상태 새로고침
    } catch (error) {
        console.error("Error updating settings:", error);
        alert("❌ 설정 저장 실패: " + (error.response?.data?.detail || error.message));
    }
});

/**
 * 매매 로그를 API에서 가져와 테이블에 표시합니다.
 */
async function fetchTradeLogs() {
    const logsBody = document.getElementById('trade-logs-body');
    logsBody.innerHTML = '<tr><td colspan="6">로그를 불러오는 중...</td></tr>';
    
    try {
        // limit=10, offset=0 으로 최신 10개 로그를 가져옵니다.
        const response = await axios.get(`${API_BASE_URL}/logs?limit=10&offset=0`);
        const logs = response.data;
        
        if (logs.length === 0) {
            logsBody.innerHTML = '<tr><td colspan="6">매매 기록이 없습니다.</td></tr>';
            return;
        }

        logsBody.innerHTML = logs.map(log => `
            <tr>
                <td>${log.order_id}</td>
                <td><strong>${log.symbol}</strong></td>
                <td><span style="color: ${log.side === 'BUY' ? '#4CAF50' : '#F44336'}; font-weight: bold;">${log.side}</span></td>
                <td>${log.executed_price ? log.executed_price.toFixed(4) : 'N/A'}</td>
                <td>${log.executed_qty.toFixed(4)}</td>
                <td>${new Date(log.log_time).toLocaleString()}</td>
            </tr>
        `).join('');

    } catch (error) {
        console.error("Error fetching trade logs:", error);
        logsBody.innerHTML = '<tr><td colspan="6">🚨 로그 로딩 중 오류 발생.</td></tr>';
    }
}