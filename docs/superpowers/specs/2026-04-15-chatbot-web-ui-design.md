# Chatbot Web UI Design Spec

**Date:** 2026-04-15
**Branch:** feat/rust-cli-chatbot (기존 브랜치에 추가)

---

## 개요

기존 Rust CLI 챗봇(`src/chatbot/`)에 Axum 기반 웹 서버와 심플 다크 테마 채팅 UI를 추가한다. CLI 모드는 그대로 유지하고, 웹 모드를 별도로 지원한다.

---

## 아키텍처

```
브라우저 (fetch POST /chat)
    ↕
Axum 웹서버 (src/chatbot/src/main.rs)
    ↕
handle_input() — 기존 커맨드 로직 재사용
```

- `GET /` → `index.html` 서빙 (인라인 HTML 문자열)
- `POST /chat` → `{ "message": "/시나리오" }` 수신 → `{ "reply": "시나리오를 작성합니다" }` 반환
- `/종료` 커맨드는 웹에서는 서버 종료 없이 "종료합니다." 메시지만 반환

---

## 파일 구조

```
src/chatbot/
├── Cargo.toml        # axum, tokio, serde, serde_json 추가
└── src/
    ├── main.rs       # Axum 서버 + 라우팅 + HTML 인라인
    └── commands.rs   # handle_input() 분리 (lib 모듈)
```

`handle_input()`을 `commands.rs`로 분리해 기존 테스트와 웹 핸들러가 모두 참조한다.

---

## 프론트엔드 (인라인 HTML)

단일 `String`으로 `main.rs`에 포함. 외부 파일 불필요.

**UI 구성:**
- 헤더: 온라인 점(초록) + "챗봇" 텍스트
- 메시지 영역: 스크롤 가능, 유저(오른쪽 파란 버블) / 봇(왼쪽 회색 버블) + 타임스탬프
- 입력창 + 전송 버튼 (Enter 키도 동작)
- 배경 `#111827`, 버블 색상 `#2563eb`(유저) / `#1f2937`(봇)

---

## API

### POST /chat
**Request:**
```json
{ "message": "/시나리오" }
```
**Response:**
```json
{ "reply": "시나리오를 작성합니다" }
```
**에러 (빈 메시지):**
```json
{ "reply": "" }
```

---

## 커맨드 동작 (웹)

| 커맨드 | 응답 |
|--------|------|
| `/시나리오` | 시나리오를 작성합니다 |
| `/런시나리오` | 테스트를 수행합니다 |
| `/종료` | 종료합니다. (서버는 유지) |
| `/`로 시작하는 미지원 | 알 수 없는 커맨드: /xxx |
| 일반 텍스트 | (빈 응답, 버블 없음) |

---

## 의존성 추가 (Cargo.toml)

```toml
axum = "0.8"
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
```

---

## 실행 방법

```bash
cd src/chatbot
cargo run --bin chatbot
# → http://localhost:3000
```

---

## 테스트

- `commands.rs`의 `handle_input()` 단위 테스트 5개 유지
- Axum 엔드포인트는 수동 브라우저 확인으로 검증
