# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\install.ui'
#
# Created: Sun Sep 07 03:14:53 2014
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(484, 534)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setWindowOpacity(1.0)
        MainWindow.setStyleSheet(_fromUtf8("background-color: rgb(53, 53, 53);\n"
"font: 75 15pt \"Open Sans\";\n"
"color: rgb(225, 225, 225);\n"
"\n"
""))
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label_5 = QtGui.QLabel(self.centralwidget)
        self.label_5.setStyleSheet(_fromUtf8("font: 75 12pt \"Open Sans\";"))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.horizontalLayout_4.addWidget(self.label_5)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.close_btn = QtGui.QPushButton(self.centralwidget)
        self.close_btn.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.close_btn.setStyleSheet(_fromUtf8("border:none;"))
        self.close_btn.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("images/close.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.close_btn.setIcon(icon)
        self.close_btn.setIconSize(QtCore.QSize(30, 30))
        self.close_btn.setFlat(True)
        self.close_btn.setObjectName(_fromUtf8("close_btn"))
        self.horizontalLayout_4.addWidget(self.close_btn)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setMinimumSize(QtCore.QSize(0, 200))
        self.label.setStyleSheet(_fromUtf8(""))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_3.addWidget(self.label)
        self.verticalLayout_4.addLayout(self.verticalLayout_3)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.frame = QtGui.QFrame(self.centralwidget)
        self.frame.setStyleSheet(_fromUtf8("border-style: outset;\n"
"     border-width: 2px;\n"
"     border-radius: 10px;\n"
"     border-color: grey;"))
        self.frame.setObjectName(_fromUtf8("frame"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.frame)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_4 = QtGui.QLabel(self.frame)
        self.label_4.setStyleSheet(_fromUtf8("border:none;"))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout_2.addWidget(self.label_4)
        self.server_le = QtGui.QLineEdit(self.frame)
        self.server_le.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);\n"
"border:none;\n"
"font: 75 10pt \"Open Sans\";\n"
"color:black;\n"
"padding: 4px;"))
        self.server_le.setFrame(True)
        self.server_le.setObjectName(_fromUtf8("server_le"))
        self.horizontalLayout_2.addWidget(self.server_le)
        self.serverSet_btn = QtGui.QPushButton(self.frame)
        self.serverSet_btn.setMinimumSize(QtCore.QSize(30, 0))
        self.serverSet_btn.setMaximumSize(QtCore.QSize(16777214, 16777215))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Open Sans"))
        font.setPointSize(15)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(9)
        self.serverSet_btn.setFont(font)
        self.serverSet_btn.setStyleSheet(_fromUtf8("border-style: outset;\n"
"     border-width: 1px;\n"
"     border-radius: 10px;\n"
"     border-color: grey;"))
        self.serverSet_btn.setText(_fromUtf8("..."))
        self.serverSet_btn.setDefault(False)
        self.serverSet_btn.setFlat(True)
        self.serverSet_btn.setObjectName(_fromUtf8("serverSet_btn"))
        self.horizontalLayout_2.addWidget(self.serverSet_btn)
        self.horizontalLayout_3.addWidget(self.frame)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(15)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        spacerItem4 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem4)
        self.serverInstall_btn = QtGui.QPushButton(self.centralwidget)
        self.serverInstall_btn.setMinimumSize(QtCore.QSize(100, 100))
        self.serverInstall_btn.setMaximumSize(QtCore.QSize(100, 100))
        self.serverInstall_btn.setStyleSheet(_fromUtf8("background-color: rgb(0, 170, 0);\n"
"border:none;\n"
"     border-width: 2px;\n"
"     border-radius: 10px;"))
        self.serverInstall_btn.setText(_fromUtf8(""))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8("images/arrow.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.serverInstall_btn.setIcon(icon1)
        self.serverInstall_btn.setIconSize(QtCore.QSize(100, 100))
        self.serverInstall_btn.setFlat(False)
        self.serverInstall_btn.setObjectName(_fromUtf8("serverInstall_btn"))
        self.verticalLayout_2.addWidget(self.serverInstall_btn)
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_2.addWidget(self.label_2)
        spacerItem5 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem5)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        spacerItem6 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem6)
        self.clientInstall_btn = QtGui.QPushButton(self.centralwidget)
        self.clientInstall_btn.setMinimumSize(QtCore.QSize(100, 100))
        self.clientInstall_btn.setMaximumSize(QtCore.QSize(100, 100))
        self.clientInstall_btn.setStyleSheet(_fromUtf8("background-color: rgb(0, 85, 127);\n"
"border:none;\n"
"     border-width: 2px;\n"
"     border-radius: 10px;"))
        self.clientInstall_btn.setText(_fromUtf8(""))
        self.clientInstall_btn.setIcon(icon1)
        self.clientInstall_btn.setIconSize(QtCore.QSize(100, 100))
        self.clientInstall_btn.setObjectName(_fromUtf8("clientInstall_btn"))
        self.verticalLayout.addWidget(self.clientInstall_btn)
        self.label_3 = QtGui.QLabel(self.centralwidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        spacerItem7 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem7)
        self.horizontalLayout.addLayout(self.verticalLayout)
        spacerItem8 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem8)
        self.verticalLayout_4.addLayout(self.horizontalLayout)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.close_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "PipeL Installer", None))
        self.label_5.setText(_translate("MainWindow", "1.0", None))
        self.label.setText(_translate("MainWindow", "<html><head/><body><p>Welcome to PipeL installation,</p><p>please choose between server or client setup</p></body></html>", None))
        self.label_4.setText(_translate("MainWindow", "Server Path:", None))
        self.label_2.setText(_translate("MainWindow", "Server", None))
        self.label_3.setText(_translate("MainWindow", "Client", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

