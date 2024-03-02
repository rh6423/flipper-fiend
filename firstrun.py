# this file is called by main.py if config.csv is not found at startup
# The main.py window will also allow the user to call this file to change preferences.
# it will ask the user to select the file and folder locations for the following:
    # vpx_table_path, wheelimage_file_path, vpx_app
    # It will also derive the value of macos_command from the user's vpx_app selection:
    # macos_command = vpx_app + "/Contents/Macos/VPinballX_GL"


# When user hits save, it will create or update the config.csv file with the user's selections
# if the user hits cancel, it will close the window and do nothing

# The gui uses PySide6 and is created using Qt Designer

# Schema (or columns) for config.csv: config_item,label,value,description
# config items (or rows) managed in config.csv: , macos_command

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import csv
import os

class MainWindow(QMainWindow):
    # the main window class should present all config items to the user, and give the user a
    # file or folder selection button for each. This will open a window to select the file or folder location for each item:
    # vpx_table_path (a folder), wheelimage_file_path (a folder), vpx_app (a file)

    def __init__(self):
        super(MainWindow, self).__init__()
        loader = QUiLoader()
        self.ui = loader.load(QFile("firstrun.ui"))
        self.ui.show()
        self.ui.FileButton.clicked.connect(self.browse)
        self.ui.SaveButton.clicked.connect(self.save)
        self.ui.CancelButton.clicked.connect(self.cancel)
        self.ui.vpx_app.setText("Select VPinballX_GL.app")
        self.ui.vpx_table_path.setText("Select folder containing tables")
        self.ui.wheelimage_file_path.setText("Select folder containing wheel images")
        self.ui.macos_command.setText("")
        self.ui.vpx_app.setFocus()

    # When the user hits the save button, the config.csv file should be created with the user's selections
    def save(self):
        # create or update config.csv with user's selections
        with open('config.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["config_item", "label", "value", "description"])
            writer.writerow(["macos_command", "macos_command", self.ui.macos_command.text(), "The command to start VPinballX_GL"])
        self.close()

    # When the user hits the cancel button, the window should close and do nothing
    def cancel(self):
        self.close()

        
    # if config.csv exists, read it and populate the fields
    # if not, create it with default values and populate the values
    # if the user hits the browse button, open a file or folder selection window
        
    def browse(self):
        # open a file or folder selection window
        # if the user selects a file or folder, populate the corresponding field with the selection
        # if the user hits cancel, do nothing
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.Directory)
        file_dialog.setOption(QFileDialog.ShowDirsOnly)
        file_dialog.setOption(QFileDialog.DontUseNativeDialog)
        file_dialog.setAcceptMode(QFileDialog.AcceptOpen)
        file_dialog.setDirectory(os.path.expanduser("~"))
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            self.ui.vpx_table_path.setText(selected_files[0])
        else:
            return
        # if the user selects a file or folder, populate the corresponding field with the selection
        # if the user hits cancel, do nothing
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.Directory)
        file_dialog.setOption(QFileDialog.ShowDirsOnly)
        file_dialog.setOption(QFileDialog.DontUseNativeDialog)
        file_dialog.setAcceptMode(QFileDialog.AcceptOpen)
        file_dialog.setDirectory(os.path.expanduser("~"))
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            self.ui.wheelimage_file_path.setText(selected_files[0])
        else:
            return
        # if the user selects a file or folder, populate the corresponding field with the selection
        # if the user hits cancel, do nothing
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setOption(QFileDialog.DontUseNativeDialog)
        file_dialog.setAcceptMode(QFileDialog.AcceptOpen)
        file_dialog.setDirectory(os.path.expanduser("~"))
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            self.ui.vpx_app.setText(selected_files[0])
            self.ui.macos_command.setText(selected_files[0] + "/Contents/MacOS/VPinballX_GL")
        else:
            return
        
# main function
def main():
    app = QApplication([])
    window = MainWindow()
    sys.exit(app.exec())
    

