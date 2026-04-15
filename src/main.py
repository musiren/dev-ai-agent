"""Entry point: June orchestrates the team to build a Rust CLI chatbot."""

import os
from agents import JuneAgent


def main() -> None:
    june = JuneAgent()
    result = june.orchestrate(
        "Rust로 CLI 챗봇을 만들어줘. 저장 위치: src/chatbot/\n"
        "\n"
        "## 파일 구조\n"
        "- src/chatbot/Cargo.toml  : Rust 패키지 설정\n"
        "- src/chatbot/src/main.rs : REPL 루프 + handle_input() + 인라인 테스트\n"
        "\n"
        "## Cargo.toml 내용\n"
        "[package]\n"
        "name = \"chatbot\"\n"
        "version = \"0.1.0\"\n"
        "edition = \"2021\"\n"
        "\n"
        "## main.rs 구현 요구사항\n"
        "1. handle_input(input: &str) -> Option<String> 함수 구현\n"
        "   - '/'로 시작하지 않으면 None 반환 (무시)\n"
        "   - /시나리오  → Some(\"시나리오를 작성합니다\")\n"
        "   - /런시나리오 → Some(\"테스트를 수행합니다\")\n"
        "   - /종료      → Some(\"종료합니다.\")\n"
        "   - 그 외 /커맨드 → Some(\"알 수 없는 커맨드: <입력>\")\n"
        "\n"
        "2. main() REPL 루프\n"
        "   - '> ' 프롬프트 출력 후 stdin 한 줄 읽기\n"
        "   - handle_input() 결과가 Some이면 출력\n"
        "   - /종료 입력 시 루프 종료\n"
        "   - 일반 텍스트는 출력 없이 다음 프롬프트로\n"
        "\n"
        "3. #[cfg(test)] 인라인 테스트 (5개)\n"
        "   - test_시나리오, test_런시나리오, test_종료\n"
        "   - test_알수없는_커맨드, test_일반_텍스트는_무시\n"
        "\n"
        "## 검증\n"
        "cargo test → 5 passed\n"
        "cargo run  → /커맨드 동작 확인\n"
    )

    print(f"\n{'='*60}")
    print("팀 작업 완료 요약")
    print(f"{'='*60}")
    print(f"성공 여부: {result['success']}")
    print(f"반복 횟수: {result['iterations']}")
    print(f"\n{result['summary']}")

    # 결과물 저장
    artifacts = result["artifacts"]
    os.makedirs("src/chatbot/src", exist_ok=True)

    if artifacts["code"]:
        with open("src/chatbot/src/main.rs", "w", encoding="utf-8") as f:
            f.write(artifacts["code"])
        print("\n[저장됨] src/chatbot/src/main.rs")

    if artifacts["tests"]:
        # Rust는 인라인 테스트 — 별도 파일 없음, 리뷰로 저장
        with open("src/chatbot/test_report.txt", "w", encoding="utf-8") as f:
            f.write(artifacts["tests"])
        print("[저장됨] src/chatbot/test_report.txt")

    if artifacts["review"]:
        with open("src/chatbot/review_report.txt", "w", encoding="utf-8") as f:
            f.write(artifacts["review"])
        print("[저장됨] src/chatbot/review_report.txt")


if __name__ == "__main__":
    main()
