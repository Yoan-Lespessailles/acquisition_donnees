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
        MainWindow.resize(820, 603)
        MainWindow.setStyleSheet(u"")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_9 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.area_sentence = QWidget(self.centralwidget)
        self.area_sentence.setObjectName(u"area_sentence")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.area_sentence.sizePolicy().hasHeightForWidth())
        self.area_sentence.setSizePolicy(sizePolicy)
        font = QFont()
        font.setFamilies([u"Ubuntu"])
        self.area_sentence.setFont(font)
        self.verticalLayout_4 = QVBoxLayout(self.area_sentence)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.area_label_sentence = QWidget(self.area_sentence)
        self.area_label_sentence.setObjectName(u"area_label_sentence")
        self.horizontalLayout_5 = QHBoxLayout(self.area_label_sentence)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalSpacer_5 = QSpacerItem(248, 20, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_5)

        self.label_sentence = QLabel(self.area_label_sentence)
        self.label_sentence.setObjectName(u"label_sentence")
        sizePolicy.setHeightForWidth(self.label_sentence.sizePolicy().hasHeightForWidth())
        self.label_sentence.setSizePolicy(sizePolicy)
        self.label_sentence.setMinimumSize(QSize(500, 0))
        self.label_sentence.setMaximumSize(QSize(1500, 16777215))
        font1 = QFont()
        font1.setFamilies([u"Roboto"])
        font1.setPointSize(20)
        font1.setBold(True)
        self.label_sentence.setFont(font1)
        self.label_sentence.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_sentence.setWordWrap(True)

        self.horizontalLayout_5.addWidget(self.label_sentence)

        self.horizontalSpacer_4 = QSpacerItem(248, 20, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_4)

        self.horizontalLayout_5.setStretch(0, 1)
        self.horizontalLayout_5.setStretch(1, 10)
        self.horizontalLayout_5.setStretch(2, 1)

        self.verticalLayout_4.addWidget(self.area_label_sentence)

        self.area_cpt_sentence = QWidget(self.area_sentence)
        self.area_cpt_sentence.setObjectName(u"area_cpt_sentence")
        self.horizontalLayout_3 = QHBoxLayout(self.area_cpt_sentence)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_3 = QSpacerItem(349, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.label_cpt_sentence = QLabel(self.area_cpt_sentence)
        self.label_cpt_sentence.setObjectName(u"label_cpt_sentence")
        self.label_cpt_sentence.setMinimumSize(QSize(50, 20))
        self.label_cpt_sentence.setMaximumSize(QSize(500, 500))
        font2 = QFont()
        font2.setFamilies([u"Roboto"])
        self.label_cpt_sentence.setFont(font2)
        self.label_cpt_sentence.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_cpt_sentence.setWordWrap(False)

        self.horizontalLayout_3.addWidget(self.label_cpt_sentence)

        self.horizontalSpacer_2 = QSpacerItem(349, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)


        self.verticalLayout_4.addWidget(self.area_cpt_sentence)


        self.verticalLayout_9.addWidget(self.area_sentence)

        self.area_button = QWidget(self.centralwidget)
        self.area_button.setObjectName(u"area_button")
        self.area_button.setMaximumSize(QSize(16777215, 16777215))
        self.horizontalLayout = QHBoxLayout(self.area_button)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.button_record = QPushButton(self.area_button)
        self.button_record.setObjectName(u"button_record")
        self.button_record.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.button_record.sizePolicy().hasHeightForWidth())
        self.button_record.setSizePolicy(sizePolicy1)
        self.button_record.setMaximumSize(QSize(16777215, 16777215))
        self.button_record.setFont(font2)
        self.button_record.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_record.setStyleSheet(u"")

        self.horizontalLayout.addWidget(self.button_record)


        self.verticalLayout_9.addWidget(self.area_button)

        self.area_menu = QWidget(self.centralwidget)
        self.area_menu.setObjectName(u"area_menu")
        self.horizontalLayout_2 = QHBoxLayout(self.area_menu)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.area_video = QWidget(self.area_menu)
        self.area_video.setObjectName(u"area_video")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.area_video.sizePolicy().hasHeightForWidth())
        self.area_video.setSizePolicy(sizePolicy2)
        self.verticalLayout_3 = QVBoxLayout(self.area_video)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.area_record = QWidget(self.area_video)
        self.area_record.setObjectName(u"area_record")
        sizePolicy1.setHeightForWidth(self.area_record.sizePolicy().hasHeightForWidth())
        self.area_record.setSizePolicy(sizePolicy1)
        self.area_record.setStyleSheet(u"background-color: black;")
        self.horizontalLayout_4 = QHBoxLayout(self.area_record)
        self.horizontalLayout_4.setSpacing(6)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(9, 0, 9, 0)
        self.label_record_timer = QLabel(self.area_record)
        self.label_record_timer.setObjectName(u"label_record_timer")
        font3 = QFont()
        font3.setFamilies([u"Roboto"])
        font3.setBold(True)
        self.label_record_timer.setFont(font3)
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
        sizePolicy.setHeightForWidth(self.area_preview.sizePolicy().hasHeightForWidth())
        self.area_preview.setSizePolicy(sizePolicy)

        self.verticalLayout_3.addWidget(self.area_preview)


        self.horizontalLayout_2.addWidget(self.area_video)

        self.area_select = QWidget(self.area_menu)
        self.area_select.setObjectName(u"area_select")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.area_select.sizePolicy().hasHeightForWidth())
        self.area_select.setSizePolicy(sizePolicy3)
        self.verticalLayout = QVBoxLayout(self.area_select)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.area_language = QWidget(self.area_select)
        self.area_language.setObjectName(u"area_language")
        self.verticalLayout_8 = QVBoxLayout(self.area_language)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.label_select_language = QLabel(self.area_language)
        self.label_select_language.setObjectName(u"label_select_language")
        self.label_select_language.setFont(font2)

        self.verticalLayout_8.addWidget(self.label_select_language)

        self.select_language = QComboBox(self.area_language)
        self.select_language.setObjectName(u"select_language")
        sizePolicy1.setHeightForWidth(self.select_language.sizePolicy().hasHeightForWidth())
        self.select_language.setSizePolicy(sizePolicy1)
        self.select_language.setFont(font2)
        self.select_language.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_8.addWidget(self.select_language)


        self.verticalLayout.addWidget(self.area_language)

        self.area_device = QWidget(self.area_select)
        self.area_device.setObjectName(u"area_device")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.area_device.sizePolicy().hasHeightForWidth())
        self.area_device.setSizePolicy(sizePolicy4)
        self.verticalLayout_7 = QVBoxLayout(self.area_device)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.area_micro_selection = QWidget(self.area_device)
        self.area_micro_selection.setObjectName(u"area_micro_selection")
        self.verticalLayout_2 = QVBoxLayout(self.area_micro_selection)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_micro = QLabel(self.area_micro_selection)
        self.label_micro.setObjectName(u"label_micro")
        self.label_micro.setFont(font2)

        self.verticalLayout_2.addWidget(self.label_micro)

        self.select_micro = QComboBox(self.area_micro_selection)
        self.select_micro.setObjectName(u"select_micro")
        sizePolicy1.setHeightForWidth(self.select_micro.sizePolicy().hasHeightForWidth())
        self.select_micro.setSizePolicy(sizePolicy1)
        self.select_micro.setFont(font2)
        self.select_micro.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_2.addWidget(self.select_micro)


        self.verticalLayout_7.addWidget(self.area_micro_selection)

        self.area_micro_test = QWidget(self.area_device)
        self.area_micro_test.setObjectName(u"area_micro_test")
        self.verticalLayout_6 = QVBoxLayout(self.area_micro_test)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.button_test_micro = QPushButton(self.area_micro_test)
        self.button_test_micro.setObjectName(u"button_test_micro")
        sizePolicy1.setHeightForWidth(self.button_test_micro.sizePolicy().hasHeightForWidth())
        self.button_test_micro.setSizePolicy(sizePolicy1)
        self.button_test_micro.setFont(font2)
        self.button_test_micro.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_test_micro.setTabletTracking(False)
        self.button_test_micro.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        self.verticalLayout_6.addWidget(self.button_test_micro)

        self.label_micro_state = QLabel(self.area_micro_test)
        self.label_micro_state.setObjectName(u"label_micro_state")
        self.label_micro_state.setFont(font2)

        self.verticalLayout_6.addWidget(self.label_micro_state)

        self.progressbar_micro_level = QProgressBar(self.area_micro_test)
        self.progressbar_micro_level.setObjectName(u"progressbar_micro_level")
        sizePolicy1.setHeightForWidth(self.progressbar_micro_level.sizePolicy().hasHeightForWidth())
        self.progressbar_micro_level.setSizePolicy(sizePolicy1)
        self.progressbar_micro_level.setFont(font2)
        self.progressbar_micro_level.setValue(0)
        self.progressbar_micro_level.setTextVisible(False)

        self.verticalLayout_6.addWidget(self.progressbar_micro_level)


        self.verticalLayout_7.addWidget(self.area_micro_test)

        self.area_camera = QWidget(self.area_device)
        self.area_camera.setObjectName(u"area_camera")
        self.verticalLayout_5 = QVBoxLayout(self.area_camera)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.label_select_camera = QLabel(self.area_camera)
        self.label_select_camera.setObjectName(u"label_select_camera")
        self.label_select_camera.setFont(font2)

        self.verticalLayout_5.addWidget(self.label_select_camera)

        self.select_camera = QComboBox(self.area_camera)
        self.select_camera.setObjectName(u"select_camera")
        sizePolicy1.setHeightForWidth(self.select_camera.sizePolicy().hasHeightForWidth())
        self.select_camera.setSizePolicy(sizePolicy1)
        self.select_camera.setFont(font2)
        self.select_camera.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_5.addWidget(self.select_camera)


        self.verticalLayout_7.addWidget(self.area_camera)


        self.verticalLayout.addWidget(self.area_device)


        self.horizontalLayout_2.addWidget(self.area_select)

        self.horizontalLayout_2.setStretch(0, 5)
        self.horizontalLayout_2.setStretch(1, 2)

        self.verticalLayout_9.addWidget(self.area_menu)

        self.verticalLayout_9.setStretch(0, 3)
        self.verticalLayout_9.setStretch(1, 1)
        self.verticalLayout_9.setStretch(2, 7)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 820, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
#if QT_CONFIG(shortcut)
        self.label_select_language.setBuddy(self.select_camera)
        self.label_micro.setBuddy(self.select_micro)
        self.label_select_camera.setBuddy(self.select_camera)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.select_micro, self.button_test_micro)
        QWidget.setTabOrder(self.button_test_micro, self.select_camera)
        QWidget.setTabOrder(self.select_camera, self.select_language)
        QWidget.setTabOrder(self.select_language, self.button_record)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"AVDataCollector", None))
        self.label_sentence.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.label_cpt_sentence.setText("")
        self.button_record.setText(QCoreApplication.translate("MainWindow", u"Start Recording", None))
        self.label_record_timer.setText("")
        self.label_record_dot.setText("")
        self.label_select_language.setText(QCoreApplication.translate("MainWindow", u"Language:", None))
        self.label_micro.setText(QCoreApplication.translate("MainWindow", u"Microphone:", None))
        self.button_test_micro.setText(QCoreApplication.translate("MainWindow", u"Test Mic", None))
        self.label_micro_state.setText(QCoreApplication.translate("MainWindow", u"Microphone Volume:", None))
        self.label_select_camera.setText(QCoreApplication.translate("MainWindow", u"Camera:", None))
    # retranslateUi

