# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_pyside.ui'
##
## Created by: Qt User Interface Compiler version 6.11.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 585)
        MainWindow.setStyleSheet(u"")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_3 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.widget_camera = QWidget(self.centralwidget)
        self.widget_camera.setObjectName(u"widget_camera")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_camera.sizePolicy().hasHeightForWidth())
        self.widget_camera.setSizePolicy(sizePolicy)
        self.widget_camera.setStyleSheet(u"/*background-color: black;\n"
"border-radius: 12px;*/")

        self.horizontalLayout_3.addWidget(self.widget_camera)

        self.area_sentence = QWidget(self.centralwidget)
        self.area_sentence.setObjectName(u"area_sentence")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.area_sentence.sizePolicy().hasHeightForWidth())
        self.area_sentence.setSizePolicy(sizePolicy1)
        self.verticalLayout = QVBoxLayout(self.area_sentence)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.area_settings = QWidget(self.area_sentence)
        self.area_settings.setObjectName(u"area_settings")
        self.verticalLayout_2 = QVBoxLayout(self.area_settings)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_select_micro = QLabel(self.area_settings)
        self.label_select_micro.setObjectName(u"label_select_micro")
        font = QFont()
        font.setFamilies([u"Roboto"])
        self.label_select_micro.setFont(font)

        self.verticalLayout_2.addWidget(self.label_select_micro)

        self.select_micro = QComboBox(self.area_settings)
        self.select_micro.setObjectName(u"select_micro")
        self.select_micro.setFont(font)

        self.verticalLayout_2.addWidget(self.select_micro)

        self.label_select_camera = QLabel(self.area_settings)
        self.label_select_camera.setObjectName(u"label_select_camera")
        self.label_select_camera.setFont(font)

        self.verticalLayout_2.addWidget(self.label_select_camera)

        self.select_camera = QComboBox(self.area_settings)
        self.select_camera.setObjectName(u"select_camera")
        self.select_camera.setFont(font)

        self.verticalLayout_2.addWidget(self.select_camera)


        self.verticalLayout.addWidget(self.area_settings)

        self.area_language = QWidget(self.area_sentence)
        self.area_language.setObjectName(u"area_language")
        self.horizontalLayout_2 = QHBoxLayout(self.area_language)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_select_language = QLabel(self.area_language)
        self.label_select_language.setObjectName(u"label_select_language")
        self.label_select_language.setFont(font)

        self.horizontalLayout_2.addWidget(self.label_select_language)

        self.select_language = QComboBox(self.area_language)
        self.select_language.setObjectName(u"select_language")

        self.horizontalLayout_2.addWidget(self.select_language)

        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 5)

        self.verticalLayout.addWidget(self.area_language)

        self.label_sentence = QLabel(self.area_sentence)
        self.label_sentence.setObjectName(u"label_sentence")
        sizePolicy.setHeightForWidth(self.label_sentence.sizePolicy().hasHeightForWidth())
        self.label_sentence.setSizePolicy(sizePolicy)
        font1 = QFont()
        font1.setFamilies([u"Roboto"])
        font1.setPointSize(20)
        font1.setBold(True)
        self.label_sentence.setFont(font1)
        self.label_sentence.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_sentence.setWordWrap(True)

        self.verticalLayout.addWidget(self.label_sentence)

        self.area_button = QWidget(self.area_sentence)
        self.area_button.setObjectName(u"area_button")
        self.horizontalLayout = QHBoxLayout(self.area_button)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.button_record = QPushButton(self.area_button)
        self.button_record.setObjectName(u"button_record")
        self.button_record.setEnabled(True)
        self.button_record.setFont(font)
        self.button_record.setStyleSheet(u"")

        self.horizontalLayout.addWidget(self.button_record)


        self.verticalLayout.addWidget(self.area_button)


        self.horizontalLayout_3.addWidget(self.area_sentence)

        self.horizontalLayout_3.setStretch(0, 3)
        self.horizontalLayout_3.setStretch(1, 2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 23))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
#if QT_CONFIG(shortcut)
        self.label_select_micro.setBuddy(self.select_micro)
        self.label_select_camera.setBuddy(self.select_camera)
        self.label_select_language.setBuddy(self.select_camera)
#endif // QT_CONFIG(shortcut)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label_select_micro.setText(QCoreApplication.translate("MainWindow", u"Micro :", None))
        self.label_select_camera.setText(QCoreApplication.translate("MainWindow", u"Camera :", None))
        self.label_select_language.setText(QCoreApplication.translate("MainWindow", u"Language :", None))
        self.label_sentence.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.button_record.setText(QCoreApplication.translate("MainWindow", u"Record", None))
    # retranslateUi

