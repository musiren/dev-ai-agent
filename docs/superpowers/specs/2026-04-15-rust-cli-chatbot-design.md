# Rust CLI Chatbot — Design Spec

**Date:** 2026-04-15  
**Location:** `src/chatbot/` (Cargo 프로젝트)

---

## 개요

CLI 기반 챗봇. `/커맨드` 형식의 입력에만 반응하고, 일반 텍스트는 무시한다.

---

## 아키텍처

단일 바이너리 (`src/chatbot/src/main.rs`). stdin REPL 루프에서 입력을 읽어 `match`로 커맨드를 분기한다.

```
stdin → trim → match 커맨드 → stdout 출력
```

---

## 파일 구조

```
src/chatbot/
├── Cargo.toml
└── src/
    └── main.rs
```

---

## 커맨드 목록

| 커맨드 | 출력 |
|--------|------|
| `/시나리오` | `시나리오를 작성합니다` |
| `/런시나리오` | `테스트를 수행합니다` |
| `/종료` | 프로그램 종료 |
| 그 외 `/`로 시작 | `알 수 없는 커맨드: <입력>` |
| `/` 없는 일반 텍스트 | 무시 (출력 없음) |

---

## 구현 방식

- `match` 직접 매칭 (HashMap/트레이트 불필요)
- 새 커맨드 추가 = `match` arm 한 줄 추가
- `loop` + `stdin().read_line()` REPL

---

## 실행 방법

```bash
cd src/chatbot
cargo run
```
