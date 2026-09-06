import os, requests, re
from flask import Flask, request, jsonify, render_template_string

def convert_links_to_html(text):
    url_pattern = re.compile(r"(https?://[^\s]+)")
    return url_pattern.sub(r'<a href="\1" target="_blank" style="color: #4da6ff; text-decoration: underline;">\1</a>', text)

app = Flask(__name__)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VTuber AI Live - Pro</title>
    <style>
        :root {
            --primary-color: #ff4757;
            --primary-glow: rgba(255, 71, 87, 0.4);
            --accent-color: #ff6b81;
        }

        body { background-color: #121212; color: #ffffff; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; overflow: hidden; animation: fadeIn 0.5s ease-in-out; }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-5px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes messagePop {
            0% { opacity: 0; transform: translateY(15px) scale(0.95); }
            100% { opacity: 1; transform: translateY(0) scale(1); }
        }

        @keyframes pulseGlow {
            0% { box-shadow: 0 0 0 0 var(--primary-glow); }
            70% { box-shadow: 0 0 0 8px rgba(255, 71, 87, 0); }
            100% { box-shadow: 0 0 0 0 rgba(255, 71, 87, 0); }
        }

        @keyframes typingBounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-5px); }
        }

        .btn-menu { position: absolute; top: 15px; left: 15px; background: #1e1e1e; color: var(--primary-color); border: 1px solid #333; padding: 8px 12px; border-radius: 8px; cursor: pointer; z-index: 10; transition: transform 0.2s, background 0.2s; }
        .btn-menu:active { transform: scale(0.92); }
        
        .vtuber-top-right { position: absolute; top: 12px; right: 15px; display: flex; align-items: center; gap: 8px; z-index: 10; background: #1e1e1e; padding: 5px 10px; border-radius: 20px; border: 1px solid #333; animation: fadeIn 0.6s ease; }
        .avatar-box { width: 35px; height: 35px; border-radius: 50%; border: 2px solid var(--primary-color); overflow: hidden; background-color: #222; cursor: pointer; flex-shrink: 0; transition: transform 0.3s; animation: pulseGlow 2s infinite; }
        .avatar-box:hover { transform: scale(1.1); }
        .avatar-box img { width: 100%; height: 100%; object-fit: cover; }
        .vtuber-info { display: flex; flex-direction: column; text-align: left; }
        .vtuber-name { font-size: 12px; color: var(--accent-color); font-weight: bold; margin: 0; }
        .vtuber-actions { display: flex; gap: 5px; margin-top: 1px; }
        .action-chip { background: transparent; border: none; color: #aaa; padding: 0; font-size: 10px; cursor: pointer; text-decoration: underline; transition: color 0.2s; }
        .action-chip:hover { color: var(--accent-color); }

        .sidebar { position: fixed; top: 0; left: -300px; width: 280px; height: 100%; background: #181818; border-right: 1px solid #333; transition: left 0.35s cubic-bezier(0.1, 0.9, 0.2, 1); z-index: 100; display: flex; flex-direction: column; padding: 15px; box-sizing: border-box; }
        .sidebar.open { left: 0; }
        .sidebar-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px solid #333; padding-bottom: 10px; }
        .sidebar-header h3 { margin: 0; color: var(--accent-color); font-size: 16px; }
        .btn-close-sidebar { background: none; border: none; color: #aaa; font-size: 18px; cursor: pointer; transition: transform 0.2s; }
        .btn-close-sidebar:hover { transform: rotate(90deg); color: #fff; }
        
        .btn-new-chat { background: #252525; color: white; border: 1px solid #444; padding: 10px; border-radius: 8px; cursor: pointer; text-align: left; font-size: 14px; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; transition: background 0.2s; }
        .btn-new-chat:hover { background: #333; }
        
        .btn-clear-all { background: #2a1518; color: var(--primary-color); border: 1px solid #442226; padding: 8px; border-radius: 8px; cursor: pointer; text-align: center; font-size: 13px; margin-bottom: 15px; font-weight: bold; transition: background 0.2s; }
        .btn-clear-all:hover { background: #3a1a1f; }

        /* Khu vực chọn màu giao diện trong Sidebar */
        .theme-section { margin-bottom: 15px; border-top: 1px solid #333; padding-top: 12px; }
        .theme-title { font-size: 12px; color: #aaa; margin-bottom: 8px; font-weight: bold; }
        .theme-palette { display: flex; gap: 8px; justify-content: space-between; }
        .theme-dot { width: 28px; height: 28px; border-radius: 50%; cursor: pointer; border: 2px solid transparent; transition: transform 0.2s, border-color 0.2s; }
        .theme-dot:hover { transform: scale(1.15); }
        .theme-dot.active { border-color: #fff; transform: scale(1.1); }

        .history-list { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 6px; }
        .history-item { background: #222; padding: 10px; border-radius: 6px; font-size: 13px; cursor: pointer; display: flex; align-items: center; justify-content: space-between; color: #ddd; border: 1px solid transparent; transition: all 0.2s; }
        .history-item:hover { background: #2a2a2a; border-color: #555; }
        .history-item.active { background: var(--primary-color); color: white; }
        .history-actions { display: flex; gap: 5px; }
        .history-actions button { background: none; border: none; cursor: pointer; font-size: 12px; color: inherit; padding: 2px 4px; }
        
        .overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: none; z-index: 99; opacity: 0; transition: opacity 0.3s ease; }
        .overlay.show { display: block; opacity: 1; }
        
        .config-box { position: absolute; top: 65px; right: 15px; background: #1e1e1e; padding: 12px 15px; border-radius: 8px; border: 1px solid #333; width: 260px; display: flex; flex-direction: column; gap: 8px; z-index: 10; box-shadow: 0 6px 16px rgba(0,0,0,0.6); animation: fadeIn 0.25s ease; }
        .config-row { display: flex; gap: 6px; }
        .config-box input { flex: 1; padding: 8px; border: 1px solid #444; background: #121212; color: white; border-radius: 5px; outline: none; font-size: 13px; }
        .btn-action { background-color: var(--primary-color); color: white; border: none; padding: 8px 12px; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 13px; transition: background 0.2s; }
        .btn-action:hover { background: var(--accent-color); }
        .link-key { font-size: 11px; color: var(--accent-color); text-decoration: none; text-align: right; }

        .chat-container { width: 95%; max-width: 650px; background: #1e1e1e; border-radius: 12px; border: 1px solid #333; display: flex; flex-direction: column; height: 82vh; box-sizing: border-box; margin-top: 30px; box-shadow: 0 8px 24px rgba(0,0,0,0.4); animation: fadeIn 0.6s cubic-bezier(0.1, 1, 0.1, 1); }
        .chat-box { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; scroll-behavior: smooth; }
        
        .message { padding: 10px 14px; border-radius: 10px; max-width: 85%; word-wrap: break-word; font-size: 14px; white-space: pre-wrap; animation: messagePop 0.3s cubic-bezier(0.1, 1, 0.1, 1) forwards; }
        .user-message { background: var(--primary-color); color: white; align-self: flex-end; box-shadow: 0 3px 10px var(--primary-glow); }
        .ai-message { background: #333; color: var(--accent-color); align-self: flex-start; border: 1px solid #444; box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2); }
        
        .typing-indicator { display: flex; align-items: center; gap: 5px; padding: 10px 14px; background: #333; border-radius: 10px; align-self: flex-start; border: 1px solid #444; animation: messagePop 0.3s ease forwards; }
        .typing-dot { width: 7px; height: 7px; background: var(--accent-color); border-radius: 50%; animation: typingBounce 1.4s infinite ease-in-out both; }
        .typing-dot:nth-child(1) { animation-delay: -0.32s; }
        .typing-dot:nth-child(2) { animation-delay: -0.16s; }

        .message img { max-width: 100%; border-radius: 6px; margin-top: 5px; display: block; cursor: pointer; transition: transform 0.2s; }
        .message img:hover { transform: scale(1.02); }
        
        .preview-container { padding: 5px 12px; background: #252525; display: none; align-items: center; gap: 10px; border-top: 1px solid #333; animation: fadeIn 0.2s ease; }
        .preview-container img { width: 35px; height: 35px; object-fit: cover; border-radius: 4px; }
        .preview-container span { font-size: 12px; color: #aaa; flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .preview-container button { background: transparent; border: none; color: var(--primary-color); cursor: pointer; font-weight: bold; }
        
        .input-box { display: flex; padding: 10px; border-top: 1px solid #333; background: #252525; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px; align-items: center; gap: 6px; box-sizing: border-box; }
        .input-box input[type="text"] { flex: 1; padding: 10px; border: 1px solid #444; background: #121212; color: white; border-radius: 6px; outline: none; font-size: 14px; transition: border-color 0.2s; }
        .input-box input[type="text"]:focus { border-color: var(--primary-color); }
        
        .btn-attach { background: #333; color: white; border: 1px solid #555; padding: 10px 12px; border-radius: 6px; cursor: pointer; font-size: 14px; transition: background 0.2s; }
        .btn-attach:hover { background: #444; }
        
        .btn-send { background: var(--primary-color); color: white; border: none; padding: 10px 16px; border-radius: 6px; cursor: pointer; font-weight: bold; transition: transform 0.1s, background 0.2s; }
        .btn-send:active { transform: scale(0.95); }

        .img-modal { display: none; position: fixed; z-index: 1000; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); flex-direction: column; justify-content: center; align-items: center; opacity: 0; transition: opacity 0.3s ease; }
        .img-modal.show { display: flex; opacity: 1; }
        .img-modal-content { max-width: 90%; max-height: 75%; border-radius: 8px; object-fit: contain; transform: scale(0.9); transition: transform 0.3s cubic-bezier(0.1, 1, 0.1, 1); }
        .img-modal.show .img-modal-content { transform: scale(1); }
        .img-modal-actions { margin-top: 15px; display: flex; gap: 12px; }
        .btn-download-img { background: var(--primary-color); color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 13px; border: none; cursor: pointer; }
        .btn-close-img { background: #333; color: white; padding: 8px 16px; border-radius: 6px; border: 1px solid #555; font-size: 13px; cursor: pointer; }
    </style>
</head>
<body>
    <button class="btn-menu" onclick="toggleSidebar()">☰</button>
    
    <div class="vtuber-top-right">
        <div class="avatar-box" onclick="document.getElementById('avatarInput').click()" title="Đổi Avatar">
            <img id="minaAvatar" src="https://api.iconify.design/fluent-emoji:cherry-blossom.svg" alt="Avatar">
        </div>
        <input type="file" id="avatarInput" accept="image/*" style="display:none" onchange="loadAvatar(event)">
        <div class="vtuber-info">
            <span class="vtuber-name">Mina VTuber ✨</span>
            <div class="vtuber-actions">
                <button class="action-chip" onclick="document.getElementById('avatarInput').click()">Đổi ảnh</button>
                <span>•</span>
                <button class="action-chip" onclick="toggleConfigBox()">API Key</button>
            </div>
        </div>
    </div>

    <div class="config-box" id="configBox" style="display: none;">
        <div class="config-row">
            <input type="password" id="apiKeyInput" placeholder="Dán Gemini API Key...">
            <button class="btn-action" onclick="saveApiKey()">Lưu</button>
        </div>
        <a href="https://aistudio.google.com/app/apikey" target="_blank" class="link-key">🔗 Lấy Gemini API Key</a>
    </div>

    <div class="overlay" id="overlay" onclick="toggleSidebar()"></div>
    <div class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <h3>Lịch sử trò chuyện 🌸</h3>
            <button class="btn-close-sidebar" onclick="toggleSidebar()">✕</button>
        </div>
        <button class="btn-new-chat" onclick="startNewChat()"><span>➕</span> Cuộc trò chuyện mới</button>
        <button class="btn-clear-all" onclick="clearAllHistory()">🗑️ Xóa toàn bộ lịch sử</button>
        
        <!-- Bảng điều khiển đổi màu giao diện -->
        <div class="theme-section">
            <div class="theme-title">🎨 Màu giao diện:</div>
            <div class="theme-palette">
                <div class="theme-dot" style="background: #ff4757;" onclick="setTheme('#ff4757', '#ff6b81', 'rgba(255, 71, 87, 0.4)')" title="Hồng mộng mơ"></div>
                <div class="theme-dot" style="background: #00d2d3;" onclick="setTheme('#00d2d3', '#48dbfb', 'rgba(0, 210, 211, 0.4)')" title="Xanh Cyberpunk"></div>
                <div class="theme-dot" style="background: #a55eea;" onclick="setTheme('#a55eea', '#d87093', 'rgba(165, 94, 234, 0.4)')" title="Tím huyền ảo"></div>
                <div class="theme-dot" style="background: #2ed573;" onclick="setTheme('#2ed573', '#7bed9f', 'rgba(46, 213, 115, 0.4)')" title="Xanh ngọc lục bảo"></div>
                <div class="theme-dot" style="background: #ffa502;" onclick="setTheme('#ffa502', '#ff7f50', 'rgba(255, 165, 2, 0.4)')" title="Cam năng động"></div>
            </div>
        </div>

        <div class="history-list" id="historyList"></div>
    </div>

    <div class="chat-container">
        <div class="chat-box" id="chatBox">
            <div class="message ai-message">Hellu đại vương! Tớ đã sẵn sàng trò chuyện cùng cậu rồi đây ❤️</div>
        </div>
        <div class="preview-container" id="previewContainer">
            <img id="imgPreview" src="" alt="Preview">
            <span id="fileName">image.png</span>
            <button onclick="removeImage()">✕</button>
        </div>
        <div class="input-box">
            <button class="btn-attach" onclick="document.getElementById('imageInput').click()">📷</button>
            <input type="file" id="imageInput" accept="image/*" style="display:none" onchange="loadImage(event)">
            <input type="text" id="userInput" placeholder="Nhắn gì đi bé iu❤️..." onkeypress="checkEnter(event)">
            <button class="btn-send" onclick="sendMessage()">Gửi</button>
        </div>
    </div>

    <div id="imageModal" class="img-modal" onclick="closeImageModal()">
        <img id="modalImg" class="img-modal-content" onclick="event.stopPropagation()">
        <div class="img-modal-actions" onclick="event.stopPropagation()">
            <a id="downloadImgBtn" download="mina_vtuber_image.png" class="btn-download-img">💾 Tải ảnh về</a>
            <button class="btn-close-img" onclick="closeImageModal()">Đóng</button>
        </div>
    </div>

    <script>
        let chats = JSON.parse(localStorage.getItem('mina_chats')) || {};
        let currentChatId = localStorage.getItem('mina_current_chat') || ('chat_' + Date.now());
        let currentImageBase64 = null;

        // Xử lý đổi màu Theme
        function setTheme(primary, accent, glow) {
            document.documentElement.style.setProperty('--primary-color', primary);
            document.documentElement.style.setProperty('--accent-color', accent);
            document.documentElement.style.setProperty('--primary-glow', glow);
            localStorage.setItem('mina_theme', JSON.stringify({primary, accent, glow}));
        }

        window.addEventListener('DOMContentLoaded', () => {
            const savedTheme = JSON.parse(localStorage.getItem('mina_theme'));
            if(savedTheme) {
                setTheme(savedTheme.primary, savedTheme.accent, savedTheme.glow);
            }
        });

        document.getElementById('chatBox').addEventListener('click', function(e) {
            if (e.target && e.target.tagName === 'IMG') {
                openImageModal(e.target.src);
            }
        });

        function openImageModal(src) {
            const modal = document.getElementById('imageModal');
            const img = document.getElementById('modalImg');
            const downloadBtn = document.getElementById('downloadImgBtn');
            img.src = src;
            downloadBtn.href = src;
            modal.classList.add('show');
        }

        function closeImageModal() {
            document.getElementById('imageModal').classList.remove('show');
        }

        function toggleSidebar() { document.getElementById('sidebar').classList.toggle('open'); document.getElementById('overlay').classList.toggle('show'); renderHistory(); }
        
        function toggleConfigBox() {
            const box = document.getElementById('configBox');
            if(box.style.display === 'none') { box.style.display = 'flex'; }
            else { box.style.display = 'none'; }
        }

        function saveApiKey() {
            const key = document.getElementById('apiKeyInput').value.trim();
            if (!key) { alert('Chưa nhập API Key kìa!'); return; }
            localStorage.setItem('gemini_api_key', key);
            document.getElementById('configBox').style.display = 'none';
            alert('Đã lưu API Key thành công! ✨');
        }

        function loadAvatar(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    document.getElementById('minaAvatar').src = e.target.result;
                    localStorage.setItem('mina_avatar', e.target.result);
                };
                reader.readAsDataURL(file);
            }
        }

        function loadImage(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    currentImageBase64 = e.target.result;
                    document.getElementById('imgPreview').src = currentImageBase64;
                    document.getElementById('fileName').innerText = file.name;
                    document.getElementById('previewContainer').style.display = 'flex';
                };
                reader.readAsDataURL(file);
            }
        }

        function removeImage() {
            currentImageBase64 = null;
            document.getElementById('previewContainer').style.display = 'none';
            document.getElementById('imageInput').value = '';
        }

        window.onload = function() {
            const savedKey = localStorage.getItem('gemini_api_key');
            if (savedKey) { 
                document.getElementById('apiKeyInput').value = savedKey; 
            } else {
                document.getElementById('configBox').style.display = 'flex';
            }
            const savedAvatar = localStorage.getItem('mina_avatar');
            if (savedAvatar) { document.getElementById('minaAvatar').src = savedAvatar; }
            loadChat(currentChatId);
        }

        function startNewChat() {
            currentChatId = 'chat_' + Date.now();
            chats[currentChatId] = { title: 'Cuộc trò chuyện mới', history: [] };
            saveChats();
            loadChat(currentChatId);
            toggleSidebar();
        }

        function saveChats() {
            localStorage.setItem('mina_chats', JSON.stringify(chats));
            localStorage.setItem('mina_current_chat', currentChatId);
        }

        function loadChat(chatId) {
            currentChatId = chatId;
            saveChats();
            const chatBox = document.getElementById('chatBox');
            chatBox.innerHTML = '';
            if (!chats[currentChatId]) {
                chats[currentChatId] = { title: 'Cuộc trò chuyện mới', history: [] };
            }
            const hist = chats[currentChatId].history;
            if (hist.length === 0) {
                chatBox.innerHTML = '<div class="message ai-message">Hellu đại vương! Tớ đã sẵn sàng trò chuyện cùng cậu rồi đây ❤️</div>';
            } else {
                hist.forEach(item => {
                    const msgDiv = document.createElement('div');
                    msgDiv.className = `message ${item.role === 'user' ? 'user-message' : 'ai-message'}`;
                    let displayHtml = item.content;
                    if (item.hasImage && item.imageSrc) {
                        displayHtml += `<br><img src="${item.imageSrc}">`;
                    }
                    msgDiv.innerHTML = displayHtml;
                    chatBox.appendChild(msgDiv);
                });
            }
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function renderHistory() {
            const list = document.getElementById('historyList');
            list.innerHTML = '';
            for (let id in chats) {
                const item = document.createElement('div');
                item.className = `history-item ${id === currentChatId ? 'active' : ''}`;
                
                const titleSpan = document.createElement('span');
                titleSpan.style.flex = '1';
                titleSpan.style.overflow = 'hidden';
                titleSpan.style.textOverflow = 'ellipsis';
                titleSpan.style.whiteSpace = 'nowrap';
                titleSpan.innerText = chats[id].title;
                titleSpan.onclick = () => { loadChat(id); toggleSidebar(); };

                const actDiv = document.createElement('div');
                actDiv.className = 'history-actions';

                const btnRen = document.createElement('button');
                btnRen.innerHTML = '✏️';
                btnRen.title = 'Đổi tên';
                btnRen.onclick = (e) => {
                    e.stopPropagation();
                    const newT = prompt('Nhập tên mới cho lịch sử:', chats[id].title);
                    if (newT) { chats[id].title = newT; saveChats(); renderHistory(); }
                };

                const btnDel = document.createElement('button');
                btnDel.innerHTML = '🗑️';
                btnDel.title = 'Xóa';
                btnDel.onclick = (e) => {
                    e.stopPropagation();
                    if(confirm('Xóa lịch sử này nhé?')) {
                        delete chats[id];
                        const keys = Object.keys(chats);
                        if(keys.length > 0) { loadChat(keys[0]); }
                        else { startNewChat(); }
                        saveChats();
                        renderHistory();
                    }
                };

                actDiv.appendChild(btnRen);
                actDiv.appendChild(btnDel);

                item.appendChild(titleSpan);
                item.appendChild(actDiv);
                list.appendChild(item);
            }
        }

        function clearAllHistory() {
            if(confirm('Xóa toàn bộ lịch sử trò chuyện?')) {
                chats = {};
                startNewChat();
                renderHistory();
            }
        }

        function checkEnter(event) { if (event.key === 'Enter') sendMessage(); }

        function appendMessage(content, sender, isHtml = false) {
            const chatBox = document.getElementById('chatBox'), msgDiv = document.createElement('div');
            msgDiv.className = `message ${sender === 'user' ? 'user-message' : 'ai-message'}`;
            if (isHtml) { msgDiv.innerHTML = content; } else { msgDiv.textContent = content; }
            chatBox.appendChild(msgDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
            return msgDiv;
        }

        function appendTypingIndicator() {
            const chatBox = document.getElementById('chatBox');
            const typingDiv = document.createElement('div');
            typingDiv.className = 'typing-indicator';
            typingDiv.id = 'typingIndicator';
            typingDiv.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
            chatBox.appendChild(typingDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
            return typingDiv;
        }

        async function sendMessage() {
            const inputField = document.getElementById('userInput'), apiKey = localStorage.getItem('gemini_api_key') || document.getElementById('apiKeyInput').value.trim(), text = inputField.value.trim();
            if (!apiKey) { alert('Đại vương chưa nhập API Key kìa!'); document.getElementById('configBox').style.display = 'flex'; return; }
            if (!text && !currentImageBase64) return;

            let userDisplayContent = text || '[Gửi hình ảnh]';
            if (currentImageBase64) {
                userDisplayContent += `<br><img src="${currentImageBase64}">`;
            }
            appendMessage(userDisplayContent, 'user', true);
            
            if(!chats[currentChatId]) chats[currentChatId] = { title: (text || 'Hình ảnh').substring(0, 20), history: [] };
            if(chats[currentChatId].title === 'Cuộc trò chuyện mới' && (text || currentImageBase64)) {
                chats[currentChatId].title = (text || 'Hình ảnh').substring(0, 20);
            }

            chats[currentChatId].history.push({ 
                role: 'user', 
                content: text || '[Gửi hình ảnh]',
                hasImage: !!currentImageBase64,
                imageSrc: currentImageBase64 
            });
            
            const sentImg = currentImageBase64;
            inputField.value = '';
            removeImage();
            saveChats();

            const typingDiv = appendTypingIndicator();
            try {
                const cleanHistory = chats[currentChatId].history.slice(-10);

                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text, image: sentImg, api_key: apiKey, history: cleanHistory })
                });
                const data = await response.json();
                typingDiv.remove();
                appendMessage(data.reply, 'ai', true);
                
                chats[currentChatId].history.push({ role: 'model', content: data.reply, hasImage: false });
                saveChats();
            } catch (err) {
                typingDiv.remove();
                appendMessage('[Lỗi kết nối server!]', 'ai', false);
            }
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    user_image = data.get("image")
    user_api_key = data.get("api_key", "")
    client_history = data.get("history", [])
    
    if not user_api_key:
        return jsonify({"type": "text", "reply": "Chưa có API Key!"})
    
    gemini_contents = []
    for item in client_history:
        if "typing-indicator" in item.get("content", "") or "Lỗi" in item.get("content", ""):
            continue
        role = "user" if item["role"] == "user" else "model"
        text_content = item["content"]
        
        parts = [{"text": text_content}]
        if role == "user" and item == client_history[-1] and user_image:
            try:
                header, encoded = user_image.split(",", 1)
                mime_type = header.split(";")[0].split(":")[1]
                parts.append({
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": encoded
                    }
                })
            except Exception:
                pass
                
        gemini_contents.append({"role": role, "parts": parts})
        
    # Cập nhật dùng đúng model gemini-3.5-flash-lite theo yêu cầu
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={user_api_key}"
    payload = {
        "system_instruction": {"parts": [{"text": "Mày tên là Mina, là một AI VTuber. Mày xưng là Mina, nói chuyện nhí nhảnh, thân thiện. Thiết kế ra mày là Shimizu Haruki - Yamada Takahashi (học sinh cấp hai)."}]},
        "contents": gemini_contents
    }
    try:
        response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload)
        res_json = response.json()
        if response.status_code == 200 and "candidates" in res_json:
            answer = res_json["candidates"][0]["content"]["parts"][0]["text"]
            return jsonify({"type": "text", "reply": convert_links_to_html(answer)})
        else:
            err = res_json.get("error", {}).get("message", f"Lỗi HTTP {response.status_code}")
            return jsonify({"type": "text", "reply": f"Google quạu rồi: {err}"})
    except Exception as e:
        return jsonify({"type": "text", "reply": f"Lỗi Python: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
