import sys
import os
import json
from datetime import time
from random import randint
import pathlib
from PyQt5.QtCore import Qt, QEventLoop, QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QMessageBox, QVBoxLayout, \
    QTabWidget, QInputDialog, QLabel, QLineEdit, QStatusBar, QProgressBar
from PyQt5 import QtCore

from netmiko import ConnectHandler


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.username = 'None'
        self.password = ''
        self.filepath_cmd = "None"
        self.filepath_ip = "None"
        self.filepath_temp = "None"
        self.setWindowTitle("Network Configuration Manager")
        self.resize(400, 200)
        # Create a top-level layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.directoryCheck()
        # Show loaded files
        self.conflabel = QLabel(self)
        self.conflabel.setText("Command File: %s" % self.filepath_cmd)
        self.conflabel.setAlignment(Qt.AlignBottom)
        self.IPlabel = QLabel(self)
        self.IPlabel.setText("IP File: %s" % self.filepath_ip)
        self.IPlabel.setAlignment(Qt.AlignBottom)
        self.IPlabel2 = QLabel(self)
        self.IPlabel2.setText("IP File: %s" % self.filepath_ip)
        self.IPlabel2.setAlignment(Qt.AlignBottom)
        # Create the tab widget with two tabs
        tabs = QTabWidget()
        tabs.addTab(self.networkTabUI(), "Network Configuration")
        tabs.addTab(self.backupTabUI(), "Network Backup")
        layout.addWidget(tabs)
        layout.addStretch()

    def directoryCheck(self):
        """Checks to see if there is proper file structure and creates directories if needed"""
        self.directory = str(pathlib.Path(__file__).parent.resolve())+"\IPs"
        try:
            os.makedirs(self.directory)
        except FileExistsError:
            # directory already exists
            pass


    def networkTabUI(self):
        """Network Configuration page UI."""
        NetConfTab = QWidget()
        layout = QVBoxLayout()
        """Buttons for the conf menu"""
        # setting menu to the button
        b1 = QPushButton("Load a command file")
        b1.clicked.connect(self.on_click_get_file_path_cmd)
        b2 = QPushButton('Load a IP file')
        b2.clicked.connect(self.on_click_get_file_path_ip)
        b3 = QPushButton("Deploy")
        b3.clicked.connect(self.takeinputs)
        layout.addWidget(b1)
        layout.addWidget(b2)
        layout.addWidget(b3)
        layout.addWidget(self.conflabel)
        layout.addWidget(self.IPlabel)
        NetConfTab.setLayout(layout)
        return NetConfTab

    def backupTabUI(self):
        """Network Back Up page UI."""
        NetMonTab = QWidget()
        layout = QVBoxLayout()
        bScan = QPushButton('Scan Network')
        bScan.clicked.connect(self.on_click_get_file_path_ip)
        bLoad = QPushButton('Load a IP file')
        bLoad.clicked.connect(self.on_click_get_file_path_ip)
        bDeploy = QPushButton("Backup")
        bDeploy.clicked.connect(self.saveConfig)
        bErase = QPushButton("Erase")
        bDeploy.clicked.connect(self.eraseConfig)
        layout.addWidget(bScan)
        layout.addWidget(bLoad)
        layout.addWidget(bDeploy)
        layout.addWidget(bErase)
        layout.addWidget(self.IPlabel2)
        NetMonTab.setLayout(layout)
        return NetMonTab

    def on_click_get_file_path_ip(self):
        path = QFileDialog.getOpenFileName(self, 'Open a file', 'IPs/',
                                           'All Files (*.*)')
        if path != ('', ''):
            self.filepath_ip_label = os.path.basename(path[0])
            self.filepath_ip = path[0]
            self.IPlabel.setText("IP File: %s" % self.filepath_ip_label)
            self.IPlabel.setAlignment(Qt.AlignBottom)
            self.IPlabel2.setText("IP File: %s" % self.filepath_ip_label)
            self.IPlabel2.setAlignment(Qt.AlignBottom)


    def on_click_get_file_path_cmd(self):
        path = QFileDialog.getOpenFileName(self, 'Open a file', 'CmdFiles/',
                                           'All Files (*.*)')
        if path != ('', ''):
            self.filepath_cmd = os.path.basename(path[0])
            self.conflabel.setText("Command File: %s" % self.filepath_cmd)
            self.conflabel.setAlignment(Qt.AlignBottom)



    def takeinputs(self):
        if self.filepath_cmd == 'None' or self.filepath_ip == 'None':
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Error")
            dlg.setText("Please load a IP and a configuration file")
            button = dlg.exec()

        else:
            self.username, done1 = QInputDialog.getText(
                self, 'Input Dialog', 'Enter your username:')

            self.password, done2 = QInputDialog.getText(
                self, 'Input Dialog', 'Enter your password:', QLineEdit.Password)
        device = {
            'device_type': 'cisco_ios',
            'host': 'ip',
            'username': '%s' % self.username,
            'password': '%s' % self.password
        }
        ipfile = open(self.directory + '\IPs\%s' % self.filepath_ip)
        for line in ipfile:
            device['host'] = line.strip("\n")
            print("Connecting to ", line)
            net_connect = ConnectHandler(**device)
            loop = QEventLoop()
            QTimer.singleShot(2000, loop.quit)
            loop.exec_()
            net_connect.config_mode()
            check = net_connect.check_config_mode()
            if check == True:
                outp = net_connect.send_config_from_file('CmdFiles/%s' % self.filepath_cmd)
                print("Disconnecting")
                net_connect.disconnect()
            else:
                print('Unable to enter configure terminal for ', line)
                print("Disconnecting")
                net_connect.disconnect()
        print('Commands have been deployed')
    #Function for saving configs
    def saveConfig(self):
        #Error checking if there is no IP file loaded
        if self.filepath_ip == 'None':
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Error")
            dlg.setText("Please load a IP file")
            button = dlg.exec()
        #If no error the promts user for login credentials for network devices
        else:
            self.username, done1 = QInputDialog.getText(
                self, 'Input Dialog', 'Enter your username:')

            self.password, done2 = QInputDialog.getText(
                self, 'Input Dialog', 'Enter your password:', QLineEdit.Password)
        device = {
            'device_type': 'cisco_ios',
            'host': 'ip',
            'username': '%s' % self.username,
            'password': '%s' % self.password
        }
        #Loading IP file JSON and converting to python dictionary 
        ipfile = open(self.filepath_ip)
        ipJSON = json.load(ipfile)
        #Iterating over the dictionary and grabbing the IPS and then deploying the show run command
        #to the networking devices these outputs are saved to .txt files
        for i in ipJSON:
            device['host'] = ipJSON[i].strip("\n")
            print("Connecting to ", ipJSON[i])
            net_connect = ConnectHandler(**device)
            loop = QEventLoop()
            QTimer.singleShot(2000, loop.quit)
            outp = net_connect.send_command('show run')
            print(ipJSON[i].strip("\n"), " configuration has been saved")
            with open('Configs/' + ipJSON[i].strip("\n") + '.txt', 'w') as f:
                f.write(outp)
            print("Disconnecting")
            net_connect.disconnect()
        print('Devices have been backed up')
    #Function for erasing configs 
    def eraseConfig(self):
        #Error checking if there is no IP file loaded
        if self.filepath_ip == 'None':
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Error")
            dlg.setText("Please load a IP file")
            button = dlg.exec()
        #If no error the promts user for login credentials for network devices
        else:
            self.username, done1 = QInputDialog.getText(
                self, 'Input Dialog', 'Enter your username:')

            self.password, done2 = QInputDialog.getText(
                self, 'Input Dialog', 'Enter your password:', QLineEdit.Password)
        device = {
            'device_type': 'cisco_ios',
            'host': 'ip',
            'username': '%s' % self.username,
            'password': '%s' % self.password
        }
        #Loading IP file JSON and converting to python dictionary 
        ipfile = open(self.filepath_ip)
        ipJSON = json.load(ipfile)
        #Iterating over the dictionary and grabbing the IPS and then deploying the write erase command
        for i in ipJSON:
            device['host'] = ipJSON[i].strip("\n")
            print("Connecting to ", ipJSON[i])
            net_connect = ConnectHandler(**device)
            loop = QEventLoop()
            QTimer.singleShot(2000, loop.quit)
            outp = net_connect.send_command('show run')
            print(ipJSON[i].strip("\n"), " configuration has been saved")
            with open('Configs/' + ipJSON[i].strip("\n") + '.txt', 'w') as f:
                f.write(outp)
            print("Disconnecting")
            net_connect.disconnect()
        print('Devices have been backed up')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    sys.exit(app.exec_())
