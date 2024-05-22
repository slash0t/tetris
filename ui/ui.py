from PyQt5 import QtWidgets, uic, QtGui, QtCore

from qasync import asyncSlot

from game.block_geometry import BlockGeometry
from game.tetris import Tetris
from timer import Timer


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('data/tetris.ui', self)
        self.setFixedSize(222, 550)
        self.setup_tables()

        self.tetris = None
        self.updateTimer = Timer(1 / 40, self.redraw)

        self.info.triggered.connect(self.show_info)
        self.new_game.triggered.connect(self.set_new_game)

        self.started_fps = False

        self.show()

    @staticmethod
    @asyncSlot()
    def show_info():
        msg = QtWidgets.QMessageBox()
        msg.setText("Данная игра сделана Едрышовым Артемом")
        msg.setWindowTitle("Информация")
        msg.exec()

    def read_settings(self):
        d = {
            "geometry": [BlockGeometry([(0, 0), (1, 0), (0, 1), (1, 1)])],
            "colors": [[(0, 0, 0)]],
            "difficulty_levels": 1,
            "tick_time": 150,
        }

        return d

    @asyncSlot()
    async def start_fps(self):
        await self.updateTimer.start()

    @asyncSlot()
    async def set_new_game(self):
        if not self.started_fps:
            self.started_fps = True
            await self.start_fps()

        self.tetris = Tetris(**self.read_settings())

        await self.tetris.start()

    def rotate(self, right):
        if self.tetris is None:
            return
        if self.tetris.get_state() != Tetris.GameState.ONGOING:
            return

        self.tetris.rotate_curr_block(right)

    def move(self, right):
        if self.tetris is None:
            return
        if self.tetris.get_state() != Tetris.GameState.ONGOING:
            return

        self.tetris.move_block(right)

    @asyncSlot()
    async def redraw(self):
        if self.tetris is None:
            return

        if self.tetris.get_state() == Tetris.GameState.LOST:
            self.score_label.setText(f"Game over\n{self.tetris.get_score()}")
            return

        self.score_label.setText(f"Score:\n{self.tetris.get_score()}")

        for i in range(20):
            for j in range(10):
                color = (255, 255, 255)
                if self.tetris.filled[i][j]:
                    color = self.tetris.colors[i][j]
                self.table_tetris.item(i, j).setBackground(QtGui.QColor(*color))

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Up:
            self.rotate(False)
        elif event.key() == QtCore.Qt.Key.Key_Right:
            self.move(True)
        elif event.key() == QtCore.Qt.Key.Key_Left:
            self.move(False)

    def setup_tables(self):
        for i in range(20):
            self.table_tetris.setRowHeight(i, 20)

            for j in range(10):
                self.table_tetris.setItem(i, j, QtWidgets.QTableWidgetItem())
        for i in range(4):
            self.table_preview.setRowHeight(i, 20)

            for j in range(4):
                self.table_preview.setItem(i, j, QtWidgets.QTableWidgetItem())

        for i in range(10):
            self.table_tetris.setColumnWidth(i, 20)
        for i in range(4):
            self.table_preview.setColumnWidth(i, 20)
