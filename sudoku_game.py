"""PyQt6 Sudoku Game — standalone, no API key required."""

import sys
import json
import random
import copy
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QDialog, QTableWidget, QTableWidgetItem, QHeaderView,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

RECORDS_FILE = Path.home() / ".sudoku_records.json"

DIFFICULTY = {
    "쉬움":  45,
    "보통":  35,
    "어려움": 25,
}


# ── Record storage ────────────────────────────────────────────────────────────

def load_records() -> dict[str, list[dict]]:
    if RECORDS_FILE.exists():
        try:
            data = json.loads(RECORDS_FILE.read_text(encoding="utf-8"))
            # 이전 포맷(list) 호환
            if isinstance(data, list):
                return {"보통": data}
            return data
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_record(elapsed_seconds: int, difficulty: str) -> list[dict]:
    all_records = load_records()
    records = all_records.get(difficulty, [])
    records.append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "time": elapsed_seconds,
    })
    records.sort(key=lambda r: r["time"])
    all_records[difficulty] = records
    RECORDS_FILE.write_text(json.dumps(all_records, ensure_ascii=False, indent=2), encoding="utf-8")
    return records


def fmt_time(seconds: int) -> str:
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


# ── Sudoku logic ──────────────────────────────────────────────────────────────

def _is_valid(board: list[list[int]], row: int, col: int, num: int) -> bool:
    if num in board[row]:
        return False
    if num in [board[r][col] for r in range(9)]:
        return False
    br, bc = (row // 3) * 3, (col // 3) * 3
    for r in range(br, br + 3):
        for c in range(bc, bc + 3):
            if board[r][c] == num:
                return False
    return True


def _solve(board: list[list[int]]) -> bool:
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                nums = list(range(1, 10))
                random.shuffle(nums)
                for num in nums:
                    if _is_valid(board, row, col, num):
                        board[row][col] = num
                        if _solve(board):
                            return True
                        board[row][col] = 0
                return False
    return True


def generate_puzzle(clues: int = 35) -> tuple[list[list[int]], list[list[int]]]:
    """완성된 보드를 생성한 뒤 일부 칸을 비워 퍼즐을 반환."""
    solution = [[0] * 9 for _ in range(9)]
    _solve(solution)
    puzzle = copy.deepcopy(solution)
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)
    for r, c in cells[:81 - clues]:
        puzzle[r][c] = 0
    return puzzle, solution


# ── Cell widget ───────────────────────────────────────────────────────────────

class SudokuCell(QLineEdit):
    NORMAL_STYLE = "background: white; color: #222;"
    FIXED_STYLE  = "background: #f0f0f0; color: #333; font-weight: bold;"
    ERROR_STYLE  = "background: #ffe0e0; color: red;"
    HINT_STYLE   = "background: #fff3cd; color: #856404;"

    def __init__(self, row: int, col: int):
        super().__init__()
        self.row = row
        self.col = col
        self.fixed = False
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMaxLength(1)
        self.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.setFixedSize(52, 52)
        self._border = self._border_css()
        self.setStyleSheet(self.NORMAL_STYLE + self._border)

    def _border_css(self) -> str:
        t = "2px" if self.row % 3 == 0 else "1px"
        b = "2px" if self.row == 8 else "1px"
        l = "2px" if self.col % 3 == 0 else "1px"
        r = "2px" if self.col == 8 else "1px"
        return (
            f"border-top:{t} solid #555; border-bottom:{b} solid #555;"
            f"border-left:{l} solid #555; border-right:{r} solid #555;"
        )

    def set_fixed(self, value: int):
        self.fixed = True
        self.setText(str(value))
        self.setReadOnly(True)
        self.setStyleSheet(self.FIXED_STYLE + self._border)

    def set_empty(self):
        self.fixed = False
        self.setText("")
        self.setReadOnly(False)
        self.setStyleSheet(self.NORMAL_STYLE + self._border)

    def mark_error(self):
        if not self.fixed:
            self.setStyleSheet(self.ERROR_STYLE + self._border)

    def mark_hint(self):
        if not self.fixed:
            self.setStyleSheet(self.HINT_STYLE + self._border)

    def mark_normal(self):
        if not self.fixed:
            self.setStyleSheet(self.NORMAL_STYLE + self._border)

    def value(self) -> int:
        try:
            v = int(self.text())
            return v if 1 <= v <= 9 else 0
        except ValueError:
            return 0


# ── Records dialog ────────────────────────────────────────────────────────────

class RecordsDialog(QDialog):
    def __init__(self, all_records: dict[str, list[dict]], current_diff: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("기록")
        self.setMinimumWidth(360)
        layout = QVBoxLayout(self)

        # 난이도별 탭 버튼
        diff_row = QHBoxLayout()
        self._tables: dict[str, QWidget] = {}
        self._diff_btns: dict[str, QPushButton] = {}

        from PyQt6.QtWidgets import QStackedWidget
        self._stack = QStackedWidget()

        for diff in DIFFICULTY:
            btn = QPushButton(diff)
            btn.setCheckable(True)
            btn.setFixedHeight(32)
            btn.clicked.connect(lambda _, d=diff: self._switch(d))
            diff_row.addWidget(btn)
            self._diff_btns[diff] = btn

            records = all_records.get(diff, [])
            page = QWidget()
            page_layout = QVBoxLayout(page)
            page_layout.setContentsMargins(0, 0, 0, 0)
            if not records:
                page_layout.addWidget(QLabel("기록이 없습니다."))
            else:
                table = QTableWidget(len(records), 3)
                table.setHorizontalHeaderLabels(["순위", "시간", "날짜"])
                table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
                table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
                for i, rec in enumerate(records):
                    table.setItem(i, 0, QTableWidgetItem(f"{i + 1}위"))
                    table.setItem(i, 1, QTableWidgetItem(fmt_time(rec["time"])))
                    table.setItem(i, 2, QTableWidgetItem(rec["date"]))
                page_layout.addWidget(table)
            self._stack.addWidget(page)

        layout.addLayout(diff_row)
        layout.addWidget(self._stack)

        close_btn = QPushButton("닫기")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self._switch(current_diff)

    def _switch(self, diff: str):
        idx = list(DIFFICULTY.keys()).index(diff)
        self._stack.setCurrentIndex(idx)
        for d, btn in self._diff_btns.items():
            btn.setChecked(d == diff)


# ── Main window ───────────────────────────────────────────────────────────────

class SudokuWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("스도쿠")
        self.puzzle: list[list[int]] = []
        self.solution: list[list[int]] = []
        self.cells: list[list[SudokuCell]] = []
        self._elapsed = 0
        self._finished = False
        self._difficulty = "보통"
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._build_ui()
        self.new_game()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(10)
        root.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("스도쿠")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        root.addWidget(title)

        # Difficulty selector
        diff_row = QHBoxLayout()
        self._diff_btns: dict[str, QPushButton] = {}
        for diff in DIFFICULTY:
            btn = QPushButton(diff)
            btn.setCheckable(True)
            btn.setFixedHeight(30)
            btn.setFont(QFont("Arial", 10))
            btn.clicked.connect(lambda _, d=diff: self._set_difficulty(d))
            diff_row.addWidget(btn)
            self._diff_btns[diff] = btn
        root.addLayout(diff_row)

        # Timer
        self.timer_label = QLabel("00:00")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setFont(QFont("Consolas", 18, QFont.Weight.Bold))
        self.timer_label.setStyleSheet("color: #333;")
        root.addWidget(self.timer_label)

        # Grid
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(0)
        self.cells = []
        for r in range(9):
            row_cells = []
            for c in range(9):
                cell = SudokuCell(r, c)
                cell.textChanged.connect(lambda _, rr=r, cc=c: self._on_input(rr, cc))
                grid.addWidget(cell, r, c)
                row_cells.append(cell)
            self.cells.append(row_cells)
        root.addWidget(grid_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        # Buttons
        btn_row = QHBoxLayout()
        for label, slot in [
            ("새 게임",  self.new_game),
            ("힌트",    self.show_hint),
            ("검증",    self.validate),
            ("정답",    self.reveal_solution),
            ("기록",    self.show_records),
        ]:
            btn = QPushButton(label)
            btn.setFixedHeight(38)
            btn.setFont(QFont("Arial", 11))
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)
        root.addLayout(btn_row)

        # Status
        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setFont(QFont("Arial", 11))
        root.addWidget(self.status)

        self.setFixedSize(self.sizeHint())

    # ── Timer ─────────────────────────────────────────────────────────────────

    def _tick(self):
        self._elapsed += 1
        self.timer_label.setText(fmt_time(self._elapsed))

    def _start_timer(self):
        self._elapsed = 0
        self._finished = False
        self.timer_label.setText("00:00")
        self.timer_label.setStyleSheet("color: #333;")
        self._timer.start(1000)

    def _stop_timer(self):
        self._timer.stop()

    # ── Game ──────────────────────────────────────────────────────────────────

    def _set_difficulty(self, diff: str):
        self._difficulty = diff
        self.new_game()

    def _update_diff_buttons(self):
        for diff, btn in self._diff_btns.items():
            btn.setChecked(diff == self._difficulty)
            btn.setStyleSheet(
                "background:#4a90d9; color:white; border-radius:4px;"
                if diff == self._difficulty else ""
            )

    def new_game(self):
        self._update_diff_buttons()
        clues = DIFFICULTY[self._difficulty]
        self.puzzle, self.solution = generate_puzzle(clues=clues)
        for r in range(9):
            for c in range(9):
                cell = self.cells[r][c]
                if self.puzzle[r][c]:
                    cell.set_fixed(self.puzzle[r][c])
                else:
                    cell.set_empty()
        self.status.setText("")
        self._start_timer()

    def _on_input(self, row: int, col: int):
        if self._finished:
            return
        cell = self.cells[row][col]
        cell.mark_normal()
        v = cell.value()
        if v and not _is_valid(self._current_board(skip=(row, col)), row, col, v):
            cell.mark_error()
        if self._is_complete():
            self._complete()

    def _complete(self):
        self._finished = True
        self._stop_timer()
        self.timer_label.setStyleSheet("color: #2a7a2a;")
        records = save_record(self._elapsed, self._difficulty)
        rank = next(i + 1 for i, r in enumerate(records) if r["time"] == self._elapsed)
        best = fmt_time(records[0]["time"])
        self.status.setText(
            f"🎉 완성! {fmt_time(self._elapsed)} — {rank}위  |  최고기록: {best}"
        )

    def _current_board(self, skip: tuple | None = None) -> list[list[int]]:
        board = [[0] * 9 for _ in range(9)]
        for r in range(9):
            for c in range(9):
                if skip and (r, c) == skip:
                    continue
                board[r][c] = self.cells[r][c].value()
        return board

    def validate(self):
        errors = 0
        for r in range(9):
            for c in range(9):
                cell = self.cells[r][c]
                if cell.fixed:
                    continue
                v = cell.value()
                if v == 0:
                    cell.mark_normal()
                elif v != self.solution[r][c]:
                    cell.mark_error()
                    errors += 1
                else:
                    cell.mark_normal()
        if errors == 0 and self._is_complete():
            self._complete()
        elif errors:
            self.status.setText(f"오류 {errors}개를 찾았습니다.")
        else:
            self.status.setText("아직 빈 칸이 있습니다.")

    def _candidates(self, board: list[list[int]], row: int, col: int) -> list[int]:
        used = set(board[row])
        used |= {board[r][col] for r in range(9)}
        br, bc = (row // 3) * 3, (col // 3) * 3
        used |= {board[r][c] for r in range(br, br + 3) for c in range(bc, bc + 3)}
        return [n for n in range(1, 10) if n not in used]

    def show_hint(self):
        board = self._current_board()
        best_cell, best_count = None, 10
        for r in range(9):
            for c in range(9):
                cell = self.cells[r][c]
                if cell.fixed or cell.value() == self.solution[r][c]:
                    continue
                original = board[r][c]
                board[r][c] = 0
                count = len(self._candidates(board, r, c))
                board[r][c] = original
                if count < best_count:
                    best_count, best_cell = count, (r, c)
        if best_cell is None:
            self.status.setText("모든 칸이 올바릅니다!")
            return
        r, c = best_cell
        self.cells[r][c].setText(str(self.solution[r][c]))
        self.cells[r][c].mark_hint()
        self.status.setText(f"힌트: ({r+1}, {c+1}) 칸 — 후보 {best_count}개 중 정답")

    def reveal_solution(self):
        self._stop_timer()
        self._finished = True
        for r in range(9):
            for c in range(9):
                cell = self.cells[r][c]
                if not cell.fixed:
                    cell.setText(str(self.solution[r][c]))
                    cell.mark_normal()
        self.status.setText("정답을 공개했습니다.")

    def show_records(self):
        all_records = load_records()
        dlg = RecordsDialog(all_records, self._difficulty, self)
        dlg.exec()

    def _is_complete(self) -> bool:
        for r in range(9):
            for c in range(9):
                if self.cells[r][c].value() != self.solution[r][c]:
                    return False
        return True


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    window = SudokuWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
