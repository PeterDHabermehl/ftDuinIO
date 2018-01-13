#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import sys, time, serial
import ftduino_direct as ftd
from PyQt4 import QtCore
from TouchStyle import *
from TouchAuxiliary import *
from PyQt4.QtCore import QTimer

class FtcGuiApplication(TouchApplication):
    def __init__(self, args):
        TouchApplication.__init__(self, args)
        
        
        self.duinos=[]
        self.act_duino=None
        
        self.window = TouchWindow("ftDuinIO")       
        self.window.titlebar.close.clicked.connect(self.end)
        
        self.setMainWidget()
        self.window.setCentralWidget(self.mainWidget)
        
        self.window.show()
        
        self.ftdscan()
        
        self.checker=QTimer()
        self.checker.timeout.connect(self.checkFtdComm)
        self.checker.start(250)
        
        
        self.exec_()        
        
    def end(self):
        self.out=False        
        if self.act_duino!=None:
            try:
                self.act_duino.close()
            except:
                pass
            
    def checkFtdComm(self):
        if self.act_duino!=None:
            n=self.act_duino.comm("ftduino_id_get")
            if n=="Fail":
                self.act_duino=None
                self.ftdcomm()    
        
    def ftdscan(self):
        duinos=ftd.ftduino_scan()
        self.duinos=[]
        for d in duinos:
            if d[1]!="":
                self.duinos.append(d[1])
            else:
                self.duinos.append(d[0])
        self.dList.clear()

        if len(self.duinos)>0:
            self.ftdcomm()
            self.dList.addItems(self.duinos)
        else:
            self.dFlash.setDisabled(True)
            self.dRename.setDisabled(True)
            self.dIO.setDisabled(True)
            self.dList.addItem(QCoreApplication.translate("comm","none found"))
            self.dComm.setStyleSheet("font-size: 20px;")
            self.dComm.setText(QCoreApplication.translate("comm","no"))
                
    def ftdcomm(self):
        if self.act_duino!=None:
            try:
                self.act_duino.close()
            except:
                pass
            
        self.act_duino=ftd.ftduino(ftd.ftduino_find_by_name(self.dList.currentText()))
        time.sleep(0.25)
        n=self.act_duino.comm("ftduino_id_get")
        if n!="Fail":
            self.dComm.setStyleSheet("font-size: 20px; background-color: darkgreen;")
            self.dComm.setText(QCoreApplication.translate("comm","active"))
            self.dRename.setDisabled(False)
            self.dFlash.setDisabled(False)
            self.dIO.setDisabled(False)
        else:
            self.dComm.setStyleSheet("font-size: 20px; background-color: darkred;")
            self.dComm.setText(QCoreApplication.translate("comm","failed"))
            self.dRename.setDisabled(True)
            self.dFlash.setDisabled(False)
            self.dIO.setDisabled(True)
        
    def rename_clicked(self):
        n=self.act_duino.comm("ftduino_id_get")
        if n!="" and n!="Fail":
            (res,st)=TouchAuxRequestText(QCoreApplication.translate("rename","Rename"),
                    QCoreApplication.translate("rename","Enter new ftDuino ID for device '") + n +"':",
                    n,
                    QCoreApplication.translate("rename","Okay"), self.window
                    ).exec_()
            if ((st!="") and res):
                res=self.act_duino.comm("ftduino_id_set "+st)
        self.rescan_clicked()
        
    def rescan_clicked(self):
        self.dComm.setStyleSheet("font-size: 20px; background-color: darkorange;")
        self.dComm.setText(QCoreApplication.translate("comm","scanning"))
        self.processEvents()
        self.dComm.repaint()
        self.ftdscan()
    
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
        self.out=False
        self.dWidget.show()
        self.fWidget.hide()
        self.ioWidget.hide()
        self.processEvents()
        self.ftdcomm()
    
    def io_changed(self):
        self.doIO()
    
    def dIO_clicked(self):
        self.dWidget.hide()
        self.fWidget.hide()
        self.ioWidget.show()
        self.out=True
        self.doIO()
    
    def doIO(self):        
        outType=self.ioFun.currentIndex()
        dist=self.iDCType.currentIndex()
        

        if outType==0:
            self.iDCType.hide()
            self.iTextField.show()
            self.oOut.hide()
            self.oMot.hide()
            for n in range(1,9):
                i=self.act_duino.comm("input_set_mode I"+str(n)+" Switch")
        elif outType==1:
            self.iDCType.hide()
            self.iTextField.show()
            self.oOut.hide()
            self.oMot.hide()
            for n in range(1,9):
                i=self.act_duino.comm("input_set_mode I"+str(n)+" Voltage")
        elif outType==2:
            self.iDCType.hide()
            self.iTextField.show()
            self.oOut.hide()
            self.oMot.hide()
            for n in range(1,9):
                i=self.act_duino.comm("input_set_mode I"+str(n)+" Resistance")
        elif outType==3:
            self.iDCType.show()
            self.iTextField.show()
            self.oOut.hide()
            self.oMot.hide()
            for n in range(1,5):
                i=self.act_duino.comm("counter_set_mode C"+str(n)+" Any")
                i=self.act_duino.comm("counter_clear C"+str(n))
            if dist==0: #counters Only
                i=self.act_duino.comm("ultrasonic_enable false")
            else: # dist + counters
                i=self.act_duino.comm("ultrasonic_enable true")
        elif outType==4:
            self.iDCType.hide()
            self.iTextField.hide()
            self.oOut.show()
            self.oMot.hide()
        elif outType==5:
            self.iDCType.hide()
            self.iTextField.hide()
            self.oOut.hide()
            self.oMot.show()
        
        while self.out:
            self.processEvents()
            time.sleep(0.05)
            s=""
            if outType<3:
                for n in range(1,9):
                    s=s+"I"+str(n)+": "
                    i=self.act_duino.comm("input_get I"+str(n))
                    if outType==0:
                        if i=="1":      s=s+"True"
                        elif i=="0":    s=s+"False"
                        else:           s=s+"Fail"
                        s=s+"\n"
                    elif outType==1:
                        a="     "+i
                        s=s+a[-5:]+" mV\n"
                    elif outType==2:
                        a="     "+i
                        s=s+a[-5:]+" Ohm\n"              
                self.iTextField.setText(s)
            elif outType==3:
                if dist==0:
                    a="     "+self.act_duino.comm("counter_get C1")
                    s="C1: "+a[-5:]+"\n"
                else:
                    a=self.act_duino.comm("ultrasonic_get")
                    if a!="-1":
                        a="     "+a
                        s="D1: "+a[-5:]+" cm\n"
                    else: s="D1:  Fail\n"
                for n in range(2,5):
                    s=s+"C"+str(n)+": "
                    a="     "+self.act_duino.comm("counter_get C"+str(n))
                    s=s+a[-5:]+"\n"
                self.iTextField.setText(s)
                
            
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
        
        hbox=QHBoxLayout()
        
        text=QLabel(QCoreApplication.translate("devices","Connect:"))
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
        
        self.dRename=QPushButton(QCoreApplication.translate("devices","Rename"))
        self.dRename.setStyleSheet("font-size: 20px;")
        
        devices.addWidget(self.dRename)
        
        self.dFlash=QPushButton(QCoreApplication.translate("devices","Flash binary"))
        self.dFlash.setStyleSheet("font-size: 20px;")
        devices.addWidget(self.dFlash)
        
        self.dWidget.setLayout(devices)
        
        self.dRescan.clicked.connect(self.rescan_clicked)
        self.dRename.clicked.connect(self.rename_clicked)
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
        
        #self.iTextField.hide()
        
        # outputs:
        self.oOut=QWidget()
        oOut=QVBoxLayout()
        
        hbox=QHBoxLayout()
        
        self.oPower=QSlider()
        self.oPower.setMinimum(0)
        self.oPower.setMaximum(512)
        self.oPower.setOrientation(1)
        self.oPower.setValue(512)
        
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
        
        self.oOut.hide()
        
        self.oB1.pressed.connect(self.oB1_pressed)
        self.oB1.released.connect(self.oB1_released)
        self.oB2.pressed.connect(self.oB2_pressed)
        self.oB2.released.connect(self.oB2_released)
        self.oB3.pressed.connect(self.oB3_pressed)
        self.oB3.released.connect(self.oB3_released)
        self.oB4.pressed.connect(self.oB4_pressed)
        self.oB4.released.connect(self.oB4_released)
        self.oB5.pressed.connect(self.oB5_pressed)
        self.oB5.released.connect(self.oB5_released)
        self.oB6.pressed.connect(self.oB6_pressed)
        self.oB6.released.connect(self.oB6_released)
        self.oB7.pressed.connect(self.oB7_pressed)
        self.oB7.released.connect(self.oB7_released)
        self.oB8.pressed.connect(self.oB8_pressed)
        self.oB8.released.connect(self.oB8_released)
        
        self.oPower.valueChanged.connect(self.oPower_changed)
        
        # motor outputs:
        self.oMot=QWidget()
        oMot=QVBoxLayout()
        
        hbox=QHBoxLayout()
        
        self.mPower=QSlider()
        self.mPower.setMinimum(0)
        self.mPower.setMaximum(512)
        self.mPower.setOrientation(1)
        self.mPower.setValue(512)
        
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
        
        self.mB1.pressed.connect(self.mB1_pressed)
        self.mB1.released.connect(self.mB1_released)
        self.mB2.pressed.connect(self.mB2_pressed)
        self.mB2.released.connect(self.mB2_released)
        self.mB3.pressed.connect(self.mB3_pressed)
        self.mB3.released.connect(self.mB3_released)
        self.mB4.pressed.connect(self.mB4_pressed)
        self.mB4.released.connect(self.mB4_released)
        self.mB5.pressed.connect(self.mB5_pressed)
        self.mB5.released.connect(self.mB5_released)
        self.mB6.pressed.connect(self.mB6_pressed)
        self.mB6.released.connect(self.mB6_released)
        self.mB7.pressed.connect(self.mB7_pressed)
        self.mB7.released.connect(self.mB7_released)
        self.mB8.pressed.connect(self.mB8_pressed)
        self.mB8.released.connect(self.mB8_released)
        
        self.mPower.valueChanged.connect(self.mPower_changed)
        
        # Back-button!
        io.addStretch()
        self.ioBack=QPushButton(QCoreApplication.translate("io","Back"))
        self.ioBack.setStyleSheet("font-size: 20px;")
        io.addWidget(self.ioBack)
        
        self.ioWidget.setLayout(io)
        
        self.ioFun.currentIndexChanged.connect(self.io_changed)
        self.iDCType.currentIndexChanged.connect(self.io_changed)
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
    
    def oB1_pressed(self):
        self.act_duino.comm("output_set O1 1 "+str(self.oPower.value()))
    def oB1_released(self):
        self.act_duino.comm("output_set O1 1 0")
    def oB2_pressed(self):
        self.act_duino.comm("output_set O2 1 "+str(self.oPower.value()))
    def oB2_released(self):
        self.act_duino.comm("output_set O2 1 0")
    def oB3_pressed(self):
        self.act_duino.comm("output_set O3 1 "+str(self.oPower.value()))
    def oB3_released(self):
        self.act_duino.comm("output_set O3 1 0")
    def oB4_pressed(self):
        self.act_duino.comm("output_set O4 1 "+str(self.oPower.value()))
    def oB4_released(self):
        self.act_duino.comm("output_set O4 1 0")
    def oB5_pressed(self):
        self.act_duino.comm("output_set O5 1 "+str(self.oPower.value()))
    def oB5_released(self):
        self.act_duino.comm("output_set O5 1 0")
    def oB6_pressed(self):
        self.act_duino.comm("output_set O6 1 "+str(self.oPower.value()))
    def oB6_released(self):
        self.act_duino.comm("output_set O6 1 0")
    def oB7_pressed(self):
        self.act_duino.comm("output_set O7 1 "+str(self.oPower.value()))
    def oB7_released(self):
        self.act_duino.comm("output_set O7 1 0")
    def oB8_pressed(self):
        self.act_duino.comm("output_set O8 1 "+str(self.oPower.value()))
    def oB8_released(self):
        self.act_duino.comm("output_set O8 1 0")
    def oPower_changed(self):
        self.oPVal.setText(str(self.oPower.value()))

    def mB1_pressed(self):
        self.act_duino.comm("motor_set M1 left "+str(self.oPower.value()))
    def mB1_released(self):
        self.act_duino.comm("motor_set M1 brake 0")
    def mB2_pressed(self):
        self.act_duino.comm("motor_set M1 right "+str(self.oPower.value()))
    def mB2_released(self):
        self.act_duino.comm("motor_set M1 brake 0")
    def mB3_pressed(self):
        self.act_duino.comm("motor_set M2 left "+str(self.oPower.value()))
    def mB3_released(self):
        self.act_duino.comm("motor_set M2 brake 0")
    def mB4_pressed(self):
        self.act_duino.comm("motor_set M2 right "+str(self.oPower.value()))
    def mB4_released(self):
        self.act_duino.comm("motor_set M2 brake 0")
    def mB5_pressed(self):
        self.act_duino.comm("motor_set M3 left "+str(self.oPower.value()))
    def mB5_released(self):
        self.act_duino.comm("motor_set M3 brake 0")
    def mB6_pressed(self):
        self.act_duino.comm("motor_set M3 right "+str(self.oPower.value()))
    def mB6_released(self):
        self.act_duino.comm("motor_set M3 brake 0")
    def mB7_pressed(self):
        self.act_duino.comm("motor_set M4 left "+str(self.oPower.value()))
    def mB7_released(self):
        self.act_duino.comm("motor_set M4 brake 0")
    def mB8_pressed(self):
        self.act_duino.comm("motor_set M4 right "+str(self.oPower.value()))
    def mB8_released(self):
        self.act_duino.comm("motor_set M4 brake 0")
    def mPower_changed(self):
        self.mPVal.setText(str(self.mPower.value()))
        
if __name__ == "__main__":
    FtcGuiApplication(sys.argv)


