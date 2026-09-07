import os, requests, re, json, base64
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
    <title>VTuber AI Live - Multi-Language</title>
    <style>
        :root {
            --primary-color: #ff4757;
            --primary-glow: rgba(255, 71, 87, 0.4);
            --accent-color: #ff6b81;
        }
        body { background-color: #121212; color: #ffffff; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; overflow: hidden; }
        
        .btn-menu { position: absolute; top: 15px; left: 15px; background: #1e1e1e; color: var(--primary-color); border: 1px solid #333; padding: 8px 12px; border-radius: 8px; cursor: pointer; z-index: 10; }
        
        /* Vị trí khoanh đỏ chọn ngôn ngữ */
        .lang-selector-box { position: absolute; top: 15px; left: 65px; z-index: 10; background: #1e1e1e; border: 1px solid #333; border-radius: 8px; padding: 5px 10px; display: flex; align-items: center; gap: 5px; }
        .lang-selector-box select { background: #121212; color: var(--accent-color); border: 1px solid #444; border-radius: 5px; padding: 4px 8px; font-size: 12px; outline: none; cursor: pointer; font-weight: bold; }

        .vtuber-top-right { position: absolute; top: 12px; right: 15px; display: flex; align-items: center; gap: 8px; z-index: 10; background: #1e1e1e; padding: 5px 10px; border-radius: 20px; border: 1px solid #333; }
        .avatar-box { width: 35px; height: 35px; border-radius: 50%; border: 2px solid var(--primary-color); overflow: hidden; background-color: #222; cursor: pointer; flex-shrink: 0; }
        .avatar-box img { width: 100%; height: 100%; object-fit: cover; }
        .vtuber-info { display: flex; flex-direction: column; text-align: left; }
        .vtuber-name { font-size: 12px; color: var(--accent-color); font-weight: bold; margin: 0; }
        .vtuber-actions { display: flex; gap: 5px; margin-top: 1px; }
        .action-chip { background: transparent; border: none; color: #aaa; padding: 0; font-size: 10px; cursor: pointer; text-decoration: underline; }
        .action-chip:hover { color: var(--accent-color); }
        
        .config-box { position: absolute; top: 65px; right: 15px; background: #1e1e1e; padding: 12px 15px; border-radius: 8px; border: 1px solid #333; width: 300px; display: none; flex-direction: column; gap: 8px; z-index: 10; box-shadow: 0 6px 16px rgba(0,0,0,0.6); }
        .config-box textarea { width: 100%; height: 80px; padding: 8px; border: 1px solid #444; background: #121212; color: white; border-radius: 5px; outline: none; font-size: 12px; resize: none; box-sizing: border-box; font-family: monospace; }
        .config-row { display: flex; justify-content: space-between; align-items: center; }
        .btn-action { background-color: var(--primary-color); color: white; border: none; padding: 6px 12px; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 12px; }
        .link-key { font-size: 11px; color: var(--accent-color); text-decoration: none; }

        .chat-container { width: 95%; max-width: 650px; background: #1e1e1e; border-radius: 12px; border: 1px solid #333; display: flex; flex-direction: column; height: 82vh; box-sizing: border-box; margin-top: 30px; box-shadow: 0 8px 24px rgba(0,0,0,0.4); }
        .chat-box { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; scroll-behavior: smooth; }
        
        .message { padding: 10px 14px 22px 14px; border-radius: 10px; max-width: 85%; word-wrap: break-word; font-size: 14px; white-space: pre-wrap; position: relative; }
        .user-message { background: var(--primary-color); color: white; align-self: flex-end; }
        .ai-message { background: #333; color: var(--accent-color); align-self: flex-start; border: 1px solid #444; }
        .message img { max-width: 100%; border-radius: 6px; margin-top: 5px; display: block; cursor: pointer; }
        
        /* Đồng hồ góc dưới bong bóng chat */
        .msg-time { position: absolute; bottom: 5px; right: 12px; font-size: 10px; opacity: 0.7; font-family: monospace; }
        .user-message .msg-time { color: #f1f1f1; }
        .ai-message .msg-time { color: #aaa; }

        .preview-container { padding: 5px 12px; background: #252525; display: none; align-items: center; gap: 10px; border-top: 1px solid #333; }
        .preview-container img { width: 35px; height: 35px; object-fit: cover; border-radius: 4px; }
        .preview-container span { font-size: 12px; color: #aaa; flex: 1; overflow: hidden; text-overflow: ellipsis; }
        .preview-container button { background: transparent; border: none; color: var(--primary-color); cursor: pointer; font-weight: bold; }
        
        .input-box { display: flex; padding: 10px; border-top: 1px solid #333; background: #252525; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px; align-items: center; gap: 6px; box-sizing: border-box; }
        .input-box input[type="text"] { flex: 1; padding: 10px; border: 1px solid #444; background: #121212; color: white; border-radius: 6px; outline: none; font-size: 14px; }
        .btn-attach { background: #333; color: white; border: 1px solid #555; padding: 10px 12px; border-radius: 6px; cursor: pointer; font-size: 14px; }
        .btn-send { background: var(--primary-color); color: white; border: none; padding: 10px 16px; border-radius: 6px; cursor: pointer; font-weight: bold; }
    </style>
</head>
<body>
    <!-- Vị trí khoanh đỏ trên hình yêu cầu: Chọn Ngôn Ngữ -->
    <div class="lang-selector-box">
        <select id="langSelect" onchange="changeLanguage()">
            <option value="vi">🇻🇳 Việt (Ưu tiên)</option>
            <option value="ja">🇯🇵 Nhật</option>
            <option value="zh">🇨🇳 Trung</option>
            <option value="ko">🇰🇷 Hàn</option>
            <option value="en-gb">🇬🇧 Anh</option>
            <option value="en-us">🇺🇸 Mỹ</option>
        </select>
    </div>

    <div class="vtuber-top-right">
        <div class="avatar-box" onclick="document.getElementById('avatarInput').click()" title="Đổi Avatar">
            <img id="minaAvatar" src="https://api.iconify.design/fluent-emoji:cherry-blossom.svg" alt="Avatar">
        </div>
        <input type="file" id="avatarInput" accept="image/*" style="display:none" onchange="loadAvatar(event)">
        <div class="vtuber-info">
            <span class="vtuber-name" id="vtuberNameLabel">Mina VTuber ✨</span>
            <div class="vtuber-actions">
                <button class="action-chip" onclick="toggleConfigBox()" id="btnKeyLabel">Kho API Key</button>
            </div>
        </div>
    </div>

    <div class="config-box" id="configBox">
        <div style="font-size: 12px; color: #aaa; font-weight: bold;" id="configTitleLabel">Nhập danh sách API Key (mỗi dòng 1 key):</div>
        <textarea id="apiKeyInput" placeholder="AIzaSy...&#10;AIzaSy..."></textarea>
        <div class="config-row">
            <a href="https://aistudio.google.com/app/apikey" target="_blank" class="link-key" id="getApiKeyLabel">🔗 Lấy thêm Key</a>
            <button class="btn-action" onclick="saveApiKey()" id="saveKeyLabel">Lưu kho</button>
        </div>
    </div>

    <div class="chat-container">
        <div class="chat-box" id="chatBox">
            <div class="message ai-message">
                <span id="welcomeText">Hellu đại vương! Đồng hồ và hệ thống đa ngôn ngữ đã sẵn sàng ❤️</span>
                <span class="msg-time" id="welcomeTime"></span>
            </div>
        </div>
        <div class="preview-container" id="previewContainer">
            <img id="imgPreview" src="" alt="Preview">
            <span id="fileName">image.png</span>
            <button onclick="removeImage()">✕</button>
        </div>
        <div class="input-box">
            <button class="btn-attach" onclick="document.getElementById('imageInput').click()">📷</button>
            <input type="file" id="imageInput" accept="image/*" style="display:none" onchange="loadImage(event)">
            <input type="text" id="userInput" placeholder="Nhắn gì đi bé iu❤️..." onkeypress="if(event.key==='Enter') sendMessage()">
            <button class="btn-send" id="sendBtnLabel" onclick="sendMessage()">Gửi</button>
        </div>
    </div>

    <script>
        // Cấu hình múi giờ tương ứng cho từng quốc gia
        const timeZones = {
            'vi': 'Asia/Ho_Chi_Minh',
            'ja': 'Asia/Tokyo',
            'zh': 'Asia/Shanghai',
            'ko': 'Asia/Seoul',
            'en-gb': 'Europe/London',
            'en-us': 'America/New_York'
        };

        // Gói tài nguyên ngôn ngữ giao diện (UI Text)
        const uiTexts = {
            'vi': { placeholder: "Nhắn gì đi bé iu❤️...", send: "Gửi", key: "Kho API Key", welcome: "Hellu đại vương! Đồng hồ và hệ thống đa ngôn ngữ đã sẵn sàng ❤️" },
            'ja': { placeholder: "何か話しかけてね、ご主人様❤️...", send: "送信", key: "APIキー倉庫", welcome: "こんにちはご主人様！時計と多言語システムが準備完了しました ❤️" },
            'zh': { placeholder: "说点什么吧主人❤️...", send: "发送", key: "API密钥库", welcome: "你好主人！时钟与多语言系统已准备就绪 ❤️" },
            'ko': { placeholder: "무엇이든 말씀하세요 주인님❤️...", send: "전송", key: "API 키 창고", welcome: "안녕하세요 주인님! 시계와 다국어 시스템이 준비되었습니다 ❤️" },
            'en-gb': { placeholder: "Say something, master❤️...", send: "Send", key: "API Key Pool", welcome: "Hello Master! Clock and multi-language system are ready ❤️" },
            'en-us': { placeholder: "Say something, master❤️...", send: "Send", key: "API Key Pool", welcome: "Hello Master! Clock and multi-language system are ready ❤️" }
        };

        function getCurrentFormattedTime() {
            const lang = document.getElementById('langSelect').value;
            const tz = timeZones[lang] || 'Asia/Ho_Chi_Minh';
            const now = new Date();
            
            // Lấy thời gian chuẩn theo múi giờ quốc gia đó
            const options = {
                timeZone: tz,
                hour: '2-digit', minute: '2-digit', second: '2-digit',
                day: '2-digit', month: '2-digit', year: 'numeric',
                hour12: false
            };
            return new Intl.DateTimeFormat('en-GB', options).format(now);
        }

        function changeLanguage() {
            const lang = document.getElementById('langSelect').value;
            localStorage.setItem('mina_lang', lang);
            
            // Cập nhật chữ giao diện theo ngôn ngữ
            const t = uiTexts[lang] || uiTexts['vi'];
            document.getElementById('userInput').placeholder = t.placeholder;
            document.getElementById('sendBtnLabel').textContent = t.send;
            document.getElementById('btnKeyLabel').textContent = t.key;
            document.getElementById('welcomeText').textContent = t.welcome;
            
            // Cập nhật lại thời gian chào mừng theo múi giờ mới chọn
            document.getElementById('welcomeTime').textContent = getCurrentFormattedTime();
        }

        window.addEventListener('DOMContentLoaded', () => {
            const savedLang = localStorage.getItem('mina_lang');
            if(savedLang) {
                document.getElementById('langSelect').value = savedLang;
            }
            changeLanguage();
        });

        function toggleConfigBox() {
            const box = document.getElementById('configBox');
            box.style.display = box.style.display === 'flex' ? 'none' : 'flex';
        }

        function saveApiKey() {
            const keysText = document.getElementById('apiKeyInput').value.trim();
            if (!keysText) { alert('Chưa nhập key nào kìa đại vương!'); return; }
            localStorage.setItem('gemini_api_keys', keysText);
            document.getElementById('configBox').style.display = 'none';
            alert('Đã lưu kho API Key thành công! ✨');
        }

        function loadAvatar(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    document.getElementById('minaAvatar').src = e.target.result;
                    localStorage.setItem('mina_avatar', e.target.result);
                };
                reader.readAsDataURL(file);
            }
        }

        let selectedImageFile = null;
        function loadImage(event) {
            const file = event.target.files[0];
            if (file) {
                selectedImageFile = file;
                const reader = new FileReader();
                reader.onload = (e) => {
                    document.getElementById('imgPreview').src = e.target.result;
                    document.getElementById('fileName').innerText = file.name;
                    document.getElementById('previewContainer').style.display = 'flex';
                };
                reader.readAsDataURL(file);
            }
        }

        function removeImage() {
            selectedImageFile = null;
            document.getElementById('previewContainer').style.display = 'none';
            document.getElementById('imageInput').value = '';
        }

        window.onload = function() {
            const savedKeys = localStorage.getItem('gemini_api_keys');
            if (savedKeys) { document.getElementById('apiKeyInput').value = savedKeys; }
            const savedAvatar = localStorage.getItem('mina_avatar');
            if (savedAvatar) { document.getElementById('minaAvatar').src = savedAvatar; }
            document.getElementById('welcomeTime').textContent = getCurrentFormattedTime();
        }

        async function sendMessage() {
            const keysText = localStorage.getItem('gemini_api_keys') || document.getElementById('apiKeyInput').value.trim();
            const text = document.getElementById('userInput').value.trim();
            const currentLang = document.getElementById('langSelect').value;
            
            if (!keysText) { alert('Đại vương chưa nhập kho API Key!'); document.getElementById('configBox').style.display = 'flex'; return; }
            if (!text && !selectedImageFile) return;

            let imageBase64Temp = selectedImageFile ? document.getElementById('imgPreview').src : null;
            let userDisplayContent = text || '[Gửi hình ảnh]';
            if (imageBase64Temp) userDisplayContent += `<br><img src="${imageBase64Temp}">`;
            
            const chatBox = document.getElementById('chatBox');
            
            // Tạo bong bóng chat User kèm đồng hồ góc dưới
            const userMsgDiv = document.createElement('div');
            userMsgDiv.className = 'message user-message';
            userMsgDiv.innerHTML = `${userDisplayContent}<span class="msg-time">${getCurrentFormattedTime()}</span>`;
            chatBox.appendChild(userMsgDiv);
            chatBox.scrollTop = chatBox.scrollHeight;

            const formData = new FormData();
            formData.append('message', text);
            formData.append('api_keys', keysText);
            formData.append('lang', currentLang); // Gửi kèm ngôn ngữ lên server
            if (selectedImageFile) formData.append('image', selectedImageFile);

            document.getElementById('userInput').value = '';
            removeImage();

            const typingDiv = document.createElement('div');
            typingDiv.className = 'message ai-message';
            typingDiv.innerHTML = `Mina đang suy nghĩ...<span class="msg-time">${getCurrentFormattedTime()}</span>`;
            chatBox.appendChild(typingDiv);
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const response = await fetch('/chat', { method: 'POST', body: formData });
                const data = await response.json();
                typingDiv.remove();
                
                // Tạo bong bóng chat AI kèm đồng hồ thời gian chuẩn quốc gia đó
                const aiMsgDiv = document.createElement('div');
                aiMsgDiv.className = 'message ai-message';
                aiMsgDiv.innerHTML = `${data.reply}<span class="msg-time">${getCurrentFormattedTime()}</span>`;
                chatBox.appendChild(aiMsgDiv);
                chatBox.scrollTop = chatBox.scrollHeight;
            } catch (err) {
                typingDiv.remove();
                const errDiv = document.createElement('div');
                errDiv.className = 'message ai-message';
                errDiv.innerHTML = `[Lỗi kết nối server!]<span class="msg-time">${getCurrentFormattedTime()}</span>`;
                chatBox.appendChild(errDiv);
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
    user_message = request.form.get("message", "")
    keys_raw = request.form.get("api_keys", "")
    user_lang = request.form.get("lang", "vi")
    uploaded_image = request.files.get("image")
    
    api_keys = [k.strip() for k in keys_raw.replace(",", "\n").split("\n") if k.strip()]
    if not api_keys:
        return jsonify({"reply": "Kho Key trống rỗng, đại vương hãy cấu hình lại!"})
    
    # Ép AI phản hồi đúng ngôn ngữ và truyền thông tin thời gian hiện tại vào system instruction để AI biết chính xác giờ giấc quốc gia đó
    from datetime import datetime
    import pytz
    
    tz_map = {
        'vi': 'Asia/Ho_Chi_Minh',
        'ja': 'Asia/Tokyo',
        'zh': 'Asia/Shanghai',
        'ko': 'Asia/Seoul',
        'en-gb': 'Europe/London',
        'en-us': 'America/New_York'
    }
    target_tz = pytz.timezone(tz_map.get(user_lang, 'Asia/Ho_Chi_Minh'))
    current_time_str = datetime.now(target_tz).strftime('%H:%M:%S ngày %d/%m/%Y')
    
    lang_instructions = {
        'vi': "Hãy trả lời bằng Tiếng Việt. Mày tên là Mina, AI VTuber nhí nhảnh, thân thiện.",
        'ja': "日本語で返答してください。あなたの名前はミナ、元気で親しみやすいVTuberAIです。",
        'zh': "请用中文回答。你的名字是米娜，是一个活泼友好的VTuber虚拟主播。",
        'ko': "한국어로 답변해주세요. 당신의 이름은 미나, 활발하고 친근한 버튜버 AI입니다.",
        'en-gb': "Please reply in British English. Your name is Mina, a cheerful and friendly VTuber AI.",
        'en-us': "Please reply in American English. Your name is Mina, a cheerful and friendly VTuber AI."
    }
    
    system_prompt = f"{lang_instructions.get(user_lang, lang_instructions['vi'])} Lưu ý cực kỳ quan trọng: Thời gian hiện tại theo múi giờ khu vực này là {current_time_str}. Khi đại vương hỏi giờ giấc, hãy dùng chính xác thời gian này để trả lời."

    current_parts = [{"text": user_message if user_message else "Hãy nhận xét về hình ảnh này."}]
    if uploaded_image:
        try:
            image_bytes = uploaded_image.read()
            mime_type = uploaded_image.mimetype or "image/jpeg"
            encoded_data = base64.b64encode(image_bytes).decode("utf-8")
            current_parts.append({
                "inline_data": {"mime_type": mime_type, "data": encoded_data}
            })
        except:
            pass

    gemini_contents = [{"role": "user", "parts": current_parts}]
    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": gemini_contents
    }

    success = False
    final_answer = ""
    
    for key in api_keys:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={key}"
        try:
            response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=15)
            res_json = response.json()
            
            if response.status_code == 200 and "candidates" in res_json:
                final_answer = res_json["candidates"][0]["content"]["parts"][0]["text"]
                success = True
                break
            else:
                continue
        except Exception:
            continue

    if success:
        return jsonify({"reply": convert_links_to_html(final_answer)})
    else:
        return jsonify({"reply": "⚠️ Tất cả các API Key trong kho đều đã cạn quota hoặc bị lỗi!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
