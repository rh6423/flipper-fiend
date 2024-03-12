import os
import csv
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QLineEdit, QHBoxLayout
from PySide6.QtCore import Qt
import subprocess

def read_config():
    if os.path.exists('config.csv'):
        with open('config.csv', mode='r', newline='') as file:
            reader = csv.DictReader(file)
            return {row['config_item']: row['value'] for row in reader}
    else:
        return {}

def write_config(config_items):
    with open('config.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["config_item", "label", "value", "description"])
        for key, value in config_items.items():
            writer.writerow([key, "", value, ""])  # Adjust as needed

class Configurator(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Configure Preferences")
        self.layout = QVBoxLayout()

        self.createConfigItem("vpx_table_path", "VPX Table Path (Folder):", isFolder=True)
        self.createConfigItem("wheelimage_file_path", "Wheel Image File Path (Folder):", isFolder=True)
        self.createConfigItem("vpx_app", "VPX App (File):", isFolder=False)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.saveConfig)
        self.layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.close)
        self.layout.addWidget(self.cancel_btn)

        self.setLayout(self.layout)

    def createConfigItem(self, key, label, isFolder):
        config_layout = QHBoxLayout()
        label_widget = QLabel(label)
        input_widget = QLineEdit()
        input_widget.setText(self.config.get(key, ""))
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(lambda: self.browse(isFolder, input_widget))

        config_layout.addWidget(label_widget)
        config_layout.addWidget(input_widget)
        config_layout.addWidget(browse_btn)
        self.layout.addLayout(config_layout)

    def browse(self, isFolder, input_widget):
        if isFolder:
            selection = QFileDialog.getExistingDirectory(self, "Select Folder")
        else:
            selection, _ = QFileDialog.getOpenFileName(self, "Select File")
        if selection:
            input_widget.setText(selection)

    def saveConfig(self):
        config_items = {
            "vpx_table_path": self.layout.itemAt(0).layout().itemAt(1).widget().text(),
            "wheelimage_file_path": self.layout.itemAt(1).layout().itemAt(1).widget().text(),
            "vpx_app": self.layout.itemAt(2).layout().itemAt(1).widget().text(),
            "macos_command": self.layout.itemAt(2).layout().itemAt(1).widget().text() + "/Contents/MacOS/VPinballX_GL"
        }
        write_config(config_items)
        self.close()


if __name__ == "__main__":
    app = QApplication([])
    config = read_config()
    win = Configurator(config)
    win.show()
    app.exec()
