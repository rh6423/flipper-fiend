from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QLineEdit, QScrollArea, QGridLayout,
                               QFileDialog, QTabWidget, QTableWidget, QTableWidgetItem, QTextEdit,
                               QCheckBox)
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import QSize
from pathlib import Path
import csv
import sys
import os
import subprocess
from subprocess import Popen
import json


# Read the configuration file config.csv and store the settings in a dictionary
config_settings = {}
display_name_dict = {}  # Renamed to avoid confusion with the variable inside the loop
with open('config.csv', mode='r', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        config_item = row['config_item']
        label = row['label']
        value = row['value']
        description = row['description']  # Assuming you might want to use this later
        config_settings[config_item] = value
        display_name_dict[config_item] = label

with open('ffiend.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    games_data = sorted(reader, key=lambda row: (-int(row.get('favorite', '0')), row['display_name'].lower()))


# Read the games data file and sort by the 5th column (column 4 if zero-indexed)
with open('ffiend.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    games_data = sorted(reader, key=lambda row: (-int(row.get('favorite') or '0'), row['display_name'].lower()))


# Now, games_data is sorted based on the values in the 5th column

class ArcadeTile(QWidget):
    def __init__(self, game_data, config_settings, display_name_dict):
        super().__init__()
        self.game_data = game_data
        self.config_settings = config_settings
        # if the img file is not found, use "defaultimg.png"
        if not self.game_data.get('image_file'):
            self.game_data['image_file'] = 'defaultimg.png'
        # print the game name and the image file to the console
        print(f"Game: {self.game_data['display_name']}, Image: {self.game_data['image_file']}")
        self.initUI()
    

    def initUI(self):
        # Vertical layout for each tile
        layout = QVBoxLayout()

        # Determine the image path
        image_file_name = self.game_data.get('image_file', 'defaultimg.png')
        image_path = Path(self.config_settings['wheelimage_file_path']) / image_file_name

        # Game Image
        pixmap = QPixmap(str(image_path))
        lbl_img = QLabel(self)
        lbl_img.setPixmap(pixmap.scaled(200, 200))
        layout.addWidget(lbl_img)

        # Game Title
        display_name = self.game_data.get('display_name')
        # if display_name is empty or not set, use the file name without extension as fallback
        
        if not display_name:
            # Extract file name without extension from 'vpx_file_name'
            display_name = Path(self.game_data.get('vpx_file_name', '')).stem
        # else if display_name is == "[not set]", use the file name without extension as fallback
        elif display_name == "[not set]":
            # Extract file name without extension from 'vpx_file_name'
            display_name = Path(self.game_data.get('vpx_file_name', '')).stem
        lbl_title = QLabel(display_name)
        lbl_title.setFont(QFont("Arial", 14))
        layout.addWidget(lbl_title)

        # Favorite Button
        # update the next line to show the star in yellow if the game is a favorite, grey if not
        self.btn_favorite = QPushButton('★' if self.game_data['favorite'] == '1' else '☆')
        self.btn_favorite.clicked.connect(self.toggleFavorite)
        layout.addWidget(self.btn_favorite)
        self.setLayout(layout)

    def executeShellCommand(self):
        # Use .get() to avoid KeyError and provide a default value if the key is missing
        vpx_file_path = Path(self.config_settings.get('vpx_table_path')) / self.game_data['vpx_file_name']
        # print the path to the console
        print(f"Running table: {vpx_file_path}")
        # vpx_app path should be self.config_settings.get('vpx_app') with /Contents/MacOS/VPinballX_GL appended
        vpx_app_path = Path(self.config_settings.get('vpx_app')) / 'Contents/MacOS/VPinballX_GL'

        #vpx_app_path = Path(self.config_settings.get('vpx_app'
        
        table_name = self.game_data['vpx_file_name']
        vpx_script_name = table_name.split('.')[0] + '.vbs'
        
        # if a matching vbs file exists, use it to run the table
        command = [str(vpx_app_path), '-Play', str(vpx_file_path), '-TableIni', str(vpx_script_name)]
        # print the command to the console
        print(f'{command}')
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while trying to run the game: {e}")

    def updateData(self, game_data):
        self.game_data = game_data
        # Update the wheel image
        image_file_name = self.game_data['image_file']
        image_path = (Path(self.config_settings['image_file_path']) / image_file_name) if image_file_name else Path('defaultimg.png')
        pixmap = QPixmap(str(image_path))
        self.lbl_img.setPixmap(pixmap.scaled(200, 200))  # Assuming self.lbl_img is the QLabel for the image
    
    def mousePressEvent(self, event):
        # You can check the type of mouse click here, if necessary (e.g., right-click, left-click)
        self.executeShellCommand()

    
    def toggleFavorite(self):
        # Toggle the in-memory favorite status
        new_favorite_status = '1' if self.game_data['favorite'] == '0' else '0'
        self.game_data['favorite'] = new_favorite_status

        # Update the CSV file
        games_data = []
        with open('ffiend.csv', mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['vpx_file_name'] == self.game_data['vpx_file_name']:
                    row['favorite'] = new_favorite_status
                games_data.append(row)

        with open('ffiend.csv', mode='w', newline='') as file:
            fieldnames = reader.fieldnames
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(games_data)

        # Update the UI to reflect the change
        self.btn_favorite.setText('★' if self.game_data['favorite'] == '1' else '☆')


class ArcadeWindow(QMainWindow):
    def __init__(self, config_settings, games_data, display_name):
        super().__init__()
        self.config_settings = config_settings
        self.games_data = games_data
        self.display_name = display_name  # Assuming you want to use display_name for something
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Arcade View")
        self.setGeometry(100, 100, 1400, 800)

        central_widget = QWidget()  # Create a central widget
        self.setCentralWidget(central_widget)  # Set the central widget of QMainWindow

        layout = QVBoxLayout()  # Create the main layout
        central_widget.setLayout(layout)  # Set the layout on the central widget

        # Game Manager button
        btn_game_manager = QPushButton('Game Manager')
        # when the button is pressed, open game_manager.py
        def open_game_manager_and_exit():
            # Start game_manager.py non-blocking
            Popen(['python', 'game_manager.py', json.dumps(config_settings)])
            # Exit main.py
            sys.exit()
        btn_game_manager.clicked.connect(open_game_manager_and_exit)
        layout.addWidget(btn_game_manager)

        btn_game_manager.clicked.connect(lambda: os.system('python game_manager.py'))
        layout.addWidget(btn_game_manager)

        # Preferences Button
        btn_preferences = QPushButton('Preferences')
        def open_configure_and_wait():
            # Start configure.py blocking
            subprocess.run(['python', 'configure.py'])
            # Wait for configure.py to finish. Continue running in the background
            # once it completes, re-read the config.csv
            with open('config.csv', mode='r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    config_item = row['config_item']
                    label = row['label']
                    value = row['value']
                    description = row['description']
                    config_settings[config_item] = value
                    display_name_dict[config_item] = label

            # refresh the main window if anything changed
            self.refreshData(games_data)


    
        btn_preferences.clicked.connect(open_configure_and_wait)
        layout.addWidget(btn_preferences)

        # Scroll Area for Game Tiles
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)
        scroll_widget.setLayout(scroll_layout)

        # Create a tile for each game
        for i, game_data in enumerate(self.games_data):
            # tile should have a reference to the game data, config settings, and display name
            tile = ArcadeTile(game_data, self.config_settings, self.display_name)
            scroll_layout.addWidget(tile, i // 4, i % 4)  # 4 columns per row

        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)


    # update arcade view when manage games signals a change
    def refreshData(self, games_data):
        self.games_data = games_data  # Update the games_data
        for i, game_data in enumerate(self.games_data):
            if i < len(self.tiles):  # Check if the tile already exists
                self.tiles[i].updateData(game_data)  # Update the tile data


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Initialize the application with the read configuration and display name
    mainWin = ArcadeWindow(config_settings, games_data, display_name_dict)
    mainWin.show()
    sys.exit(app.exec())
