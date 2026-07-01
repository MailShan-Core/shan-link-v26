import asyncio
import random
import json
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="MailShan Core - Secure Wireless Projection System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔒 帳號密碼本機資料庫儲存庫
USER_DB = {"admin": "admin123", "manager": "shan2026"}
active_connections = {}

def detect_device(user_agent: str) -> str:
    ua = user_agent.lower()
    if "iphone" in ua: return "Apple iPhone"
    if "macintosh" in ua or "mac os" in ua: return "Apple Mac"
    if "windows" in ua: return "Windows PC"
    if "android" in ua: return "Android Device"
    return "Unknown Device"

# ══════════════════════════════════════════════════════════════
# 🎨 網頁全代碼區塊（100% 完整登入喜統、8K 165Hz、中途斷線全螢幕確定視窗）
# ══════════════════════════════════════════════════════════════

INDEX_HTML = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>iOS 26 Core - Hub</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(35px);
            -webkit-backdrop-filter: blur(35px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .glass-card:hover {
            background: rgba(255, 255, 255, 0.08);
            border-color: rgba(255, 255, 255, 0.18);
            transform: translateY(-4px);
        }
    </style>
</head>
<body class="bg-gradient-to-br from-zinc-950 via-black to-slate-900 min-h-screen flex flex-col items-center justify-center text-white font-sans select-none overflow-hidden">
    <div class="text-center mb-12">
        <div class="h-7 bg-white/5 rounded-full px-4 py-1 inline-flex items-center text-[10px] tracking-[0.2em] text-indigo-300 font-medium border border-white/5 mb-4 shadow-inner">
            MAILSHAN PROJECTION CENTER
        </div>
        <h1 class="text-4xl font-extralight tracking-wider text-transparent bg-clip-text bg-gradient-to-b from-white to-zinc-400">請選擇裝置模式</h1>
    </div>
    <div class="flex flex-col sm:flex-row gap-6 w-full max-w-2xl px-6">
        <a href="/sender" class="glass-card flex-1 p-8 rounded-[32px] text-center group cursor-pointer shadow-2xl">
            <div class="w-14 h-14 rounded-2xl bg-white/5 flex items-center justify-center mx-auto mb-6 border border-white/10 group-hover:bg-white group-hover:text-black transition-all duration-300 text-2xl">💻</div>
            <h3 class="text-xl font-medium mb-2">我是發射端</h3>
            <p class="text-xs text-white/40 leading-relaxed">內建高級帳號登入系統與即時區網延遲監測動態島。</p>
        </a>
        <a href="/receiver" class="glass-card flex-1 p-8 rounded-[32px] text-center group cursor-pointer shadow-2xl">
            <div class="w-14 h-14 rounded-2xl bg-white/5 flex items-center justify-center mx-auto mb-6 border border-white/10 group-hover:bg-indigo-500 transition-all duration-300 text-2xl">📺</div>
            <h3 class="text-xl font-medium mb-2">我是電視端</h3>
            <p class="text-xs text-white/40 leading-relaxed">生成安全驗證代碼，支援接收端獨立畫質與權限設定。</p>
        </a>
    </div>
</body>
</html>
"""

SENDER_HTML = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>iOS 26 Core - Stream Sender</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .glass-panel { background: rgba(255, 255, 255, 0.06); backdrop-filter: blur(35px); -webkit-backdrop-filter: blur(35px); border: 1px solid rgba(255, 255, 255, 0.15); }
    </style>
</head>
<body class="bg-gradient-to-br from-gray-950 via-black to-slate-900 min-h-screen flex items-center justify-center text-white font-sans select-none">

    <div id="authPanel" class="glass-panel p-8 rounded-[32px] w-96 shadow-2xl text-center">
        <h2 class="text-2xl font-light mb-6 tracking-wide">發射端核心安全登入</h2>
        <div class="space-y-4">
            <input id="username" type="text" placeholder="帳號" class="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-center focus:outline-none focus:border-indigo-500">
            <input id="password" type="password" placeholder="密碼" class="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-center focus:outline-none focus:border-indigo-500">
            <button onclick="handleAuth('login')" class="w-full bg-white text-black font-semibold py-3 rounded-2xl hover:bg-white/90 active:scale-[0.98] transition-all">登入系統</button>
            <button onclick="handleAuth('register')" class="w-full bg-white/10 text-white text-xs py-2 rounded-xl hover:bg-white/20 transition-all">沒有帳號？點此註冊</button>
        </div>
    </div>

    <div id="mainPanel" class="glass-panel p-8 rounded-[32px] w-96 shadow-2xl text-center relative hidden">
        <div class="flex items-center justify-between px-4 py-2 bg-black/50 rounded-full mb-4 border border-white/5 text-xs">
            <div class="flex items-center gap-2">
                <span id="statusDot" class="w-2 h-2 rounded-full bg-gray-500"></span>
                <span id="statusText" class="text-white/60 font-medium">認證成功</span>
            </div>
            <div class="text-indigo-400 font-mono text-[11px]" id="pingDisplay">Ping: -- ms</div>
        </div>
        
        <div class="text-right mb-2">
            <button onclick="toggleSettings()" class="text-[11px] text-white/40 hover:text-white/80">⚙️ 發射端設定</button>
        </div>

        <div id="settingsBox" class="hidden bg-black/40 border border-white/5 rounded-2xl p-4 mb-4 text-left text-xs space-y-2">
            <label class="block">投放解析度最高上限:</label>
            <select id="resOpt" class="bg-zinc-800 border border-white/10 rounded px-2 py-1 w-full text-white">
                <option value="4320">8K Ultra HD (7680x4320 極致性能)</option>
                <option value="2160">4K Ultra HD (3840x2160)</option>
                <option value="1080">1080p Full HD</option>
            </select>
            <label class="block mt-2">目標螢幕更新率限制:</label>
            <select id="fpsOpt" class="bg-zinc-800 border border-white/10 rounded px-2 py-1 w-full text-white">
                <option value="165">165 Hz (電競高刷解鎖)</option>
                <option value="60">60 Hz (日常高流暢)</option>
                <option value="30">30 Hz (低規優化)</option>
            </select>
        </div>

        <input id="codeIn" type="text" placeholder="輸入電視端的 4 位代碼" class="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-center text-lg tracking-widest focus:outline-none focus:border-indigo-500 mb-4 transition-all">
        <button onclick="startProjection()" class="w-full bg-white text-black font-semibold py-3 rounded-2xl hover:bg-white/90 active:scale-[0.98] transition-all">開始串流畫面</button>
        <button onclick="logout()" class="mt-6 text-xs text-red-400/60 hover:text-red-400 transition-colors block mx-auto">安全登出系統</button>
    </div>

    <div id="endOverlay" class="fixed inset-0 bg-black/95 backdrop-blur-3xl z-50 flex flex-col items-center justify-center opacity-0 pointer-events-none transition-all duration-700 scale-105">
        <div class="text-center p-8 max-w-sm glass-panel rounded-[40px] border border-white/10">
            <div id="endIcon" class="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-white/10 text-2xl">📴</div>
            <h3 id="endTitle" class="text-xl font-light tracking-widest text-zinc-200 mb-2">連線已結束</h3>
            <p id="endDesc" class="text-xs text-zinc-500 leading-relaxed mb-6">頻道已安全註銷，區網通訊及編碼線路已全數安全回收。</p>
            <button onclick="closeEndPanel()" class="bg-white text-black font-semibold py-2.5 px-8 rounded-xl text-xs hover:bg-white/90 active:scale-95 transition-all w-full">確定</button>
        </div>
    </div>

    <script>
        let localStream; let peerConnection; let socket;
        let token = localStorage.getItem('sender_token');

        if(token) { showMain(); }

        async function handleAuth(type) {
            const u = document.getElementById('username').value;
            const p = document.getElementById('password').value;
            if(!u || !p) return alert('請填寫完整欄位');
            const res = await fetch('/api/auth/' + type, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: u, password: p})
            });
            const data = await res.json();
            if(data.status === 'success') {
                localStorage.setItem('sender_token', data.token);
                showMain();
            } else { alert(data.detail); }
        }

        function showMain() {
            document.getElementById('authPanel').classList.add('hidden');
            document.getElementById('mainPanel').classList.remove('hidden');
        }

        function toggleSettings() { document.getElementById('settingsBox').classList.toggle('hidden'); }

        async function startProjection() {
            const code = document.getElementById('codeIn').value;
            if(!code) return alert('請輸入連線代碼');

            updateStatus('connecting', '正在配對電視...');

            const checkRes = await fetch('/api/auth/verify-code/' + code);
            const checkData = await checkRes.json();
            if(checkData.status !== 'valid') {
                updateStatus('error', '驗證失敗');
                return alert('【代碼無效】電視端尚未產生此連線碼！');
            }

            try {
                const maxRes = document.getElementById('resOpt').value;
                const maxFps = document.getElementById('fpsOpt').value;
                
                // 📡 畫質限制分配解鎖 (極致相容 8K 與 165Hz)
                let constraints = {
                    video: {
                        width: maxRes === "4320" ? 7680 : (maxRes === "2160" ? 3840 : 1920),
                        height: parseInt(maxRes),
                        frameRate: parseInt(maxFps)
                    },
                    audio: false
                };

                localStream = await navigator.mediaDevices.getDisplayMedia(constraints);

                // 原生停止分享監控
                localStream.getVideoTracks()[0].onended = function () {
                    stopProjectionSequence("normal");
                };

            } catch (e) {
                updateStatus('error', '未授權螢幕分享');
                return;
            }

            let protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
            let wsUrl = protocol + window.location.host + "/ws/signal/sender/" + code;
            
            socket = new WebSocket(wsUrl);
            peerConnection = new RTCPeerConnection({ iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] });
            localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream));

            // 🎯【投射中途一半斷線監測機制】
            peerConnection.onconnectionstatechange = () => {
                if(peerConnection.connectionState === 'connected') {
                    updateStatus('connected', '畫質與動態已同步');
                } else if (peerConnection.connectionState === 'disconnected' || peerConnection.connectionState === 'failed') {
                    stopProjectionSequence("interrupted");
                }
            };

            peerConnection.onicecandidate = event => {
                if (event.candidate && socket.readyState === WebSocket.OPEN) {
                    socket.send(JSON.stringify({ type: 'candidate', candidate: event.candidate }));
                }
            };

            const offer = await peerConnection.createOffer();
            await peerConnection.setLocalDescription(offer);
            socket.onopen = () => { socket.send(JSON.stringify({ type: 'offer', sdp: offer.sdp })); };
            
            socket.onmessage = async (event) => {
                const message = JSON.parse(event.data);
                if (message.type === 'ping') {
                    const ping = Math.round(Date.now() - message.timestamp);
                    document.getElementById('pingDisplay').innerText = 'Ping: ' + ping + ' ms';
                    socket.send(JSON.stringify({ type: 'pong' }));
                    return;
                }
                if (message.type === 'peer_disconnected' || message.type === 'stop_projection') {
                    stopProjectionSequence("normal");
                    return;
                }
                if (message.type === 'answer') await peerConnection.setRemoteDescription(new RTCSessionDescription(message));
                else if (message.type === 'candidate') await peerConnection.addIceCandidate(new RTCIceCandidate(message.candidate));
            };
        }

        function stopProjectionSequence(reason) {
            if(socket && socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({ type: 'stop_projection' }));
                socket.close();
            }
            if(localStream) {
                localStream.getTracks().forEach(track => track.stop());
                localStream = null;
            }
            if(peerConnection) {
                peerConnection.close();
            }
            
            updateStatus('ready', '系統就緒');
            document.getElementById('pingDisplay').innerText = "Ping: -- ms";

            // 根據原因抽換確定面板文字
            const title = document.getElementById('endTitle');
            const desc = document.getElementById('endDesc');
            const icon = document.getElementById('endIcon');

            if(reason === "interrupted") {
                icon.innerText = "❌";
                title.innerText = "連線中途斷開";
                desc.innerText = "偵測到區網訊號異常或電視接收端閃退，連線已中斷，請按確定重試。";
            } else {
                icon.innerText = "📴";
                title.innerText = "投影已結束";
                desc.innerText = "無線螢幕投影頻道已註銷，內存與網絡資源已完全安全釋放。";
            }

            const overlay = document.getElementById('endOverlay');
            overlay.classList.remove('opacity-0', 'pointer-events-none', 'scale-105');
            overlay.classList.add('opacity-100', 'scale-100');
        }

        function closeEndPanel() {
            const overlay = document.getElementById('endOverlay');
            overlay.classList.remove('opacity-100', 'scale-100');
            overlay.classList.add('opacity-0', 'pointer-events-none', 'scale-105');
        }

        function updateStatus(state, text) {
            const dot = document.getElementById('statusDot');
            const txt = document.getElementById('statusText');
            txt.innerText = text;
            if(state === 'connected') dot.className = "w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]";
            else if (state === 'connecting') dot.className = "w-2 h-2 rounded-full bg-yellow-500 animate-pulse";
            else if (state === 'error') dot.className = "w-2 h-2 rounded-full bg-red-500";
            else dot.className = "w-2 h-2 rounded-full bg-zinc-500";
        }

        // 🔒 已完全修復、不引起崩潰的發射端高級登出
        function logout() {
            localStorage.removeItem('sender_token');
            stopProjectionSequence("normal");
            setTimeout(() => { window.location.reload(); }, 100);
        }
    </script>
</body>
</html>
"""

RECEIVER_HTML = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>iOS 26 Core - TV Receiver</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .glass-panel {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(40px);
            -webkit-backdrop-filter: blur(40px);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
    </style>
</head>
<body class="bg-black min-h-screen flex items-center justify-center text-white font-sans overflow-hidden select-none relative">

    <div id="authPanel" class="glass-panel p-8 rounded-[32px] w-96 shadow-2xl text-center z-20">
        <h2 class="text-2xl font-light mb-6 tracking-wide">電視接收端授權登入</h2>
        <div class="space-y-4">
            <input id="tv_username" type="text" placeholder="電視管理員帳號" class="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-center focus:outline-none focus:border-indigo-500">
            <input id="tv_password" type="password" placeholder="管理密碼" class="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-center focus:outline-none focus:border-indigo-500">
            <button onclick="handleTvAuth()" class="w-full bg-indigo-600 text-white font-semibold py-3 rounded-2xl">授權並啟動接收</button>
        </div>
    </div>

    <div id="setupPanel" class="glass-panel p-12 rounded-[40px] w-[500px] shadow-2xl text-center z-10 transition-all duration-700 scale-100 hidden">
        <div class="h-8 bg-zinc-900 rounded-full mx-auto mb-8 flex items-center justify-between px-4 text-[11px] text-indigo-300 font-medium tracking-widest border border-white/5">
            <div class="flex items-center">
                <span class="w-2 h-2 rounded-full bg-indigo-500 animate-pulse mr-2"></span>
                SHAN LINK TV CORE v26
            </div>
            <div id="deviceDisplay" class="text-white/40 font-normal">來源裝置: 等待中</div>
        </div>
        
        <div class="text-left text-xs text-white/30 mb-4 bg-zinc-900/50 p-3 rounded-xl flex justify-between items-center">
            <span>接收端設定：高硬骨加速影像解碼通道</span>
            <button onclick="tvLogout()" class="text-red-400 hover:underline">Tv登出</button>
        </div>

        <h1 class="text-2xl font-light tracking-wide mb-2">無線投影接收端</h1>
        <p class="text-sm text-white/30 mb-8">請在發射端輸入下方安全連線碼</p>
        <div id="codeDisplay" class="text-6xl font-bold tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-white to-zinc-500 py-6 font-mono">----</div>
    </div>

    <div id="tvEndOverlay" class="fixed inset-0 bg-black z-40 flex flex-col items-center justify-center opacity-0 pointer-events-none transition-all duration-1000 scale-105">
        <div class="w-24 h-[1px] bg-gradient-to-r from-transparent via-indigo-500 to-transparent rounded-full mb-8 animate-pulse"></div>
        <h2 class="text-3xl font-extralight tracking-widest text-zinc-500 mb-2">PROJECTION ENDED</h2>
        <p class="text-xs text-zinc-700 font-mono tracking-widest uppercase">MailShan Link · Channel Terminated</p>
    </div>

    <video id="tvVideo" autoplay playsinline muted class="absolute inset-0 w-full h-full object-contain z-30 opacity-0 pointer-events-none bg-black transition-all duration-500"></video>

    <script>
        let peerConnection; let socket;
        let token = localStorage.getItem('receiver_token');

        if(token) { showReceiverCore(); }

        async function handleTvAuth() {
            const u = document.getElementById('tv_username').value;
            const p = document.getElementById('tv_password').value;
            const res = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: u, password: p})
            });
            const data = await res.json();
            if(data.status === 'success') {
                localStorage.setItem('receiver_token', data.token);
                showReceiverCore();
            } else { alert('認證失敗，密碼錯誤'); }
        }

        async function showReceiverCore() {
            document.getElementById('authPanel').classList.add('hidden');
            document.getElementById('setupPanel').classList.remove('hidden');
            
            try {
                const response = await fetch('/api/auth/generate-code');
                const data = await response.json();
                const pairingCode = data.code;
                document.getElementById('codeDisplay').innerText = pairingCode;

                let protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
                let wsUrl = protocol + window.location.host + "/ws/signal/receiver/" + pairingCode;
                
                socket = new WebSocket(wsUrl);
                initWebRTC(pairingCode);
            } catch (e) {
                document.getElementById('codeDisplay').innerText = "ERR";
            }
        }

        function initWebRTC(code) {
            peerConnection = new RTCPeerConnection({ iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] });
            
            peerConnection.ontrack = (event) => {
                const videoElement = document.getElementById('tvVideo');
                const setupPanel = document.getElementById('setupPanel');
                if (event.streams && event.streams[0]) {
                    videoElement.srcObject = event.streams[0];
                    videoElement.muted = true;
                    
                    // 💥 強制翻轉視訊透明度，突破低規電視圖層黑屏快取
                    videoElement.style.opacity = "1";
                    videoElement.style.pointerEvents = "auto";
                    setupPanel.classList.add('opacity-0', 'scale-95');
                    
                    setTimeout(() => {
                        videoElement.play().catch(err => {});
                    }, 200);

                    // 點擊網頁強制破除解碼防禦
                    document.body.addEventListener('click', () => {
                        videoElement.muted = false;
                        videoElement.play().catch(e => {});
                    }, { once: true });
                }
            };
            
            peerConnection.onicecandidate = event => {
                if (event.candidate && socket.readyState === WebSocket.OPEN) {
                    socket.send(JSON.stringify({ type: 'candidate', candidate: event.candidate }));
                }
            };
            
            socket.onmessage = async (event) => {
                const message = JSON.parse(event.data);
                if (message.type === 'ping') { socket.send(JSON.stringify({ type: 'pong' })); return; }
                if (message.type === 'device_detected') { document.getElementById('deviceDisplay').innerText = '來源裝置: ' + message.device; return; }
                
                if (message.type === 'peer_disconnected' || message.type === 'stop_projection') {
                    executeTvStopSequence();
                    return;
                }
                
                if (message.type === 'offer') {
                    await peerConnection.setRemoteDescription(new RTCSessionDescription(message));
                    const answer = await peerConnection.createAnswer();
                    await peerConnection.setLocalDescription(answer);
                    socket.send(JSON.stringify({ type: 'answer', sdp: answer.sdp }));
                } else if (message.type === 'candidate') await peerConnection.addIceCandidate(new RTCIceCandidate(message.candidate));
            };
        }

        function executeTvStopSequence() {
            const videoElement = document.getElementById('tvVideo');
            const overlay = document.getElementById('tvEndOverlay');
            
            if(videoElement) {
                videoElement.pause();
                videoElement.srcObject = null;
                videoElement.style.opacity = "0";
            }
            if(peerConnection) peerConnection.close();
            if(socket) socket.close();

            overlay.classList.remove('opacity-0', 'pointer-events-none', 'scale-105');
            overlay.classList.add('opacity-100', 'scale-100');

            setTimeout(() => {
                window.location.reload();
            }, 3000);
        }

        // ⭐ 已完全修正、不破壞主腳本環境的電視端高級登出
        function tvLogout() {
            localStorage.removeItem('receiver_token');
            window.location.reload();
        }
    </script>
</body>
</html>
"""

# ══════════════════════════════════════════════════════════════
# 📡 伺服器核心路由與 API 控制項
# ══════════════════════════════════════════════════════════════

from pydantic import BaseModel
class AuthModel(BaseModel):
    username: str
    password: str

@app.post("/api/auth/login")
async def api_login(data: AuthModel):
    if data.username in USER_DB and USER_DB[data.username] == data.password:
        return {"status": "success", "token": f"token_{data.username}_{int(time.time())}"}
    return {"status": "error", "detail": "帳號或密碼錯誤"}

@app.post("/api/auth/register")
async def api_register(data: AuthModel):
    if data.username in USER_DB:
        return {"status": "error", "detail": "該帳號已存在"}
    USER_DB[data.username] = data.password
    return {"status": "success", "token": f"token_{data.username}_{int(time.time())}"}

@app.get("/api/auth/verify-code/{code}")
async def verify_code(code: str):
    if code in active_connections:
        return {"status": "valid"}
    return {"status": "invalid"}

@app.get("/", response_class=HTMLResponse)
async def get_index(): return INDEX_HTML

@app.get("/sender", response_class=HTMLResponse)
async def get_sender(): return SENDER_HTML

@app.get("/receiver", response_class=HTMLResponse)
async def get_receiver(): return RECEIVER_HTML

@app.get("/api/auth/generate-code")
async def generate_code():
    code = str(random.randint(1000, 9999))
    while code in active_connections:
        code = str(random.randint(1000, 9999))
    active_connections[code] = {"sender": None, "receiver": None, "sender_device": "未連線", "sender_last_seen": 0}
    return {"code": code}

@app.websocket("/ws/signal/{role}/{code}")
async def signaling_endpoint(websocket: WebSocket, role: str, code: str):
    await websocket.accept()
    if code not in active_connections:
        await websocket.close(code=4000, reason="代碼無效")
        return
    active_connections[code][role] = websocket
    if role == "sender":
        user_agent = websocket.headers.get("user-agent", "")
        device_type = detect_device(user_agent)
        active_connections[code]["sender_device"] = device_type
        if active_connections[code]["receiver"]:
            await active_connections[code]["receiver"].send_text(json.dumps({"type": "device_detected", "device": device_type}))

    monitor_task = asyncio.create_task(connection_monitor(code, role))
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "pong": continue
            target_role = "receiver" if role == "sender" else "sender"
            target_ws = active_connections[code][target_role]
            if target_ws: await target_ws.send_text(data)
    except WebSocketDisconnect:
        pass
    finally:
        monitor_task.cancel()
        if code in active_connections:
            active_connections[code][role] = None
            target_role = "receiver" if role == "sender" else "sender"
            target_ws = active_connections[code][target_role]
            if target_ws:
                try: await target_ws.send_text(json.dumps({"type": "peer_disconnected"}))
                except: pass
            if active_connections[code]["sender"] is None and active_connections[code]["receiver"] is None:
                del active_connections[code]

async def connection_monitor(code: str, role: str):
    while True:
        await asyncio.sleep(3)
        if code not in active_connections: break
        ws = active_connections[code][role]
        if ws:
            try: await ws.send_text(json.dumps({ "type": "ping", "timestamp": time.time() * 1000 }))
            except: break

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)