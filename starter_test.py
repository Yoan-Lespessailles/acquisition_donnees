import sys

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from ui_test_pyside6 import Ui_MainWindow

class MyWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Qt Designer")
        self.resize(600, 400)
        
        self.setupUi(self)

        self.btnOk.clicked.connect(self.btnOkClicked)

    @Slot()
    def btnOkClicked(self):
        print(self.txtLogin.text(), self.txtpassword.text(), self.spnAge.value())

# Exécute le bloc uniquement si ce fichier est lancé directement, pas s’il est importé
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    sys.exit(app.exec())