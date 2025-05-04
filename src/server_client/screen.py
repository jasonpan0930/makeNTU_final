import sys
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QScrollArea, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QFont

class CarPlateManager(QObject):
    delete_plate_signal = pyqtSignal(str)
    plates_changed = pyqtSignal()
    plate_deleted = pyqtSignal(str)
    plate_pending_delete = pyqtSignal(str)
    plate_cancel_delete = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.plates = []
        self.pending_deletes = {}  # plate -> QTimer
        self.delete_plate_signal.connect(self._handle_delete_plate)

    def get_allplate(self):
        return self.plates

    def add_plate(self, plate):
        if plate in self.pending_deletes:
            self.pending_deletes[plate].stop()
            del self.pending_deletes[plate]
            self.plate_cancel_delete.emit(plate)
            print(f"取消刪除: {plate}")

        if plate not in self.plates:
            self.plates.append(plate)
            self.plates_changed.emit()

    def delete_plate(self, plate, delay=3000):
        self.delete_plate_signal.emit(plate)
        '''if plate in self.pending_deletes:
            return  # 已經排隊刪除了

        timer = QTimer(self)
        timer.setSingleShot(True)

        def do_delete():
            if plate in self.plates:
                self.plates.remove(plate)
                self.plate_deleted.emit(plate)
                self.plates_changed.emit()
                print(f"已刪除: {plate}")
            self.pending_deletes.pop(plate, None)

        timer.timeout.connect(do_delete)
        timer.start(delay)
        self.pending_deletes[plate] = timer
        self.plate_pending_delete.emit(plate)
        print(f"排隊刪除: {plate}（3秒內可取消）")'''

    def _handle_delete_plate(self, plate):
        #at main so can use QTimer
        def do_delete():
            if plate in self.plates:
                self.plates.remove(plate)
                self.plate_deleted.emit(plate)
                self.plates_changed.emit()
                print(f"已刪除: {plate}")
            self.pending_deletes.pop(plate, None)

        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(do_delete)
        timer.start(3000)

        self.pending_deletes[plate] = timer
        self.plate_pending_delete.emit(plate)
        print(f"排隊刪除: {plate}（3秒內可取消）")

    def clear_plates(self):
        self.plates.clear()
        self.plates_changed.emit()

    def move_plate_to_top(self, plate):
        if plate in self.plates:
            self.plates.remove(plate)
            self.plates.insert(0, plate)
            self.plates_changed.emit()

# 主UI
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("車牌系統")
        self.setFixedSize(600, 400)
        self.setStyleSheet("background-color: #1a1a2e;")

        self.plate_manager = CarPlateManager()
        self.plate_labels = {}  # plate字串 -> QLabel
        self.calling_timers = {}   # plate -> QTimer

        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 左側
        self.main_display = RoundedFrame()
        self.main_display.setFixedSize(400, 380)
        self.main_display.setStyleSheet(frame_style())
        main_display_layout = QVBoxLayout(self.main_display)

        self.main_display_label = QLabel("主畫面顯示內容")
        self.main_display_label.setAlignment(Qt.AlignCenter)
        self.main_display_label.setStyleSheet("color: white; font-size: 32px;")
        main_display_layout.addWidget(self.main_display_label)

        # 右側
        right_side = QVBoxLayout()
        right_side.setSpacing(10)

        # 時間
        self.time_display = RoundedFrame()
        self.time_display.setFixedSize(170, 50)
        self.time_display.setStyleSheet(frame_style())
        time_layout = QVBoxLayout(self.time_display)
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("color: white; font-size: 24px;")
        time_layout.addWidget(self.time_label)

        # 車牌清單
        self.plate_display = RoundedFrame()
        self.plate_display.setFixedSize(170, 320)
        self.plate_display.setStyleSheet(frame_style())
        plate_layout = QVBoxLayout(self.plate_display)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("border: none;")
        plate_layout.addWidget(scroll)

        self.plate_container = QWidget()
        self.plate_container_layout = QVBoxLayout(self.plate_container)
        self.plate_container_layout.setContentsMargins(5, 5, 5, 5)
        self.plate_container_layout.setSpacing(5)
        self.plate_container_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(self.plate_container)

        # 排版
        main_layout.addWidget(self.main_display)
        main_layout.addLayout(right_side)
        right_side.addWidget(self.time_display)
        right_side.addWidget(self.plate_display)

        # 連接
        self.plate_manager.plates_changed.connect(self.refresh_plate_list)
        self.plate_manager.plate_pending_delete.connect(self.mark_plate_pending_delete)
        self.plate_manager.plate_cancel_delete.connect(self.restore_plate_style)
        self.plate_manager.plate_deleted.connect(self.remove_plate_label)

        # 啟動時間
        self.update_time()
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)

    def update_time(self):
        current_time = time.strftime("%H:%M:%S")
        self.time_label.setText(current_time)

    def is_plate_pending(self, plate):
        return plate in self.plate_manager.pending_deletes

    def refresh_plate_list(self):
        # 清空
        for i in reversed(range(self.plate_container_layout.count())):
            widget = self.plate_container_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        self.plate_labels.clear()

        for plate in self.plate_manager.plates:
            label = QLabel(plate)
            label.setFixedHeight(25)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            label.setAlignment(Qt.AlignCenter)

            # 正確設樣式
            if self.is_plate_pending(plate):
                label.setStyleSheet(pending_plate_style())
            elif plate in self.calling_timers:
                label.setStyleSheet(calling_plate_style())
            else:
                label.setStyleSheet(normal_plate_style())

            self.plate_container_layout.addWidget(label)
            self.plate_labels[plate] = label
    
    def plate_calling(self, plate, delay=10000):
        if plate not in self.plate_labels:
            print(f"找不到車牌 {plate}，忽略")
            return

        # 1. 拉到最上
        self.plate_manager.move_plate_to_top(plate)

        # 2. 換成綠色
        label = self.plate_labels.get(plate)
        if label:
            label.setStyleSheet(calling_plate_style())

        # 3. 重設倒數計時器
        if plate in self.calling_timers:
            self.calling_timers[plate].stop()
            del self.calling_timers[plate]

        timer = QTimer(self)
        timer.setSingleShot(True)

        def reset_color():
            label = self.plate_labels.get(plate)
            if label:
                label.setStyleSheet(normal_plate_style())
            self.calling_timers.pop(plate, None)

        timer.timeout.connect(reset_color)
        timer.start(delay)  # 10秒
        self.calling_timers[plate] = timer

    def mark_plate_pending_delete(self, plate):
        if plate in self.plate_labels:
            label = self.plate_labels[plate]
            label.setStyleSheet(pending_plate_style())

    def restore_plate_style(self, plate):
        if plate in self.plate_labels:
            label = self.plate_labels[plate]
            label.setStyleSheet(normal_plate_style())

    def remove_plate_label(self, plate):
        if plate in self.plate_labels:
            label = self.plate_labels.pop(plate)
            label.setParent(None)
    
    ###main screen
    def mainScreen_display(self, text: str):
        self.main_display_label.setText(text)

class RoundedFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)

def frame_style():
    return """
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #33475b, stop:1 #1a1f36);
    border-radius: 20px;
    """

def normal_plate_style():
    return """
        background-color: #3b5998;
        color: white;
        border-radius: 10px;
        font-size: 20px;
    """

def calling_plate_style():
    return """
        background-color: #3cb371;  /* 綠色 */
        color: white;
        border-radius: 10px;
        font-size: 20px;
    """

def pending_plate_style():
    return """
        background-color: #555555;
        color: #dddddd;
        border-radius: 10px;
        font-size: 20px;
    """

__all__ = ["MainWindow"]

# 啟動
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()

    window.show()

    # Demo
    window.plate_manager.add_plate("ABC-123")
    window.plate_manager.add_plate("XYZ-789")
    window.plate_manager.get_allplate()  ##return list of plate str

    def later_updates():
        window.plate_manager.delete_plate("ABC-123")
        window.plate_manager.add_plate("NEW-555")
        window.plate_manager.move_plate_to_top("XYZ-789")


    def cancel_delete():
        window.plate_manager.add_plate("ABC-123")

    QTimer.singleShot(3000, later_updates)  # 3秒後排程刪除
    #QTimer.singleShot(5000, cancel_delete)  # 5秒後補回（取消刪除)

    def calling():
        window.plate_calling("ABC-123")
    QTimer.singleShot(7000, calling)

    sys.exit(app.exec())
