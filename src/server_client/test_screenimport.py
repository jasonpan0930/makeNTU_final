from screen import MainWindow
from PySide6.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    window.plate_manager.add_plate("GHI-999")
    window.mainScreen_display("叫號中：GHI-999")  # ✅ 就可以這樣呼叫

    sys.exit(app.exec())