# dev-ai-agent

AI Agent 학습을 위한 교육용 프로젝트입니다.  
Claude API를 활용한 멀티에이전트 개발 자동화 시스템과 부가 기능들을 포함합니다.

---

## 주요 기능

### 1. 멀티에이전트 개발 자동화 시스템

`src/agents/` — Claude API 기반의 AI 개발 팀

| 에이전트 | 역할 | 주요 기능 |
|----------|------|-----------|
| **June** (Orchestrator) | 팀 총괄 | 요구사항 분석, 명세 작성, 반복 개선 결정 |
| **March** (Developer) | 코드 구현 | PEP 8 준수 Python 코드 작성, 리팩토링 |
| **April** (Tester) | 테스트 작성 | pytest 단위/통합/엣지 케이스 테스트 |
| **May** (Reviewer) | 코드 리뷰 | 품질·보안·성능 검토, SOLID 원칙 평가 |

**자동화 파이프라인 흐름:**
```
사용자 요청 → June(명세) → March(구현) → April(테스트) → May(리뷰)
                                ↑__________________________|
                                     (리뷰 반영, 최대 3회)
```

**실행 방법:**
```bash
cp .env.example .env   # ANTHROPIC_API_KEY 설정
pip install -e .
python -m src.main
```

---

### 2. 스도쿠 게임

`sudoku_game.py` — PyQt6 기반 독립형 데스크톱 게임

- 3가지 난이도 (쉬움 / 보통 / 어려움)
- 힌트 기능 (가장 쉬운 칸 강조 표시)
- 실시간 타이머 및 최고 기록 저장 (`.sudoku_records.json`)
- 정답 검증

**실행 방법:**
```bash
pip install PyQt6
python sudoku_game.py
```

**웹 버전:** `index.html` (GitHub Pages 배포)

---

### 3. SSH 파일 업로더

`ssh_uploader/` — FastAPI 기반 웹 앱

브라우저에서 SSH 키 인증으로 원격 서버에 파일을 업로드합니다.

- SSH 키 파일 선택으로 원격 서버 연결
- SFTP 원격 디렉토리 트리 탐색
- 드래그&드롭 다중 파일 업로드
- 업로드 진행률 및 결과 표시

**실행 방법:**
```bash
pip install -r ssh_uploader/requirements.txt
uvicorn ssh_uploader.app:app --reload --port 8000
# http://localhost:8000 접속
```

**API 엔드포인트:**
| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/connect` | SSH 키로 서버 연결 |
| GET | `/api/browse` | 원격 디렉토리 목록 조회 |
| POST | `/api/upload` | 다중 파일 업로드 |
| POST | `/api/disconnect` | 연결 해제 |

---

## 기술 스택

- **Python 3.12+**
- **Anthropic SDK** — Claude API (멀티에이전트)
- **FastAPI + uvicorn** — 웹 서버 (SSH 업로더)
- **Paramiko** — SSH/SFTP 연결
- **PyQt6** — 데스크톱 GUI (스도쿠)
- **pytest / pytest-asyncio / pytest-mock** — 테스트

---

## 프로젝트 구조

```
dev-ai-agent/
├── src/
│   ├── agents/
│   │   ├── base.py        # BaseAgent (API 호출, 스트리밍)
│   │   ├── models.py      # 공유 데이터 모델
│   │   ├── march.py       # Developer 에이전트
│   │   ├── april.py       # Tester 에이전트
│   │   ├── may.py         # Reviewer 에이전트
│   │   └── june.py        # Orchestrator 에이전트
│   ├── ssh_uploader/
│   │   ├── app.py         # FastAPI 서버
│   │   ├── upload.html    # 프론트엔드
│   │   └── requirements.txt
│   ├── sudoku/
│   │   ├── sudoku_game.py # PyQt6 스도쿠 게임
│   │   └── sudoku.html    # 웹 버전
│   └── main.py            # 진입점
├── index.html             # GitHub Pages 진입점
├── tests/                 # pytest 테스트 스위트
├── pyproject.toml
└── .env.example
```

---

## 환경 설정

```bash
# 의존성 설치
pip install -e .

# API 키 설정
cp .env.example .env
# .env 파일에 ANTHROPIC_API_KEY=your_key_here 입력
```
