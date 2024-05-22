import asyncio
import sys

from PyQt5 import QtWidgets
from qasync import QEventLoop

from ui.mainwindow import MainWindow

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    event_loop = QEventLoop(app)
    asyncio.set_event_loop(event_loop)

    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)

    main_window = MainWindow()
    main_window.show()

    with event_loop:
        event_loop.run_until_complete(app_close_event.wait())
