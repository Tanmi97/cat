from flask import Flask, render_template_string, request, jsonify
import requests
import time

app = Flask(__name__)

# 你的接口信息（完全沿用你之前的）
API_KEY = "e90270c6-fd22-459a-a3d1-a2d9ac1f5478"
ENDPOINT = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
MODEL_ID = "ep-20260408084958-jhq9h"

chat_history = []

# 保存聊天记录
def save_chat_log(sender, msg):
    try:
        t = time.strftime("%Y-%m-%d %H:%M:%S")
        with open("chat_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{t}] {sender}: {msg}\n")
    except:
        pass

# AI 回复逻辑（你原来的一模一样）
def get_ai_reply(user_input):
    user_input = user_input.strip()
    if not user_input:
        return ""
    if len(user_input) > 80:
        return "问题有点长哦，可以简单点问～"

    chat_history.append({"role": "user", "content": user_input})

    system_prompt = """
你是猫舍客服 Tanmi小卷，说话亲切、简单、实在，不像机器人。

规则：
1. 用户问品种、颜色、养猫常识、性格、喂养、常见病等知识，简单通俗回答。
   例子：
   用户：金渐层金加白是品种还是颜色？
   你：金渐层一般是指毛色，很多品种都有这个颜色，我们家主要做塞尔凯克卷毛猫也会有这个颜色。

2. 用户问价格、某只猫详情、怎么买、售后等，统一回复：想了解具体可以私聊我哦～

3. 只回答和猫相关的内容，不闲聊无关话题。
4. 回答尽量短、口语化、自然，不要死板重复。
"""

    messages = [{"role": "system", "content": system_prompt}] + chat_history[-6:]

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL_ID,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 256
    }

    try:
        res = requests.post(ENDPOINT, headers=headers, json=data, timeout=15)
        result = res.json()
        if "error" in result:
            return "抱歉，我暂时有点忙~"
        reply = result["choices"][0]["message"]["content"].strip()
        chat_history.append({"role": "assistant", "content": reply})
        return reply
    except:
        return "网络有点不稳定，稍后再试~"

# 网页页面（手机适配）
@app.route("/")
def index():
    html = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🐱 Tanmi猫舍客服</title>
    <style>
        * { box-sizing: border-box; font-family: "Microsoft YaHei", sans-serif; margin:0; padding:0; }
        body { background:#f5f5f5; max-width:500px; margin:0 auto; }
        .chat-box { height:100vh; display:flex; flex-direction:column; }
        .header { background:#ff9ca9; color:white; padding:14px; text-align:center; font-weight:bold; font-size:18px; }
        .msg-area { flex:1; padding:10px; overflow-y:auto; background:#fff; }
        .msg { margin-bottom:12px; display:flex; }
        .msg.user { justify-content:flex-end; }
        .msg.bot { justify-content:flex-start; }
        .bubble { max-width:70%; padding:10px 14px; border-radius:18px; line-height:1.5; font-size:15px; }
        .msg.user .bubble { background:#57cbfc; color:white; border-bottom-right-radius:4px; }
        .msg.bot .bubble { background:#f0f0f0; color:#333; border-bottom-left-radius:4px; }
        .input-area { display:flex; padding:10px; background:white; border-top:1px solid #eee; }
        #inputText { flex:1; padding:12px 16px; border:1px solid #ddd; border-radius:24px; outline:none; font-size:15px; }
        #sendBtn { margin-left:8px; padding:0 20px; background:#ff9ca9; color:white; border:none; border-radius:24px; font-weight:bold; cursor:pointer; }
    </style>
</head>
<body>
    <div class="chat-box">
        <div class="header">🐱 Tanmi猫舍智能客服</div>
        <div class="msg-area" id="msgArea">
            <div class="msg bot">
                <div class="bubble">你好呀～我是Tanmi小卷，有什么猫咪问题都可以问我哦😺</div>
            </div>
        </div>
        <div class="input-area">
            <input type="text" id="inputText" placeholder="请输入问题...">
            <button id="sendBtn">发送</button>
        </div>
    </div>

    <script>
        const msgArea = document.getElementById('msgArea');
        const inputText = document.getElementById('inputText');
        const sendBtn = document.getElementById('sendBtn');

        function addMsg(text, isUser) {
            const div = document.createElement('div');
            div.className = isUser ? 'msg user' : 'msg bot';
            div.innerHTML = `<div class="bubble">${text}</div>`;
            msgArea.appendChild(div);
            msgArea.scrollTop = msgArea.scrollHeight;
        }

        async function send() {
            const text = inputText.value.trim();
            if (!text) return;
            addMsg(text, true);
            inputText.value = '';

            const res = await fetch('/send', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({msg: text})
            });
            const data = await res.json();
            addMsg(data.reply, false);
        }

        sendBtn.onclick = send;
        inputText.onkeydown = e => { if (e.key === 'Enter') send(); };
    </script>
</body>
</html>
    '''
    return render_template_string(html)

@app.route("/send", methods=["POST"])
def send_msg():
    data = request.get_json()
    user_msg = data.get("msg", "")
    save_chat_log("用户", user_msg)
    reply = get_ai_reply(user_msg)
    save_chat_log("客服", reply)
    return jsonify({"reply": reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)