import sys
from PySide2.QtWidgets import QApplication
from pmWidgets import pmUI


if __name__ == "__main__":
    app = QApplication(sys.argv)

    win = pmUI()

    sys.exit(app.exec_())
