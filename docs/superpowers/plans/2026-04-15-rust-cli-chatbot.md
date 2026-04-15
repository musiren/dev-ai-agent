# Rust CLI Chatbot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `src/chatbot/`에 Rust CLI 챗봇을 만든다. `/커맨드` 형식 입력에만 반응하며 일반 텍스트는 무시한다.

**Architecture:** stdin REPL 루프 → `handle_input()` 함수로 커맨드 분기 → stdout 출력. 커맨드 처리 로직을 별도 순수 함수로 분리해 단위 테스트가 가능하게 한다.

**Tech Stack:** Rust (stable), Cargo, 외부 크레이트 없음

---

## 파일 구조

```
src/chatbot/
├── Cargo.toml       # 패키지 메타데이터
└── src/
    └── main.rs      # REPL 루프 + handle_input() + 인라인 테스트
```

---

### Task 1: Cargo 프로젝트 초기화

**Files:**
- Create: `src/chatbot/Cargo.toml`
- Create: `src/chatbot/src/main.rs`

- [ ] **Step 1: Cargo.toml 생성**

`src/chatbot/Cargo.toml`:
```toml
[package]
name = "chatbot"
version = "0.1.0"
edition = "2021"

[[bin]]
name = "chatbot"
path = "src/main.rs"
```

- [ ] **Step 2: 빌드 확인용 최소 main.rs 생성**

`src/chatbot/src/main.rs`:
```rust
fn main() {}
```

- [ ] **Step 3: 빌드 통과 확인**

```bash
cd src/chatbot
cargo build
```

Expected: `Compiling chatbot v0.1.0` 이후 오류 없이 완료

- [ ] **Step 4: 커밋**

```bash
cd ../..
git add src/chatbot/
git commit -m "chore: init Rust chatbot Cargo project"
```

---

### Task 2: handle_input() 구현 (TDD)

**Files:**
- Modify: `src/chatbot/src/main.rs`

- [ ] **Step 1: 실패하는 테스트 작성**

`src/chatbot/src/main.rs`를 아래로 교체:

```rust
fn main() {}

/// 커맨드 입력을 처리한다.
/// `/`로 시작하는 커맨드면 Some(응답), 일반 텍스트면 None 반환.
fn handle_input(input: &str) -> Option<String> {
    todo!()
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

- [ ] **Step 2: 테스트 실패 확인**

```bash
cd src/chatbot
cargo test
```

Expected: `panicked at 'not yet implemented'` 오류로 실패

- [ ] **Step 3: handle_input() 구현**

`handle_input` 함수를 아래로 교체 (나머지 코드 유지):

```rust
fn handle_input(input: &str) -> Option<String> {
    if !input.starts_with('/') {
        return None;
    }
    let response = match input {
        "/시나리오"    => "시나리오를 작성합니다".to_string(),
        "/런시나리오"  => "테스트를 수행합니다".to_string(),
        "/종료"        => "종료합니다.".to_string(),
        other          => format!("알 수 없는 커맨드: {}", other),
    };
    Some(response)
}
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
cargo test
```

Expected: `test result: ok. 5 passed`

- [ ] **Step 5: 커밋**

```bash
cd ../..
git add src/chatbot/src/main.rs
git commit -m "feat: implement handle_input() with command dispatch"
```

---

### Task 3: REPL 루프 구현

**Files:**
- Modify: `src/chatbot/src/main.rs`

- [ ] **Step 1: main() 구현**

`main()` 함수를 아래로 교체 (handle_input, tests 유지):

```rust
use std::io::{self, BufRead, Write};

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

- [ ] **Step 2: 빌드 확인**

```bash
cd src/chatbot
cargo build
```

Expected: 오류 없이 빌드 완료

- [ ] **Step 3: 동작 수동 확인**

```bash
cargo run
```

입력 시나리오:
```
> /시나리오
시나리오를 작성합니다
> /런시나리오
테스트를 수행합니다
> 일반텍스트
> /없는커맨드
알 수 없는 커맨드: /없는커맨드
> /종료
종료합니다.
```

- [ ] **Step 4: 테스트 전체 재확인**

```bash
cargo test
```

Expected: `test result: ok. 5 passed`

- [ ] **Step 5: 커밋**

```bash
cd ../..
git add src/chatbot/src/main.rs
git commit -m "feat: add REPL loop to chatbot"
```

---

## 검증

```bash
cd src/chatbot
cargo test          # 5 passed
cargo run           # 수동 동작 확인
```
