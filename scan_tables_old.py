# this file loads upopdb.csv, and gives users a way to configure the settings for each record in upopdb.csv
# There is a table view of the data in upopdb.csv in the upper part of the window. User can select
# a record and edit the data in the lower part of the window.
# There is a button bar at the bottom of the window with buttons for "Scan", "Edit Game", and "Exit"
# The "Scan" button examines all .vpx files in vpx_table_path and stages them for addition or 
# update in upopdb.csv
    # for each .vpx file found in vpx_table_path:
        # 1. scan data for the table in upopdb.csv'
        # 2. if vpx file name is not found in upopdb.csv:
            # a. look for the table in puplookup.csv
            # b. if found, add the table to upopdb.csv using puplookup.csv data
            # c. if not found, add the table to upopdb.csv using data from the .vpx file
# The "Edit Game" button opens a new window with fields for each column in upopdb.csv, 
# populated with the data for the selected record.
# The "Exit" button closes the window

# Give the user an option to select a wheel image for a game

import os
import csv
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QLineEdit, QHBoxLayout
from PySide6.QtCore import Qt

