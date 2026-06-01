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
    QMainWindow, QMenuBar, QProgressBar, QPushButton,
    QSizePolicy, QSpacerItem, QStatusBar, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(820, 595)
        MainWindow.setStyleSheet(u"")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_3 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.area_video = QWidget(self.centralwidget)
        self.area_video.setObjectName(u"area_video")
        self.verticalLayout_3 = QVBoxLayout(self.area_video)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.area_record = QWidget(self.area_video)
        self.area_record.setObjectName(u"area_record")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.area_record.sizePolicy().hasHeightForWidth())
        self.area_record.setSizePolicy(sizePolicy)
        self.area_record.setStyleSheet(u"background-color: black;")
        self.horizontalLayout_4 = QHBoxLayout(self.area_record)
        self.horizontalLayout_4.setSpacing(6)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(9, 0, 9, 0)
        self.label_record_timer = QLabel(self.area_record)
        self.label_record_timer.setObjectName(u"label_record_timer")
        font = QFont()
        font.setFamilies([u"Roboto"])
        font.setBold(True)
        self.label_record_timer.setFont(font)
        self.label_record_timer.setStyleSheet(u"color: white;\n"
"border-radius: 6px;\n"
"padding: 4px 8px;")

        self.horizontalLayout_4.addWidget(self.label_record_timer)

        self.horizontalSpacer = QSpacerItem(411, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.label_record_dot = QLabel(self.area_record)
        self.label_record_dot.setObjectName(u"label_record_dot")
        self.label_record_dot.setMinimumSize(QSize(20, 20))
        self.label_record_dot.setMaximumSize(QSize(20, 20))
        self.label_record_dot.setStyleSheet(u"background-color: red;\n"
"border-radius: 10px;")

        self.horizontalLayout_4.addWidget(self.label_record_dot)


        self.verticalLayout_3.addWidget(self.area_record)

        self.area_preview = QWidget(self.area_video)
        self.area_preview.setObjectName(u"area_preview")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.area_preview.sizePolicy().hasHeightForWidth())
        self.area_preview.setSizePolicy(sizePolicy1)

        self.verticalLayout_3.addWidget(self.area_preview)


        self.horizontalLayout_3.addWidget(self.area_video)

        self.area_menu = QWidget(self.centralwidget)
        self.area_menu.setObjectName(u"area_menu")
        sizePolicy.setHeightForWidth(self.area_menu.sizePolicy().hasHeightForWidth())
        self.area_menu.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(self.area_menu)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.area_micro = QWidget(self.area_menu)
        self.area_micro.setObjectName(u"area_micro")
        self.verticalLayout_7 = QVBoxLayout(self.area_micro)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.area_micro_selection = QWidget(self.area_micro)
        self.area_micro_selection.setObjectName(u"area_micro_selection")
        self.verticalLayout_2 = QVBoxLayout(self.area_micro_selection)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_micro = QLabel(self.area_micro_selection)
        self.label_micro.setObjectName(u"label_micro")
        font1 = QFont()
        font1.setFamilies([u"Roboto"])
        self.label_micro.setFont(font1)

        self.verticalLayout_2.addWidget(self.label_micro)

        self.select_micro = QComboBox(self.area_micro_selection)
        self.select_micro.setObjectName(u"select_micro")
        sizePolicy.setHeightForWidth(self.select_micro.sizePolicy().hasHeightForWidth())
        self.select_micro.setSizePolicy(sizePolicy)
        self.select_micro.setFont(font1)
        self.select_micro.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_2.addWidget(self.select_micro)


        self.verticalLayout_7.addWidget(self.area_micro_selection)

        self.area_micro_test = QWidget(self.area_micro)
        self.area_micro_test.setObjectName(u"area_micro_test")
        self.verticalLayout_6 = QVBoxLayout(self.area_micro_test)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.button_test_micro = QPushButton(self.area_micro_test)
        self.button_test_micro.setObjectName(u"button_test_micro")
        sizePolicy.setHeightForWidth(self.button_test_micro.sizePolicy().hasHeightForWidth())
        self.button_test_micro.setSizePolicy(sizePolicy)
        self.button_test_micro.setFont(font1)
        self.button_test_micro.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_test_micro.setTabletTracking(False)
        self.button_test_micro.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        self.verticalLayout_6.addWidget(self.button_test_micro)

        self.label_micro_state = QLabel(self.area_micro_test)
        self.label_micro_state.setObjectName(u"label_micro_state")
        self.label_micro_state.setFont(font1)

        self.verticalLayout_6.addWidget(self.label_micro_state)

        self.progressbar_micro_level = QProgressBar(self.area_micro_test)
        self.progressbar_micro_level.setObjectName(u"progressbar_micro_level")
        sizePolicy.setHeightForWidth(self.progressbar_micro_level.sizePolicy().hasHeightForWidth())
        self.progressbar_micro_level.setSizePolicy(sizePolicy)
        self.progressbar_micro_level.setFont(font1)
        self.progressbar_micro_level.setValue(0)
        self.progressbar_micro_level.setTextVisible(False)

        self.verticalLayout_6.addWidget(self.progressbar_micro_level)


        self.verticalLayout_7.addWidget(self.area_micro_test)


        self.verticalLayout.addWidget(self.area_micro)

        self.widget = QWidget(self.area_menu)
        self.widget.setObjectName(u"widget")
        self.verticalLayout_5 = QVBoxLayout(self.widget)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.label_select_camera = QLabel(self.widget)
        self.label_select_camera.setObjectName(u"label_select_camera")
        self.label_select_camera.setFont(font1)

        self.verticalLayout_5.addWidget(self.label_select_camera)

        self.select_camera = QComboBox(self.widget)
        self.select_camera.setObjectName(u"select_camera")
        sizePolicy.setHeightForWidth(self.select_camera.sizePolicy().hasHeightForWidth())
        self.select_camera.setSizePolicy(sizePolicy)
        self.select_camera.setFont(font1)
        self.select_camera.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_5.addWidget(self.select_camera)


        self.verticalLayout.addWidget(self.widget)

        self.area_language = QWidget(self.area_menu)
        self.area_language.setObjectName(u"area_language")
        self.verticalLayout_8 = QVBoxLayout(self.area_language)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.label_select_language = QLabel(self.area_language)
        self.label_select_language.setObjectName(u"label_select_language")
        self.label_select_language.setFont(font1)

        self.verticalLayout_8.addWidget(self.label_select_language)

        self.select_language = QComboBox(self.area_language)
        self.select_language.setObjectName(u"select_language")
        sizePolicy.setHeightForWidth(self.select_language.sizePolicy().hasHeightForWidth())
        self.select_language.setSizePolicy(sizePolicy)
        self.select_language.setFont(font1)
        self.select_language.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_8.addWidget(self.select_language)


        self.verticalLayout.addWidget(self.area_language)

        self.area_sentence = QWidget(self.area_menu)
        self.area_sentence.setObjectName(u"area_sentence")
        font2 = QFont()
        font2.setFamilies([u"Ubuntu"])
        self.area_sentence.setFont(font2)
        self.verticalLayout_4 = QVBoxLayout(self.area_sentence)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_cpt_sentence = QLabel(self.area_sentence)
        self.label_cpt_sentence.setObjectName(u"label_cpt_sentence")
        self.label_cpt_sentence.setFont(font1)
        self.label_cpt_sentence.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_4.addWidget(self.label_cpt_sentence)

        self.label_sentence = QLabel(self.area_sentence)
        self.label_sentence.setObjectName(u"label_sentence")
        sizePolicy1.setHeightForWidth(self.label_sentence.sizePolicy().hasHeightForWidth())
        self.label_sentence.setSizePolicy(sizePolicy1)
        font3 = QFont()
        font3.setFamilies([u"Roboto"])
        font3.setPointSize(20)
        font3.setBold(True)
        self.label_sentence.setFont(font3)
        self.label_sentence.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_sentence.setWordWrap(True)

        self.verticalLayout_4.addWidget(self.label_sentence)


        self.verticalLayout.addWidget(self.area_sentence)

        self.area_button = QWidget(self.area_menu)
        self.area_button.setObjectName(u"area_button")
        self.horizontalLayout = QHBoxLayout(self.area_button)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.button_record = QPushButton(self.area_button)
        self.button_record.setObjectName(u"button_record")
        self.button_record.setEnabled(True)
        sizePolicy.setHeightForWidth(self.button_record.sizePolicy().hasHeightForWidth())
        self.button_record.setSizePolicy(sizePolicy)
        self.button_record.setFont(font1)
        self.button_record.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_record.setStyleSheet(u"")

        self.horizontalLayout.addWidget(self.button_record)


        self.verticalLayout.addWidget(self.area_button)


        self.horizontalLayout_3.addWidget(self.area_menu)

        self.horizontalLayout_3.setStretch(0, 3)
        self.horizontalLayout_3.setStretch(1, 2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 820, 23))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
#if QT_CONFIG(shortcut)
        self.label_micro.setBuddy(self.select_micro)
        self.label_select_camera.setBuddy(self.select_camera)
        self.label_select_language.setBuddy(self.select_camera)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.select_micro, self.button_test_micro)
        QWidget.setTabOrder(self.button_test_micro, self.select_camera)
        QWidget.setTabOrder(self.select_camera, self.select_language)
        QWidget.setTabOrder(self.select_language, self.button_record)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label_record_timer.setText("")
        self.label_record_dot.setText("")
        self.label_micro.setText(QCoreApplication.translate("MainWindow", u"Micro :", None))
        self.button_test_micro.setText(QCoreApplication.translate("MainWindow", u"Test micro", None))
        self.label_micro_state.setText(QCoreApplication.translate("MainWindow", u"Volume du micro :", None))
        self.label_select_camera.setText(QCoreApplication.translate("MainWindow", u"Cam\u00e9ra :", None))
        self.label_select_language.setText(QCoreApplication.translate("MainWindow", u"Langue :", None))
        self.label_cpt_sentence.setText("")
        self.label_sentence.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.button_record.setText(QCoreApplication.translate("MainWindow", u"Record", None))
    # retranslateUi

