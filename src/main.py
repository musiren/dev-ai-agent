"""Entry point: June orchestrates the team to build a PyQt6 Sudoku game."""

from agents import JuneAgent


def main() -> None:
    june = JuneAgent()
    result = june.orchestrate(
        "PyQt6로 스도쿠 게임을 만들어주세요.\n"
        "요구사항:\n"
        "- PyQt6 기반 GUI\n"
        "- 9x9 스도쿠 보드 표시\n"
        "- 새 게임 생성, 숫자 입력, 정답 검증 기능\n"
        "- 힌트 기능 (틀린 칸 강조)\n"
    )

    print(f"\n{'='*60}")
    print("팀 작업 완료 요약")
    print(f"{'='*60}")
    print(f"성공 여부: {result['success']}")
    print(f"반복 횟수: {result['iterations']}")
    print(f"\n{result['summary']}")

    # 결과물 저장
    artifacts = result["artifacts"]
    if artifacts["code"]:
        with open("sudoku_game.py", "w", encoding="utf-8") as f:
            f.write(artifacts["code"])
        print("\n[저장됨] sudoku_game.py")

    if artifacts["tests"]:
        with open("test_sudoku_game.py", "w", encoding="utf-8") as f:
            f.write(artifacts["tests"])
        print("[저장됨] test_sudoku_game.py")

    if artifacts["review"]:
        with open("review_report.txt", "w", encoding="utf-8") as f:
            f.write(artifacts["review"])
        print("[저장됨] review_report.txt")


if __name__ == "__main__":
    main()
