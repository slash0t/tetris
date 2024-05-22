import json

from PyQt5 import QtWidgets, uic, QtGui, QtCore

from qasync import asyncSlot

from game.block_geometry import BlockGeometry
from game.tetris import Tetris
from timer import Timer
from ui.settings import Settings


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('data/tetris.ui', self)
        self.setFixedSize(222, 550)
        self.setup_tables()

        self.tetris = None
        self.updateTimer = Timer(1 / 40, self.redraw)

        self.info.triggered.connect(self.show_info)
        self.new_game.triggered.connect(self.set_new_game)
        self.settings.triggered.connect(self.launch_settings_window)

        self.started_fps = False

        self.settings = None

        self.show()

    @staticmethod
    @asyncSlot()
    def show_info():
        msg = QtWidgets.QMessageBox()
        msg.setText("Данная игра сделана Едрышовым Артемом")
        msg.setWindowTitle("Информация")
        msg.exec()

    @staticmethod
    def read_settings():
        d = {}

        with open('data/settings.json') as f:
            dd = json.loads(f.read())

        d["difficulty_levels"] = dd["difficulty_levels"]
        d["tick_time"] = dd["tick_time"]

        colors = []
        for arr in dd["colors"]:
            curr = [tuple(color) for color in arr]
            colors.append(curr)
        d["colors"] = colors

        geometry = []
        for geom in dd["geometry"]:
            curr = BlockGeometry([tuple(coord) for coord in geom])
            geometry.append(curr)

        d["geometry"] = geometry

        return d

    def launch_settings_window(self):
        if self.settings is not None:
            self.settings.close()

        self.settings = Settings()
        self.settings.show()

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

        for i in range(4):
            for j in range(4):
                self.table_preview.item(i, j).setBackground(QtGui.QColor(255, 255, 255))

        block = self.tetris.get_next_block()
        for pos in block.geometry.coords:
            y, x = pos
            x += 2 - block.geometry.size // 2
            y += 2 - block.geometry.size // 2
            self.table_preview.item(x, y).setBackground(QtGui.QColor(*block.color))

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
