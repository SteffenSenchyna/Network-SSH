import sys
import os
import json
from datetime import time
from random import randint
import pathlib
from PyQt5.QtCore import Qt, QEventLoop, QTimer, QThread, pyqtSignal, pyqtSlot, QObject
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QMessageBox, QVBoxLayout, \
    QTabWidget, QInputDialog, QLabel, QLineEdit, QStatusBar, QProgressBar
from PyQt5 import QtCore
import test
from netmiko import ConnectHandler

class Window(QWidget):
    def __init__(self):
        super().__init__()
        #Initializing Variables
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
        tabs.addTab(self.backupTabUI(), "Network Backup")
        tabs.addTab(self.networkTabUI(), "Network Configuration")
        layout.addWidget(tabs)
        layout.addStretch()

    def directoryCheck(self):
        #Checks to see if there is proper file structure and creates directories if needed
        self.directoryIP = str(pathlib.Path(__file__).parent.resolve())+"\IPs"
        self.directoryConfig = str(pathlib.Path(__file__).parent.resolve())+"\Configs"
        try:
            os.makedirs(self.directoryIP)
            os.makedirs(self.directoryConfig)
        except FileExistsError:
            # directory already exists
            pass

    def backupTabUI(self):
        """Network Back Up page UI."""
        NetMonTab = QWidget()
        layout = QVBoxLayout()
        #Creating buttons and attaching functions to button presses
        bScan = QPushButton('Scan Network')
        bScan.clicked.connect(self.on_click_get_file_path_ip)
        bLoad = QPushButton('Load a IP file')
        bLoad.clicked.connect(self.on_click_get_file_path_ip)
        bDeploy = QPushButton("Backup")
        bDeploy.clicked.connect(self.saveConfig)
        bErase = QPushButton("Erase")
        bErase.clicked.connect(self.eraseConfig)
        #Attaching buttons to GUI
        layout.addWidget(bScan)
        layout.addWidget(bLoad)
        layout.addWidget(bDeploy)
        layout.addWidget(bErase)
        layout.addWidget(self.IPlabel2)
        NetMonTab.setLayout(layout)
        return NetMonTab

    def networkTabUI(self):
        """Network Configuration page UI."""
        NetConfTab = QWidget()
        layout = QVBoxLayout()
        """Buttons for the conf menu"""
        # setting menu to the button
        b1 = QPushButton("Load a command file")
        b1.clicked.connect(lambda:test)
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
            dlg = QMessageBox.critical(self)
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
        ipfile = open(self.directoryIP + '\IPs\%s' % self.filepath_ip)
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
            dlg.exec()
        #If no error promts user for login credentials for network devices
        else:
            #Prompts user for network login credentials credentials
            self.username, done1 = QInputDialog.getText(
                self, 'Input Dialog', 'Enter Username:')
            self.password, done2 = QInputDialog.getText(
                self, 'Input Dialog', 'Enter Password:', QLineEdit.Password)
            self.secret, done3 = QInputDialog.getText(
                self, 'Input Dialog', 'Enter Secret:', QLineEdit.Password)
                
            if self.username == "" or self.password == "" or self.secret == "":
                dlg = QMessageBox.critical(self)
                dlg.setWindowTitle("Error")
                dlg.setText("Please enter all fields")
                dlg.exec()
            
            else:
                #Takes user inputs and sets up netmiko devcie configs
                device = {
                    'device_type': 'cisco_ios',
                    'host': 'ip',
                    'username': '%s' % self.username,
                    'password': '%s' % self.password,
                    'secret': '%s' % self.secret
                }
                #Loading IP file JSON and converting to python dictionary 
                ipfile = open(self.filepath_ip)
                ipJSON = json.load(ipfile)
                #Iterating over the dictionary and grabbing the IPS and then deploying the show run command
                #The output is then saved and written to a .txt file 
                try:
                    for i in ipJSON:
                        device['host'] = ipJSON[i].strip("\n")
                        print("Connecting to ", ipJSON[i])
                        net_connect = ConnectHandler(**device)
                        #The QEvent loop is needed to prevent a hanging SSH call which will crash the GUI
                        loop = QEventLoop()
                        QTimer.singleShot(2000, loop.quit)
                        net_connect.enable()
                        outp = net_connect.send_command('show run')
                        print(ipJSON[i].strip("\n"), " configuration has been saved")
                        with open(f"{self.directoryConfig}\\" + ipJSON[i].strip("\n") + '.txt', 'w') as f:
                            f.write(outp)
                        print("Disconnecting")
                        net_connect.disconnect()
                    print('Devices have been backed up')
                #Prints error message that is thrown from netmiko 
                except Exception as e:
                    print(e)
                
    #Function for erasing configs 
    def eraseConfig(self):
         #Error checking if there is no IP file loaded
        if self.filepath_ip == 'None':
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Error")
            dlg.setText("Please load a IP file")
            dlg.exec()
        #If no error promts user for login credentials for network devices
        else:
            #Prompts user for network login credentials credentials
            self.username, done1 = QInputDialog.getText(
                self, 'Input Dialog', 'Enter Username:')
            self.password, done2 = QInputDialog.getText(
                self, 'Input Dialog', 'Enter Password:', QLineEdit.Password)
            self.secret, done3 = QInputDialog.getText(
                self, 'Input Dialog', 'Enter Secret:', QLineEdit.Password)
                
            if self.username == "" or self.password == "" or self.secret == "":
                dlg = QMessageBox.critical(self)
                dlg.setWindowTitle("Error")
                dlg.setText("Please enter all fields")
                dlg.exec()
            
            else:
                #Takes user inputs and sets up netmiko devcie configs
                device = {
                    'device_type': 'cisco_ios',
                    'host': 'ip',
                    'username': '%s' % self.username,
                    'password': '%s' % self.password,
                    'secret': '%s' % self.secret
                }
                #Loading IP file JSON and converting to python dictionary 
                ipfile = open(self.filepath_ip)
                ipJSON = json.load(ipfile)
                #Iterating over the dictionary and grabbing the IPS and then deploying the write erase reload command
                #The output is then saved and written to a .txt file 
                eraseCommands = ['write erase', 'reload']
                try:
                    for i in ipJSON:
                        device['host'] = ipJSON[i].strip("\n")
                        print("Connecting to ", ipJSON[i])
                        net_connect = ConnectHandler(**device)
                        #The QEvent loop is needed to prevent a hanging SSH call which will crash the GUI
                        loop = QEventLoop()
                        QTimer.singleShot(2000, loop.quit)
                        net_connect.enable()
                        net_connect.send_config_set(eraseCommands)
                        print(ipJSON[i].strip("\n"), " Device has been erased")
                        print("Disconnecting")
                        net_connect.disconnect()
                    print('Devices have been backed up')
                #Prints error message that is thrown from netmiko 
                except Exception as e:
                    print(e)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    sys.exit(app.exec_())
