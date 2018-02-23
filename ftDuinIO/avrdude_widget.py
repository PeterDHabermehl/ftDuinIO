#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import os, sys, serial, time
import queue, pty, subprocess, select
from TxtStyle import *

class SmallLabel(QLabel):
    def __init__(self, str, parent=None):
        super(SmallLabel, self).__init__(str, parent)
        self.setObjectName("smalllabel")
        self.setAlignment(Qt.AlignCenter)
        
class AvrdudeWidget(QWidget):
    def __init__(self, port):
        QWidget.__init__(self)
        self.port = port
        
        self.vbox = QVBoxLayout()

        self.vbox.addStretch()
        self.lbl = SmallLabel("Idle")
        self.vbox.addWidget(self.lbl)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.vbox.addWidget(self.progress)
        
        self.result = SmallLabel("")
        self.vbox.addWidget(self.result)
        
        self.vbox.addStretch()

        self.setLayout(self.vbox)
        
    def trigger_bootloader(self):
        self.set_state("bootloader")
        try:
            ser = serial.Serial()
            ser.port = self.port
            ser.baudrate = 1200
            ser.open()
            ser.setDTR(0)
            ser.close()
            time.sleep(1)
        except:
            print("ERROR: Unable to force bootloader")
            return False
        
        return True

    def build_command(self, file):
        cmd = [ "avrdude",
                "-patmega32u4",
                "-cavr109",
                "-P"+self.port,
                "-b57600",
                "-D",
                "-Uflash:w:"+file ]
        return cmd;
    
    def exec_command(self, commandline):
        self.buffer = ""
        self.state = None
        
        # run subprocess
        self.log_master_fd, self.log_slave_fd = pty.openpty()
        self.app_process = subprocess.Popen(commandline, stdout=self.log_slave_fd, stderr=self.log_slave_fd)
        
        # start a timer to monitor the ptys
        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self.on_output_timer)
        self.log_timer.start(1)

    def set_progress(self, perc):
        self.progress.setValue(perc)

    def set_state(self, state):
        if state == "bootloader":
            self.lbl.setText("Preparing ...")
        elif state == "write":
            self.lbl.setText("Writing ...")
        elif state == "verify":
            self.lbl.setText("Verifying ...")
        elif state == "done":
            self.lbl.setText("Upload finished")

    def set_result(self, state):
        if state == None:
            self.result.setText("in progress ...")
        elif state == False:
            self.result.setStyleSheet("QLabel { background-color : red; }");
            self.result.setText("Failure!")
        elif state == True:
            self.result.setStyleSheet("QLabel { background-color : green; }");
            self.result.setText("Success")
            
    def parse_line(self, str):
        # check for state indicators
        if str.startswith("avrdude"):
            parts = str.split()
            if parts[1] == "writing" and parts[2] == "flash":
                self.state = "write"
                self.set_state(self.state)
            if parts[1] == "reading" and parts[2] == "on-chip":
                self.state = "verify"
                self.set_state(self.state)
            if parts[1].startswith("done"):
                self.state = "done"
                self.set_state(self.state)
        
        if str.startswith("Reading") or str.startswith("Writing"):
            # this is a line that belongs to some ascii progress
            # bar. So we parse it for the progress bar widget
            perc = int(str.split('|')[2].strip().split()[0][:-1])
            if self.state == "write":
                self.set_progress(perc/2)
            if self.state == "verify":
                self.set_progress(50+perc/2)
        
    def parse_output(self, data):
        # append to buffer
        self.buffer = self.buffer + data.decode("utf-8")
        lines = self.buffer.splitlines()
        # at least one full line in buffer?
        if len(lines) > 1:
            for i in lines[:-1]: self.parse_line(i)
            # keep last line in buffer, but keep \r if present
            self.buffer = self.buffer.splitlines(True)[-1]
        
    def app_is_running(self):
        if self.app_process == None:
            return False

        return self.app_process.poll() == None
    
    def on_output_timer(self):
        # read whatever the process may have written
        if select.select([self.log_master_fd], [], [], 0)[0]:
            output = os.read(self.log_master_fd, 100)
            if output: self.parse_output(output)
        else:
            # check if process is still alive
            if not self.app_is_running():
                # read all remaining data
                while select.select([self.log_master_fd], [], [], 0)[0]:
                    output = os.read(self.log_master_fd, 100)
                    if output: self.parse_output(output)
                    time.sleep(0.01)
                    
                self.set_result(self.app_process.returncode == 0)

                # close any open ptys
                os.close(self.log_master_fd)
                os.close(self.log_slave_fd)

                # remove timer
                self.log_timer = None
            
    def flash(self, file):
        self.set_result(None)
        if not self.trigger_bootloader():
            self.set_result(False)
            return
        
        cmd = self.build_command(file)
        self.exec_command(cmd)
            
class FtcGuiApplication(TxtApplication):
    def __init__(self, args):
        TxtApplication.__init__(self, args)

        # create the empty main window
        self.w = TxtWindow("AvrDudeDemo")

        self.avrdude = AvrdudeWidget("/dev/ttyACM0")
        self.w.setCentralWidget(self.avrdude)

        # start a timer that fires after one second as
        # if the user clicked something
        self.start_timer = QTimer()
        self.start_timer.timeout.connect(self.on_start)
        self.start_timer.setSingleShot(True)
        self.start_timer.start(10)
 
        self.w.show() 
        self.exec_()        

    def on_start(self):
        # this starts a background process
        self.avrdude.flash("./binaries/Blink.ino.hex:i")
        
if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
