use axum::{routing::{get, post}, Router, Json};
use serde::{Deserialize, Serialize};

mod commands;
use commands::handle_input;

#[derive(Deserialize)]
struct ChatRequest {
    message: String,
}

#[derive(Serialize)]
struct ChatResponse {
    reply: String,
}

async fn chat_handler(Json(req): Json<ChatRequest>) -> Json<ChatResponse> {
    let reply = handle_input(req.message.trim())
        .unwrap_or_default();
    Json(ChatResponse { reply })
}

async fn index_handler() -> axum::response::Html<&'static str> {
    axum::response::Html(HTML)
}

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/", get(index_handler))
        .route("/chat", post(chat_handler));

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    println!("챗봇 서버 실행 중: http://localhost:3000");
    axum::serve(listener, app).await.unwrap();
}

const HTML: &str = r#"<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>챗봇</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #111827; font-family: 'Segoe UI', sans-serif; height: 100vh; display: flex; flex-direction: column; }
  #header {
    background: #1f2937; padding: 14px 20px;
    display: flex; align-items: center; gap: 10px;
    border-bottom: 1px solid #374151; flex-shrink: 0;
  }
  #status-dot { width: 10px; height: 10px; background: #10b981; border-radius: 50%; box-shadow: 0 0 6px #10b981; }
  #header-title { color: #f9fafb; font-size: 15px; font-weight: 600; }
  #messages { flex: 1; padding: 20px; display: flex; flex-direction: column; gap: 14px; overflow-y: auto; }
  .msg-row { display: flex; gap: 10px; align-items: flex-start; }
  .msg-row.user { justify-content: flex-end; }
  .avatar {
    width: 30px; height: 30px; background: #374151; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    color: #9ca3af; font-size: 12px; font-weight: 700; flex-shrink: 0;
  }
  .bubble {
    padding: 10px 14px; font-size: 14px; line-height: 1.5;
    max-width: 70%; word-break: break-word;
  }
  .bubble.bot {
    background: #1f2937; color: #e5e7eb;
    border: 1px solid #374151; border-radius: 4px 14px 14px 14px;
  }
  .bubble.user {
    background: #2563eb; color: white;
    border-radius: 14px 14px 4px 14px;
  }
  .timestamp { color: #6b7280; font-size: 10px; margin-top: 4px; }
  .msg-row.user .timestamp { text-align: right; margin-right: 4px; }
  .msg-row.bot .timestamp { margin-left: 4px; }
  #input-bar {
    padding: 14px 16px; background: #1f2937;
    border-top: 1px solid #374151;
    display: flex; gap: 10px; align-items: center; flex-shrink: 0;
  }
  #input {
    flex: 1; background: #111827; border: 1px solid #374151;
    border-radius: 10px; padding: 10px 16px;
    color: #e5e7eb; font-size: 14px; outline: none;
  }
  #input::placeholder { color: #6b7280; }
  #input:focus { border-color: #2563eb; }
  #send-btn {
    background: #2563eb; color: white; border: none;
    border-radius: 10px; padding: 10px 20px;
    font-size: 14px; font-weight: 600; cursor: pointer;
  }
  #send-btn:hover { background: #1d4ed8; }
</style>
</head>
<body>
<div id="header">
  <div id="status-dot"></div>
  <span id="header-title">챗봇</span>
</div>
<div id="messages">
  <div class="msg-row bot">
    <div class="avatar">B</div>
    <div>
      <div class="bubble bot">안녕하세요! /시나리오, /런시나리오 커맨드를 사용해보세요.</div>
      <div class="timestamp" id="welcome-time"></div>
    </div>
  </div>
</div>
<div id="input-bar">
  <input id="input" type="text" placeholder="/커맨드를 입력하세요..." autocomplete="off" />
  <button id="send-btn">전송</button>
</div>
<script>
  const messagesEl = document.getElementById('messages');
  const inputEl = document.getElementById('input');
  const sendBtn = document.getElementById('send-btn');

  function now() {
    return new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
  }

  document.getElementById('welcome-time').textContent = now();

  function addMessage(text, role) {
    const row = document.createElement('div');
    row.className = `msg-row ${role}`;
    const time = now();
    if (role === 'bot') {
      row.innerHTML = `
        <div class="avatar">B</div>
        <div>
          <div class="bubble bot">${text}</div>
          <div class="timestamp">${time}</div>
        </div>`;
    } else {
      row.innerHTML = `
        <div>
          <div class="bubble user">${text}</div>
          <div class="timestamp">${time}</div>
        </div>`;
    }
    messagesEl.appendChild(row);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  async function send() {
    const msg = inputEl.value.trim();
    if (!msg) return;
    inputEl.value = '';
    addMessage(msg, 'user');
    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg }),
      });
      const data = await res.json();
      if (data.reply) addMessage(data.reply, 'bot');
    } catch {
      addMessage('오류가 발생했습니다.', 'bot');
    }
  }

  sendBtn.addEventListener('click', send);
  inputEl.addEventListener('keydown', e => { if (e.key === 'Enter') send(); });
</script>
</body>
</html>"#;
