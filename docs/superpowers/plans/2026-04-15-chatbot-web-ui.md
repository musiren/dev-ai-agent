# Chatbot Web UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 기존 Rust CLI 챗봇에 Axum 웹서버와 심플 다크 채팅 UI를 추가한다.

**Architecture:** `handle_input()`을 `commands.rs`로 분리하고, `main.rs`에 Axum 서버를 추가한다. `GET /`는 인라인 HTML을 서빙하고, `POST /chat`은 JSON으로 커맨드를 받아 응답을 반환한다.

**Tech Stack:** Rust, Axum 0.8, Tokio 1, Serde/serde_json 1

---

## 파일 구조

```
src/chatbot/
├── Cargo.toml          # axum, tokio, serde, serde_json 추가
└── src/
    ├── commands.rs     # handle_input() + 테스트 (main.rs에서 분리)
    └── main.rs         # Axum 서버 + GET / + POST /chat + 인라인 HTML
```

---

### Task 1: Cargo.toml에 의존성 추가

**Files:**
- Modify: `src/chatbot/Cargo.toml`

- [ ] **Step 1: Cargo.toml 전체 교체**

`src/chatbot/Cargo.toml`:
```toml
[package]
name = "chatbot"
version = "0.1.0"
edition = "2021"

[[bin]]
name = "chatbot"
path = "src/main.rs"

[dependencies]
axum = "0.8"
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
```

- [ ] **Step 2: 의존성 다운로드 확인**

```bash
cd src/chatbot
~/.cargo/bin/cargo fetch
```

Expected: 오류 없이 완료 (처음 실행 시 다운로드 발생)

- [ ] **Step 3: 커밋**

```bash
cd ../..
git add src/chatbot/Cargo.toml src/chatbot/Cargo.lock
git commit -m "chore: add axum/tokio/serde dependencies for web UI"
```

---

### Task 2: handle_input()을 commands.rs로 분리

**Files:**
- Create: `src/chatbot/src/commands.rs`
- Modify: `src/chatbot/src/main.rs`

- [ ] **Step 1: commands.rs 생성**

`src/chatbot/src/commands.rs`:
```rust
/// 커맨드 입력을 처리한다.
/// `/`로 시작하는 커맨드면 Some(응답), 일반 텍스트면 None 반환.
pub fn handle_input(input: &str) -> Option<String> {
    if !input.starts_with('/') {
        return None;
    }
    let response = match input {
        "/시나리오"   => "시나리오를 작성합니다".to_string(),
        "/런시나리오" => "테스트를 수행합니다".to_string(),
        "/종료"       => "종료합니다.".to_string(),
        other         => format!("알 수 없는 커맨드: {}", other),
    };
    Some(response)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_시나리오() {
        assert_eq!(
            handle_input("/시나리오"),
            Some("시나리오를 작성합니다".to_string())
        );
    }

    #[test]
    fn test_런시나리오() {
        assert_eq!(
            handle_input("/런시나리오"),
            Some("테스트를 수행합니다".to_string())
        );
    }

    #[test]
    fn test_종료() {
        assert_eq!(
            handle_input("/종료"),
            Some("종료합니다.".to_string())
        );
    }

    #[test]
    fn test_알수없는_커맨드() {
        assert_eq!(
            handle_input("/없는커맨드"),
            Some("알 수 없는 커맨드: /없는커맨드".to_string())
        );
    }

    #[test]
    fn test_일반_텍스트는_무시() {
        assert_eq!(handle_input("안녕"), None);
        assert_eq!(handle_input("hello world"), None);
        assert_eq!(handle_input(""), None);
    }
}
```

- [ ] **Step 2: main.rs를 commands 모듈 사용하도록 교체**

`src/chatbot/src/main.rs` 전체 교체:
```rust
use std::io::{self, BufRead, Write};

mod commands;
use commands::handle_input;

fn main() {
    let stdin = io::stdin();
    print!("> ");
    io::stdout().flush().unwrap();

    for line in stdin.lock().lines() {
        let input = line.unwrap();
        let trimmed = input.trim();

        if let Some(response) = handle_input(trimmed) {
            println!("{}", response);
            if trimmed == "/종료" {
                break;
            }
        }

        print!("> ");
        io::stdout().flush().unwrap();
    }
}
```

- [ ] **Step 3: 테스트 통과 확인**

```bash
cd src/chatbot
~/.cargo/bin/cargo test
```

Expected: `test result: ok. 5 passed`

- [ ] **Step 4: 커밋**

```bash
cd ../..
git add src/chatbot/src/commands.rs src/chatbot/src/main.rs
git commit -m "refactor: extract handle_input() to commands.rs"
```

---

### Task 3: Axum 웹서버 + POST /chat 엔드포인트

**Files:**
- Modify: `src/chatbot/src/main.rs`

- [ ] **Step 1: main.rs 전체 교체 (웹서버 추가)**

`src/chatbot/src/main.rs`:
```rust
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
```

- [ ] **Step 2: 빌드 확인**

```bash
cd src/chatbot
~/.cargo/bin/cargo build
```

Expected: 오류 없이 빌드 완료 (처음 실행 시 axum 컴파일로 시간 소요)

- [ ] **Step 3: 서버 실행 후 브라우저 확인**

```bash
~/.cargo/bin/cargo run
```

브라우저에서 `http://localhost:3000` 접속 후:
- `/시나리오` 입력 → `시나리오를 작성합니다` 응답 확인
- `/런시나리오` 입력 → `테스트를 수행합니다` 응답 확인
- `/종료` 입력 → `종료합니다.` 응답 확인 (서버는 계속 실행)
- 일반 텍스트 입력 → 응답 없음 확인

- [ ] **Step 4: 기존 단위 테스트 통과 확인**

```bash
~/.cargo/bin/cargo test
```

Expected: `test result: ok. 5 passed`

- [ ] **Step 5: 커밋**

```bash
cd ../..
git add src/chatbot/src/main.rs
git commit -m "feat: add Axum web server with dark chat UI"
```

---

## 최종 검증

```bash
cd src/chatbot
~/.cargo/bin/cargo test       # 5 passed
~/.cargo/bin/cargo run        # http://localhost:3000 접속하여 동작 확인
```
