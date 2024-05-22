import json

from PyQt5 import QtWidgets, uic


class Settings(QtWidgets.QMainWindow):
    def __init__(self):
        super(Settings, self).__init__()
        uic.loadUi('data/settings.ui', self)

        self.d = None
        self.load_info()

        self.show()

    def load_info(self):
        with open('data/settings.json') as f:
            self.d = json.loads(f.read())

        self.line_line.setText(self.d["points_for_line"])
        self.line_tetris.setText(self.d["points_for_tetris"])
        self.line_tick.setText(self.d["tick_time"])

    def can_save(self):
        return self.line_line.text().isnumeric() \
               and self.line_tetris.text().isnumeric() \
               and self.line_tick.text().isnumeric()

    def save(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("Информация")

        if not self.can_save():
            msg.setText("Не получилось сохранить настройки")
        else:
            self.d["points_for_line"] = int(self.line_line.text())
            self.d["points_for_tetris"] = int(self.line_tetris.text())
            self.d["tick_time"] = int(self.line_tick.text())

            msg.setText("Найстройки успешно сохранены")

            with open('data/settings.json', 'w') as f:
                f.write(json.dumps(self.d))

        msg.exec()
