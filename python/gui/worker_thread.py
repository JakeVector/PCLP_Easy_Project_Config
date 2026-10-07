from PySide6.QtCore import QObject, Signal, Slot

class Worker(QObject):
    finished = Signal()
    error = Signal(str)

    def __init__(self, task):
        super().__init__()
        self.task = task

    @Slot()
    def run(self):
        try:
            if callable(self.task):
                self.task()
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()