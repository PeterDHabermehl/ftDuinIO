#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import sys, time
import ftduino_direct as ftd
from PyQt4 import QtCore
from TouchStyle import *

class FtcGuiApplication(TouchApplication):
    def __init__(self, args):
        TouchApplication.__init__(self, args)
        
        self.window = TouchWindow("ftDuinIO")       
        
        self.setMainWidget()
        self.window.setCentralWidget(self.mainWidget)
        
        self.window.show()
        
        self.exec_()        
        
    def fFlash_clicked(self):
        self.fLabel.hide()
        self.fSelect.hide()
        self.fBinary.hide()
        self.fFlash.hide()
        self.fWidget.hide()

        self.fWidget.show()
    
        self.fCon.setText("ftd:> avrdude ftduino_direct")
        self.processEvents()
        self.fWidget.repaint()
        for n in range(0,16):
            a="["
            for m in range(0,20):
                if m<=n: a=a + "="
                else: a=a+" "
            a=a+"]"
            self.fCon.setText("ftd:> avrdude ftduino_direct\n"+a)
            self.processEvents()
            self.fWidget.repaint()
            time.sleep(0.2)
            
        time.sleep(1)
        self.fCon.setText("ftd:> avrdude ftduino_direct\n"+a+"\navrdude failed error 42\nftd:>")
    
    def xBack_clicked(self):
        self.dWidget.show()
        self.fWidget.hide()
        self.ioWidget.hide()
        
    def dIO_clicked(self):
        self.dWidget.hide()
        self.fWidget.hide()
        self.ioWidget.show()
        
    def dFlash_clicked(self):
        self.dWidget.hide()
        self.ioWidget.hide()
        self.fCon.setText("ftd:> ")
        self.fLabel.show()
        self.fSelect.show()
        self.fBinary.show()
        self.fFlash.show()
        self.fWidget.show()

    def setDWidget(self):        
        # Widget für Devices:
        
        self.dWidget=QWidget()
        
        devices=QVBoxLayout()
        
        hbox=QHBoxLayout()
        
        text=QLabel(QCoreApplication.translate("devices","Device:"))
        text.setStyleSheet("font-size: 20px;")
        hbox.addWidget(text)
        
        hbox.addStretch()
        
        self.dRescan=QPushButton(QCoreApplication.translate("devices","Rescan"))
        self.dRescan.setStyleSheet("font-size: 20px;")
        hbox.addWidget(self.dRescan)
        
        devices.addLayout(hbox)
        
        self.dList=QComboBox()
        self.dList.setStyleSheet("font-size: 20px;")
        self.dList.addItem(" --- none ---")
        devices.addWidget(self.dList)
        
        hbox=QVBoxLayout()
        
        text=QLabel(QCoreApplication.translate("devices","Communication:"))
        text.setStyleSheet("font-size: 20px;")
        hbox.addWidget(text)

        self.dComm=QLineEdit()
        self.dComm.setReadOnly(True)
        self.dComm.setStyleSheet("font-size: 20px; color: white;")
        self.dComm.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.dComm.setText(QCoreApplication.translate("flash","no device"))
        hbox.addWidget(self.dComm)
        
        devices.addLayout(hbox)
        
        devices.addStretch()
        
        self.dIO=QPushButton(QCoreApplication.translate("devices","I/O test"))
        self.dIO.setStyleSheet("font-size: 20px;")
        
        devices.addWidget(self.dIO)
        
        self.dFlash=QPushButton(QCoreApplication.translate("devices","Flash binary"))
        self.dFlash.setStyleSheet("font-size: 20px;")
        devices.addWidget(self.dFlash)
        
        self.dWidget.setLayout(devices)
        
        self.dIO.clicked.connect(self.dIO_clicked)
        self.dFlash.clicked.connect(self.dFlash_clicked)

    def setFWidget(self):       
        # widget für Flashtool:
        
        self.fWidget=QWidget()
        
        flash=QVBoxLayout()
        
        hbox=QHBoxLayout()
        
        self.fLabel=QLabel(QCoreApplication.translate("flash","Binary:"))
        self.fLabel.setStyleSheet("font-size: 20px;")
        hbox.addWidget(self.fLabel)
        
        self.fSelect=QPushButton(QCoreApplication.translate("flash","Select"))
        self.fSelect.setStyleSheet("font-size: 20px;")
        hbox.addWidget(self.fSelect)
        
        flash.addLayout(hbox)
        
        self.fBinary=QLineEdit()
        self.fBinary.setReadOnly(True)
        self.fBinary.setStyleSheet("font-size: 20px; color: white;")
        self.fBinary.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.fBinary.setText(QCoreApplication.translate("flash","ftduino_direct"))
        flash.addWidget(self.fBinary)
        
        self.fFlash=QPushButton(QCoreApplication.translate("flash","--> Flash <--"))
        self.fFlash.setStyleSheet("font-size: 20px; color: white; background-color: darkred;")
        flash.addWidget(self.fFlash)
        
        self.fCon=QTextEdit()
        self.fCon.setReadOnly(True)
        self.fCon.setWordWrapMode(QTextOption.WrapAnywhere)
        self.fCon.setStyleSheet("font-size: 12px; color: white; background-color: black; font-family: monospace;")
        self.fCon.setText("root> ")
        flash.addWidget(self.fCon)
        
        self.fBack=QPushButton(QCoreApplication.translate("flash","Back"))
        self.fBack.setStyleSheet("font-size: 20px; color: white;")
        flash.addWidget(self.fBack)
        
        self.fWidget.setLayout(flash)
        
        self.fFlash.clicked.connect(self.fFlash_clicked)
        self.fBack.clicked.connect(self.xBack_clicked)        
    
    def setIOWidget(self):
        # widget für I/O Test
        self.ioWidget=QWidget()
        
        io=QVBoxLayout()
        
        self.ioFun=QComboBox()
        self.ioFun.setStyleSheet("font-size: 20px;")
        self.ioFun.addItems(  [ QCoreApplication.translate("io","Inp. Switch"),
                                QCoreApplication.translate("io","Inp. Voltage"),
                                QCoreApplication.translate("io","Inp. Resistance"),
                                QCoreApplication.translate("io","Inp. Dist.&Count."),
                                QCoreApplication.translate("io","Outputs"),
                                QCoreApplication.translate("io","Motors")
                               ] )
        io.addWidget(self.ioFun)
        
        # Verschiedene I/O Widgets:
        
        # Dist. und counter input
        self.iDCType=QComboBox()
        self.iDCType.setStyleSheet("font-size: 20px;")
        self.iDCType.addItems(  [   QCoreApplication.translate("io","Counters"),
                                    QCoreApplication.translate("io","Distance")
                                ] )
        io.addWidget(self.iDCType)  
        
        self.iDCType.hide()
        
        # Dig. & analog Input
        self.iTextField=QTextEdit()
        self.iTextField.setReadOnly(True)
        self.iTextField.setWordWrapMode(QTextOption.WrapAnywhere)
        self.iTextField.setStyleSheet("font-size: 15px; color: white; background-color: black; font-family: monospace;")
        self.iTextField.setText("I1: ____0\nI2: ____0\nI3: ____0\nI4: ____0\nI5: ____0\nI6: ____0\nI7: ____0\nI8: ____0")
        io.addWidget(self.iTextField)
        
        self.iTextField.hide()
        
        # outputs:
        self.oOut=QWidget()
        oOut=QVBoxLayout()
        
        hbox=QHBoxLayout()
        
        self.oPower=QSlider()
        self.oPower.setMinimum(0)
        self.oPower.setMaximum(512)
        self.oPower.setOrientation(1)
        
        hbox.addWidget(self.oPower)
        
        self.oPVal=QLabel()
        self.oPVal.setStyleSheet("font-size: 20px; color: white;")
        self.oPVal.setText("512")
        hbox.addWidget(self.oPVal)
        oOut.addLayout(hbox)
        
        hbox=QHBoxLayout()
        self.oB1=QPushButton("O1")
        self.oB1.setStyleSheet("font-size: 20px;")
        hbox.addWidget(self.oB1)
        self.oB2=QPushButton("O2")
        self.oB2.setStyleSheet("font-size: 20px;")
        hbox.addWidget(self.oB2)        
        oOut.addLayout(hbox)

        hbox=QHBoxLayout()
        self.oB3=QPushButton("O3")
        self.oB3.setStyleSheet("font-size: 20px;")
        hbox.addWidget(self.oB3)
        self.oB4=QPushButton("O4")
        self.oB4.setStyleSheet("font-size: 20px;")
        hbox.addWidget(self.oB4)        
        oOut.addLayout(hbox)
        
        hbox=QHBoxLayout()
        self.oB5=QPushButton("O5")
        self.oB5.setStyleSheet("font-size: 20px;")
        hbox.addWidget(self.oB5)
        self.oB6=QPushButton("O6")
        self.oB6.setStyleSheet("font-size: 20px;")
        hbox.addWidget(self.oB6)        
        oOut.addLayout(hbox)
        
        hbox=QHBoxLayout()
        self.oB7=QPushButton("O7")
        self.oB7.setStyleSheet("font-size: 20px;")
        hbox.addWidget(self.oB7)
        self.oB8=QPushButton("O8")
        self.oB8.setStyleSheet("font-size: 20px;")
        hbox.addWidget(self.oB8)        
        oOut.addLayout(hbox)
        
        self.oOut.setLayout(oOut)
        
        io.addWidget(self.oOut)
        
        #self.oOut.hide()

        # motor outputs:
        self.oMot=QWidget()
        oMot=QVBoxLayout()
        
        hbox=QHBoxLayout()
        
        self.mPower=QSlider()
        self.mPower.setMinimum(0)
        self.mPower.setMaximum(512)
        self.mPower.setOrientation(1)
        
        hbox.addWidget(self.mPower)
        
        self.mPVal=QLabel()
        self.mPVal.setStyleSheet("font-size: 20px; color: white;")
        self.mPVal.setText("512")
        hbox.addWidget(self.mPVal)
        oMot.addLayout(hbox)
        
        hbox=QHBoxLayout()
        self.mB1=QPushButton(QCoreApplication.translate("mout"," left "))
        self.mB1.setStyleSheet("font-size: 20px;")
        hbox.addWidget(self.mB1)
        txt=QLabel("M1")
        txt.setStyleSheet("font-size: 20px;")
        txt.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        hbox.addWidget(txt)
        self.mB2=QPushButton(QCoreApplication.translate("mout","right"))
        self.mB2.setStyleSheet("font-size: 20px;")
        hbox.addWidget(self.mB2)        
        oMot.addLayout(hbox)

        hbox=QHBoxLayout()
        self.mB3=QPushButton(QCoreApplication.translate("mout","left"))
        self.mB3.setStyleSheet("font-size: 20px;")
        hbox.addWidget(self.mB3)
        txt=QLabel("M2")
        txt.setStyleSheet("font-size: 20px;")
        txt.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        hbox.addWidget(txt)
        self.mB4=QPushButton(QCoreApplication.translate("mout","right"))
        self.mB4.setStyleSheet("font-size: 20px;")
        hbox.addWidget(self.mB4)        
        oMot.addLayout(hbox)
        
        hbox=QHBoxLayout()
        self.mB5=QPushButton(QCoreApplication.translate("mout","left"))
        self.mB5.setStyleSheet("font-size: 20px;")
        hbox.addWidget(self.mB5)
        txt=QLabel("M3")
        txt.setStyleSheet("font-size: 20px;")
        txt.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        hbox.addWidget(txt)
        self.mB6=QPushButton(QCoreApplication.translate("mout","right"))
        self.mB6.setStyleSheet("font-size: 20px;")
        hbox.addWidget(self.mB6)        
        oMot.addLayout(hbox)
        
        hbox=QHBoxLayout()
        self.mB7=QPushButton(QCoreApplication.translate("mout","left"))
        self.mB7.setStyleSheet("font-size: 20px;")
        hbox.addWidget(self.mB7)
        txt=QLabel("M4")
        txt.setStyleSheet("font-size: 20px;")
        txt.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        hbox.addWidget(txt)
        self.mB8=QPushButton(QCoreApplication.translate("mout","right"))
        self.mB8.setStyleSheet("font-size: 20px;")
        hbox.addWidget(self.mB8)        
        oMot.addLayout(hbox)
        
        self.oMot.setLayout(oMot)
        
        io.addWidget(self.oMot)
        
        self.oMot.hide()
        
        
        # Back-button!
        io.addStretch()
        self.ioBack=QPushButton(QCoreApplication.translate("io","Back"))
        self.ioBack.setStyleSheet("font-size: 20px;")
        io.addWidget(self.ioBack)
        
        self.ioWidget.setLayout(io)
        
        self.ioBack.clicked.connect(self.xBack_clicked)
        
    def setMainWidget(self):
        self.setDWidget()
        self.setFWidget()
        self.setIOWidget()
        
        self.mainWidget=QWidget()
        mL=QVBoxLayout()
        mL.addWidget(self.dWidget)
        mL.addWidget(self.fWidget)
        mL.addWidget(self.ioWidget)
        
        self.dWidget.show()
        self.fWidget.hide()
        self.ioWidget.hide()
        
        self.mainWidget.setLayout(mL)
        
if __name__ == "__main__":
    FtcGuiApplication(sys.argv)


