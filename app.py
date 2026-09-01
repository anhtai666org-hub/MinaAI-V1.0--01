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
        body { background-color: #121212; color: #ffffff; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; overflow: hidden; }
        .btn-menu { position: absolute; top: 15px; left: 15px; background: #1e1e1e; color: #ff4757; border: 1px solid #333; padding: 8px 12px; border-radius: 8px; cursor: pointer; z-index: 10; }
        .sidebar { position: fixed; top: 0; left: -300px; width: 280px; height: 100%; background: #181818; border-right: 1px solid #333; transition: left 0.3s ease; z-index: 100; display: flex; flex-direction: column; padding: 15px; box-sizing: border-box; }
        .sidebar.open { left: 0; }
        .sidebar-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px solid #333; padding-bottom: 10px; }
        .sidebar-header h3 { margin: 0; color: #ff6b81; font-size: 16px; }
        .btn-close-sidebar { background: none; border: none; color: #aaa; font-size: 18px; cursor: pointer; }
        .btn-new-chat { background: #252525; color: white; border: 1px solid #444; padding: 10px; border-radius: 8px; cursor: pointer; text-align: left; font-size: 14px; margin-bottom: 10px; display: flex; align-items: center; gap: 8px; }
        .btn-clear-all { background: #2a1518; color: #ff4757; border: 1px solid #442226; padding: 8px; border-radius: 8px; cursor: pointer; text-align: center; font-size: 13px; margin-bottom: 15px; font-weight: bold; }
        .history-list { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 6px; }
        .history-item { background: #222; padding: 10px; border-radius: 6px; font-size: 13px; cursor: pointer; display: flex; align-items: center; justify-content: space-between; color: #ddd; border: 1px solid transparent; }
        .history-item:hover { background: #2a2a2a; border-color: #555; }
        .history-item.active { background: #ff4757; color: white; }
        .history-actions { display: flex; gap: 5px; }
        .history-actions button { background: none; border: none; cursor: pointer; font-size: 12px; color: inherit; padding: 2px 4px; }
        .overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: none; z-index: 99; }
        .overlay.show { display: block; }
        .config-box { margin-bottom: 8px; background: #1e1e1e; padding: 10px 15px; border-radius: 8px; border: 1px solid #333; width: 90%; max-width: 450px; display: flex; flex-direction: column; gap: 8px; box-sizing: border-box; }
        .config-row { display: flex; gap: 6px; }
        .config-box input { flex: 1; padding: 8px; border: 1px solid #444; background: #121212; color: white; border-radius: 5px; outline: none; font-size: 13px; }
        .btn-action { background-color: #ff4757; color: white; border: none; padding: 8px 14px; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 13px; }
        .link-key { font-size: 12px; color: #ff6b81; text-decoration: none; text-align: right; }
        .vtuber-container { text-align: center; margin-bottom: 8px; }
        .avatar-box { width: 100px; height: 100px; border-radius: 50%; border: 3px solid #ff4757; overflow: hidden; margin: 0 auto 5px auto; background-color: #222; cursor: pointer; }
        .avatar-box img { width: 100%; height: 100%; object-fit: cover; }
        .avatar-btns { display: flex; justify-content: center; gap: 10px; margin-bottom: 6px; }
        .action-chip { background: transparent; border: 1px solid #444; color: #ccc; padding: 3px 10px; border-radius: 12px; font-size: 11px; cursor: pointer; display: flex; align-items: center; gap: 4px; }
        .action-chip:hover { border-color: #ff4757; color: #ff6b81; }
        .chat-container { width: 90%; max-width: 450px; background: #1e1e1e; border-radius: 12px; border: 1px solid #333; display: flex; flex-direction: column; height: 340px; box-sizing: border-box; }
        .chat-box { flex: 1; padding: 12px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
        .message { padding: 10px 14px; border-radius: 10px; max-width: 85%; word-wrap: break-word; font-size: 14px; white-space: pre-wrap; }
        .user-message { background: #ff4757; color: white; align-self: flex-end; }
        .ai-message { background: #333; color: #ff6b81; align-self: flex-start; border: 1px solid #444; }
        .message img { max-width: 100%; border-radius: 6px; margin-top: 5px; display: block; cursor: pointer; transition: transform 0.2s; }
        .message img:hover { transform: scale(1.02); }
        .preview-container { padding: 5px 12px; background: #252525; display: none; align-items: center; gap: 10px; border-top: 1px solid #333; }
        .preview-container img { width: 35px; height: 35px; object-fit: cover; border-radius: 4px; }
        .preview-container span { font-size: 12px; color: #aaa; flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .preview-container button { background: transparent; border: none; color: #ff4757; cursor: pointer; font-weight: bold; }
        .input-box { display: flex; padding: 10px; border-top: 1px solid #333; background: #252525; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px; align-items: center; gap: 5px; box-sizing: border-box; }
        .input-box input[type="text"] { flex: 1; padding: 9px; border: 1px solid #444; background: #121212; color: white; border-radius: 6px; outline: none; font-size: 13px; }
        .btn-attach { background: #333; color: white; border: 1px solid #555; padding: 9px 10px; border-radius: 6px; cursor: pointer; font-size: 14px; }
        .btn-send { background: #ff4757; color: white; border: none; padding: 9px 14px; border-radius: 6px; cursor: pointer; font-weight: bold; }

        /* Modal xem ảnh phóng to */
        .img-modal { display: none; position: fixed; z-index: 1000; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); flex-direction: column; justify-content: center; align-items: center; }
        .img-modal.show { display: flex; }
        .img-modal-content { max-width: 90%; max-height: 75%; border-radius: 8px; object-fit: contain; }
        .img-modal-actions { margin-top: 15px; display: flex; gap: 12px; }
        .btn-download-img { background: #ff4757; color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 13px; border: none; cursor: pointer; }
        .btn-close-img { background: #333; color: white; padding: 8px 16px; border-radius: 6px; border: 1px solid #555; font-size: 13px; cursor: pointer; }
    </style>
</head>
<body>
    <button class="btn-menu" onclick="toggleSidebar()">☰</button>
    <div class="overlay" id="overlay" onclick="toggleSidebar()"></div>
    <div class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <h3>Lịch sử trò chuyện 🌸</h3>
            <button class="btn-close-sidebar" onclick="toggleSidebar()">✕</button>
        </div>
        <button class="btn-new-chat" onclick="startNewChat()"><span>➕</span> Cuộc trò chuyện mới</button>
        <button class="btn-clear-all" onclick="clearAllHistory()">🗑️ Xóa toàn bộ lịch sử</button>
        <div class="history-list" id="historyList"></div>
    </div>
    <div class="config-box" id="configBox">
        <div class="config-row">
            <input type="password" id="apiKeyInput" placeholder="Dán Gemini API Key vào đây...">
            <button class="btn-action" onclick="saveApiKey()">OK</button>
        </div>
        <a href="https://aistudio.google.com/app/apikey" target="_blank" class="link-key">🔗 Lấy Gemini API Key tại đây</a>
    </div>
    <div class="vtuber-container">
        <div class="avatar-box" onclick="document.getElementById('avatarInput').click()">
            <img id="minaAvatar" src="https://api.iconify.design/fluent-emoji:cherry-blossom.svg" alt="Avatar">
        </div>
        <input type="file" id="avatarInput" accept="image/*" style="display:none" onchange="loadAvatar(event)">
        <h3 style="margin: 2px 0; color: #ff6b81;">Mina VTuber (v1.0) ✨</h3>
        <div class="avatar-btns">
            <button class="action-chip" onclick="document.getElementById('avatarInput').click()">🖼️ Đổi Avatar</button>
            <button class="action-chip" onclick="toggleConfigBox()">🔒 <span id="toggleKeyText">Thu gọn</span></button>
        </div>
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

    <!-- Modal Xem & Tải Ảnh -->
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

        // Bắt sự kiện click vào bất kỳ ảnh nào trong hộp chat
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
            const txt = document.getElementById('toggleKeyText');
            if(box.style.display === 'none') { box.style.display = 'flex'; txt.innerText = 'Thu gọn'; }
            else { box.style.display = 'none'; txt.innerText = 'Mở rộng'; }
        }
        function saveApiKey() {
            const key = document.getElementById('apiKeyInput').value.trim();
            if (!key) { alert('Chưa nhập API Key kìa!'); return; }
            localStorage.setItem('gemini_api_key', key);
            document.getElementById('configBox').style.display = 'none';
            document.getElementById('toggleKeyText').innerText = 'Mở rộng';
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
                document.getElementById('configBox').style.display = 'none'; 
                document.getElementById('toggleKeyText').innerText = 'Mở rộng';
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
                    msgDiv.innerHTML = item.content;
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
        async function sendMessage() {
            const inputField = document.getElementById('userInput'), apiKey = localStorage.getItem('gemini_api_key') || document.getElementById('apiKeyInput').value.trim(), text = inputField.value.trim();
            if (!apiKey) { alert('Đại vương chưa nhập API Key kìa!'); document.getElementById('configBox').style.display = 'flex'; document.getElementById('toggleKeyText').innerText = 'Thu gọn'; return; }
            if (!text && !currentImageBase64) return;

            let userDisplayContent = text;
            if (currentImageBase64) {
                userDisplayContent += `<br><img src="${currentImageBase64}">`;
            }
            appendMessage(userDisplayContent, 'user', true);
            
            if(!chats[currentChatId]) chats[currentChatId] = { title: text.substring(0, 20) || 'Đoạn chat', history: [] };
            if(chats[currentChatId].title === 'Cuộc trò chuyện mới' && text) {
                chats[currentChatId].title = text.substring(0, 20);
            }
            chats[currentChatId].history.push({ role: 'user', content: userDisplayContent });
            
            const sentImg = currentImageBase64;
            inputField.value = '';
            removeImage();
            saveChats();

            const loadingDiv = appendMessage('Mina đang nghĩ... 💭', 'ai', false);
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text, image: sentImg, api_key: apiKey, history: chats[currentChatId].history })
                });
                const data = await response.json();
                loadingDiv.remove();
                appendMessage(data.reply, 'ai', true);
                chats[currentChatId].history.push({ role: 'model', content: data.reply });
                saveChats();
            } catch (err) {
                loadingDiv.remove();
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
        if "Mina đang nghĩ" in item["content"] or "Lỗi" in item["content"]:
            continue
        role = "user" if item["role"] == "user" else "model"
        gemini_contents.append({"role": role, "parts": [{"text": item["content"]}]})
        
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
