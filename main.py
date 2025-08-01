from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QFileDialog, QFrame
)
from PyQt5.QtGui import QPainter, QFont, QPalette, QColor
from PyQt5.QtCore import Qt, QRect
import sys

GRID_SIZE = 60
CELL_SIZE = 13
DEFAULT_CHAR = ' '
ASCII_CHARS = ['#', '*', '@', '+', '-', '=', 'o', 'x', '%', '&', '~', '/', '\\', '0']

class DrawGrid(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid = [[DEFAULT_CHAR for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.selected_char = ASCII_CHARS[0]
        self.setFixedSize(GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE)
        self.setMouseTracking(True)
        self.drawing = False
        self.erasing = False
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, Qt.white)
        self.setPalette(palette)
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.setLineWidth(2)

    def set_selected_char(self, char):
        self.selected_char = char

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self._draw_char(event.x(), event.y(), self.selected_char)
        elif event.button() == Qt.RightButton:
            self.erasing = True
            self._draw_char(event.x(), event.y(), DEFAULT_CHAR)

    def mouseReleaseEvent(self, event):
        self.drawing = False
        self.erasing = False

    def mouseMoveEvent(self, event):
        if self.drawing:
            self._draw_char(event.x(), event.y(), self.selected_char)
        elif self.erasing:
            self._draw_char(event.x(), event.y(), DEFAULT_CHAR)

    def _draw_char(self, x_pixel, y_pixel, char):
        x = x_pixel // CELL_SIZE
        y = y_pixel // CELL_SIZE
        if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
            self.grid[y][x] = char
            # Update only the cell's rectangle for repaint
            cell_rect = QRect(
                x * CELL_SIZE,
                y * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )
            self.update(cell_rect)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(QFont("Courier", CELL_SIZE - 2))
        painter.setPen(Qt.black)
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                char = self.grid[y][x]
                if char != DEFAULT_CHAR:
                    # Draw character in cell
                    painter.drawText(
                        x * CELL_SIZE,
                        y * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE,
                        Qt.AlignCenter,
                        char
                    )
        # Draw grid lines for better visibility
        painter.setPen(QColor(220, 220, 220))
        for x in range(GRID_SIZE + 1):
            painter.drawLine(x * CELL_SIZE, 0, x * CELL_SIZE, GRID_SIZE * CELL_SIZE)
        for y in range(GRID_SIZE + 1):
            painter.drawLine(0, y * CELL_SIZE, GRID_SIZE * CELL_SIZE, y * CELL_SIZE)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ASCII Drawing Board")

        # Character selection
        char_layout = QHBoxLayout()
        char_layout.addWidget(QLabel("Choose character:"))
        self.char_buttons = []
        for char in ASCII_CHARS:
            btn = QPushButton(char)
            btn.setFixedWidth(24)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, c=char: self.select_char(c))
            char_layout.addWidget(btn)
            self.char_buttons.append(btn)
        self.char_buttons[0].setChecked(True)

        # Canvas (centered with margins)
        self.grid_widget = DrawGrid(self)
        canvas_frame = QFrame()
        canvas_layout = QVBoxLayout()
        canvas_layout.setContentsMargins(20, 20, 20, 20)
        canvas_layout.addWidget(self.grid_widget)
        canvas_frame.setLayout(canvas_layout)
        canvas_frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        canvas_frame.setLineWidth(2)
        canvas_frame.setStyleSheet("background: #eee;")

        # Save button
        save_btn = QPushButton("Save (Ctrl+S)")
        save_btn.clicked.connect(self.save)
        save_btn.setShortcut("Ctrl+S")

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.addLayout(char_layout)
        main_layout.addWidget(canvas_frame)
        main_layout.addWidget(save_btn)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.selected_char = ASCII_CHARS[0]
        self.grid_widget.set_selected_char(self.selected_char)

    def select_char(self, char):
        self.selected_char = char
        self.grid_widget.set_selected_char(char)
        # Uncheck all buttons except the selected one
        for btn in self.char_buttons:
            btn.setChecked(btn.text() == char)

    def save(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save ASCII Art", "ascii_art.txt", "Text Files (*.txt)")
        if filename:
            with open(filename, "w") as f:
                for row in self.grid_widget.grid:
                    f.write(''.join(row) + '\n')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())