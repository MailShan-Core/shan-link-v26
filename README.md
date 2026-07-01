\# MailShan Link v26 Core (初始核心純淨版)

> 🍏 \*\*Apple-Style 流體美學視覺 · WebRTC 零延遲區網投影系統之頂峰原型\*\*



MailShan Link v26 Core 是一款基於 Python FastAPI 後端監控與前端 HTML5 原生 WebRTC（Web Real-Time Communication）技術打造的\*\*零延遲、超高流暢度無線螢幕投影系統\*\*。



本版本為最完美的\*\*初始純淨版\*\*，徹底去除了繁瑣的外部網路憑證（HTTPS/SSL）機制與任何商業會員權限死鎖。全系統解鎖最高硬體調度權限，直接開放 \*\*8K Ultra HD 超微畫質\*\* 與 \*\*165Hz 電競級極致高刷\*\*，回歸「一鍵極速通車、局域網點對點直連」的純粹工程體驗。



\---



\## 🎨 iOS 26 概念流體視覺設計 (Apple UI Design)



本系統介面設計嚴格遵循 Apple 介面設計規範（Human Interface Guidelines），排除任何冗餘的 Gaming 元素，專注於極簡與純粹的科技美學：



\* \*\*超幾何磨砂（Hyper-Frostmorphism）\*\*：全系統卡片與控制面板採用 `backdrop-filter: blur(35px)` 微光高流體毛玻璃效果，搭配大導角（`rounded-\[32px]`）與 `rgba(255, 255, 255, 0.05)` 的細緻微光邊框，引導極佳的視覺 scannability。

\* \*\*智慧監測動態島 (Dynamic Island)\*\*：發射端與接收端頂部內建環形動態島，完美整合系統狀態指示燈，並以毫秒級（ms）即時更新、渲染當前局域網的傳輸 Ping 值與心跳監控（Heartbeat）。

\* \*\*未來感退場流體彈窗 (End-Overlay)\*\*：當使用者點擊瀏覽器自帶的「停止分享」或因區網訊號異常時，雙端將秒級同步啟動 iOS 26 滿版流體退場動畫，強制釋放電視端硬體解碼快取與記憶體（RAM），徹底告別生硬的畫面定格或黑屏。



\---



\## ⚡ 核心技術優勢與同步演算法



本系統在無需外部伺服器穿透的環境下，達成影音完全同步與高負載穩定性：



\### 1. 0-Latency 零延遲完全同步

\* \*\*頻寬優化限制\*\*：前端內建編碼調度演算法，強制將 WebRTC 位元率壓制在區網 Wi-Fi 最舒適的 `6Mbps` 頻寬，避免低階 Android TV 晶片多餘積壓。

\* \*\*物理級零快取\*\*：在發射端注入 `latencyHint: "low"` 參數，並在接收端強制寫入 `playDelay = 0`，命令解碼器不留影格快取、一有資料立刻渲染，達成音視訊物理級的零時差完全同步。



\### 2. 8K 165Hz 電競級性能調度

\* 後端無規格審查鎖定，發射端設定面板開箱即享有 \*\*8K Ultra HD (7680x4320)\*\* 的超高動態解析度分配率，以及最高 \*\*165Hz\*\* 的電競刷新率上限，完美釋放 Mac M3 Max 或 高階 Windows PC 的原生螢幕實力。



\### 3. 中途斷線安全攔截防護

\* 投射中途一半若因局域網波動、電視端瀏覽器快取閃退，發射端的 WebRTC 狀態監聽器（`onconnectionstatechange`）將在千分之一秒內捕捉到 `disconnected` 或 `failed` 訊號，自動安全熔斷。

\* \*\*徹底避免死鎖\*\*：系統會直接拋出優雅的滿版「確定」中斷提示視窗，絕對不允許未初始化的 WebSockets 或 MediaStream 拋出 Null 錯誤，保證前端 JavaScript 執行緒永遠不卡死崩潰。



\---



\## 📡 系統核心架構



系統完全解耦，由三大核心模組構成，在純區域網路（LAN）環境下跑點對點加密直連：



\[ 電腦發射端 (Sender) ] ──( 訊號配對 )──> \[ FastAPI 核心控制中心 (8000 埠) ]

│                                              │

└───────( WebRTC 點對點 8K 165Hz 直連 )────────┘

▼

\[ 電視接收端 (Receiver) ] (硬體加速解碼出圖)





1\. \*\*FastAPI Core 監控中心\*\*：處理即時訊號配對、WebSocket 信令交換、自動偵測來源裝置類型（Apple Mac / Windows PC / iPhone / Android）並同步派發至電視端。

2\. \*\*發射端核心 (Stream Sender)\*\*：一鍵調用瀏覽器原生的螢幕共用 API，內建画質設定選單與心跳 Ping 值回傳系統。

3\. \*\*電視接收端核心 (TV Receiver)\*\*：針對低階 Android TV 的網頁核心（WebView）進行性能調優，重構 `<video>` 渲染層透明度權重，徹底突破硬理解碼不出圖的漏洞。



\---



\## 🛠️ 快速啟動與部署指南



\### 1. 安裝環境依賴

本專案基於輕量高效的 Python 非同步生態系，僅需安裝標準核心依賴：

```bash

pip install fastapi uvicorn pydantic

2\. 啟動 Python 伺服器

將全代碼儲存為 app.py 後，在終端機（Terminal）或 PyCharm 中執行：



Bash

python app.py

伺服器將在本地 http://127.0.0.1:8000 正式上線。



3\. 變更模式連線

電腦發射端：使用 Chrome 或 Edge 瀏覽器打開 http://\[你的伺服器IP]:8000/sender。



電視接收端：電視打開 http://\[你的伺服器IP]:8000/receiver。



配對通車：電視端畫面上會秒級生成一組安全隨機 4 位代碼（PIN 碼），將此代碼輸入發射端對話框中，選擇你要的解析度與刷新率，點擊「開始串流畫面」，即可享受大螢幕完全同步的極致流暢視覺。



📝 專案 OTA 系統日誌 (OTA Logs)

v26.1.0 (最新版本)：實裝 8K 165Hz 電競串流協定；重構資源回收機制，徹底修復未建立流即呼叫關閉導致的 JS 按鈕死鎖崩潰 Bug。



v26.0.4：優化電視端硬體加速出圖通道，移除非必要的 hidden 屬性快取，根除部分低階電視黑屏漏洞。



v26.0.0 (立項實裝)：MailShan Link 無線核心架構確立，iOS 26 控制中心與流體毛玻璃 UI 規範全量實裝。



⚙️ 專案技術維護

本專案由 MailShan 核心技術維護小組 (MailShan Core Team) 獨立開發、調優與維護。



系統標識識別：MailShan Core System / Shan Link TV Core v26



開發與維護者標記：CC Chairman (CC 董事長) / Chen Manager (陳經理) / CHENFEYAN



專屬技術 domain：MailShan Core Infrastructure

