"""PyQt6 Sudoku Game — standalone, no API key required."""

import sys
import random
import copy
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor


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
    NORMAL_STYLE = "background: white; color: #222; border: 1px solid #bbb;"
    FIXED_STYLE  = "background: #f0f0f0; color: #333; border: 1px solid #bbb; font-weight: bold;"
    ERROR_STYLE  = "background: #ffe0e0; color: red; border: 1px solid red;"
    HINT_STYLE   = "background: #fff3cd; color: #856404; border: 1px solid #ffc107;"

    def __init__(self, row: int, col: int):
        super().__init__()
        self.row = row
        self.col = col
        self.fixed = False
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMaxLength(1)
        self.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.setFixedSize(52, 52)
        self._set_border_style()
        self.setStyleSheet(self.NORMAL_STYLE + self._border_css())

    def _border_css(self) -> str:
        t = "2px" if self.row % 3 == 0 else "1px"
        b = "2px" if self.row == 8 else "1px"
        l = "2px" if self.col % 3 == 0 else "1px"
        r = "2px" if self.col == 8 else "1px"
        return f"border-top:{t} solid #555; border-bottom:{b} solid #555; border-left:{l} solid #555; border-right:{r} solid #555;"

    def _set_border_style(self):
        self._border = self._border_css()

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


# ── Main window ───────────────────────────────────────────────────────────────

class SudokuWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("스도쿠")
        self.puzzle: list[list[int]] = []
        self.solution: list[list[int]] = []
        self.cells: list[list[SudokuCell]] = []
        self._build_ui()
        self.new_game()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(12)
        root.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("스도쿠")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        root.addWidget(title)

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
            ("새 게임", self.new_game),
            ("힌트",   self.show_hint),
            ("검증",   self.validate),
            ("정답",   self.reveal_solution),
        ]:
            btn = QPushButton(label)
            btn.setFixedHeight(38)
            btn.setFont(QFont("Arial", 12))
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)
        root.addLayout(btn_row)

        # Status
        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setFont(QFont("Arial", 11))
        root.addWidget(self.status)

        self.setFixedSize(self.sizeHint())

    def new_game(self):
        self.puzzle, self.solution = generate_puzzle(clues=35)
        for r in range(9):
            for c in range(9):
                cell = self.cells[r][c]
                if self.puzzle[r][c]:
                    cell.set_fixed(self.puzzle[r][c])
                else:
                    cell.set_empty()
        self.status.setText("")

    def _on_input(self, row: int, col: int):
        """입력 시 해당 셀만 실시간 유효성 표시."""
        cell = self.cells[row][col]
        cell.mark_normal()
        v = cell.value()
        if v and not _is_valid(self._current_board(skip=(row, col)), row, col, v):
            cell.mark_error()

    def _current_board(self, skip: tuple | None = None) -> list[list[int]]:
        board = [[0] * 9 for _ in range(9)]
        for r in range(9):
            for c in range(9):
                if skip and (r, c) == skip:
                    continue
                board[r][c] = self.cells[r][c].value()
        return board

    def validate(self):
        """전체 보드 검증 — 틀린 칸 강조."""
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
            self.status.setText("🎉 완성! 축하합니다!")
        elif errors:
            self.status.setText(f"오류 {errors}개를 찾았습니다.")
        else:
            self.status.setText("아직 빈 칸이 있습니다.")

    def _candidates(self, board: list[list[int]], row: int, col: int) -> list[int]:
        """해당 칸에 올 수 있는 후보 숫자 목록 반환."""
        used = set(board[row])
        used |= {board[r][col] for r in range(9)}
        br, bc = (row // 3) * 3, (col // 3) * 3
        used |= {board[r][c] for r in range(br, br + 3) for c in range(bc, bc + 3)}
        return [n for n in range(1, 10) if n not in used]

    def show_hint(self):
        """후보 숫자가 가장 적은 칸(제일 쉬운 칸)에 힌트 표시."""
        board = self._current_board()
        best_cell = None
        best_count = 10

        for r in range(9):
            for c in range(9):
                cell = self.cells[r][c]
                if cell.fixed or cell.value() == self.solution[r][c]:
                    continue
                # 틀린 값이 입력된 칸은 일단 비워서 후보 계산
                original = board[r][c]
                board[r][c] = 0
                count = len(self._candidates(board, r, c))
                board[r][c] = original
                if count < best_count:
                    best_count = count
                    best_cell = (r, c)

        if best_cell is None:
            self.status.setText("모든 칸이 올바릅니다!")
            return

        r, c = best_cell
        self.cells[r][c].setText(str(self.solution[r][c]))
        self.cells[r][c].mark_hint()
        self.status.setText(f"힌트: ({r+1}, {c+1}) 칸 — 후보 {best_count}개 중 정답")

    def reveal_solution(self):
        """정답 전체 공개."""
        for r in range(9):
            for c in range(9):
                cell = self.cells[r][c]
                if not cell.fixed:
                    cell.setText(str(self.solution[r][c]))
                    cell.mark_normal()
        self.status.setText("정답을 공개했습니다.")

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
