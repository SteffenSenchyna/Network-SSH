import sys
import time
from PyQt5.QtCore import QThread, pyqtSignal, QObject, pyqtSlot
from PyQt5.QtWidgets import QApplication, QPushButton, QWidget, QHBoxLayout, QProgressBar, QVBoxLayout


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Widget")
        self.h_box = QHBoxLayout(self)
        self.main_window_button = QPushButton("Start")
        self.popup = PopUpProgressB()
        self.main_window_button.clicked.connect(self.popup.show)
        self.h_box.addWidget(self.main_window_button)
        self.setLayout(self.h_box)
        self.show()


class Worker(QObject):
    finished = pyqtSignal()
    intReady = pyqtSignal(int)

    @pyqtSlot()
    def proc_counter(self):  # A slot takes no params
        for i in range(1, 100):
            time.sleep(1)
            self.intReady.emit(i)

        self.finished.emit()


class PopUpProgressB(QWidget):

    def __init__(self):
        super().__init__()
        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(30, 40, 500, 75)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.pbar)
        self.setLayout(self.layout)
        self.setGeometry(300, 300, 550, 100)
        self.setWindowTitle('Progress Bar')
        self.obj = Worker()
        self.thread = QThread()
        self.obj.intReady.connect(self.on_count_changed)
        self.obj.moveToThread(self.thread)
        self.obj.finished.connect(self.thread.quit)
        self.thread.started.connect(self.obj.proc_counter)
        self.thread.start()

    def on_count_changed(self, value):
        self.pbar.setValue(value)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())