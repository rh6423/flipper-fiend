import os
import csv
from PySide6.QtWidgets import QApplication, QMainWindow, QTableView, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QFileDialog, QMessageBox, QLineEdit, QLabel, QFormLayout
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex

class CsvTableModel(QAbstractTableModel):
    def __init__(self, csv_data):
        super().__init__()
        self.csv_data = csv_data  # Renamed from 'data' to 'csv_data' to avoid conflict
        self.headers = ["Column1", "Column2", "Column3", "..."]  # Adjust based on your CSV

    def rowCount(self, parent=QModelIndex()):
        return len(self.csv_data)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers) if self.csv_data else 0

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            # Return the value for the given index
            return self.csv_data[index.row()][index.column()]
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            # Return the appropriate header based on the section index
            if section < len(self.headers):
                return self.headers[section]
        return None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Configuration")
        self.resize(1024, 768)
        
        # Load CSV data
        self.ffiend_data = self.load_csv("ffiend.csv")
        self.model = CsvTableModel(self.ffiend_data)
        
        # Main layout
        layout = QVBoxLayout()
        
        # Table view
        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        layout.addWidget(self.table_view)
        
        # Set column widths here
        self.table_view.setColumnWidth(0, 100)  # Set width of the first column
        self.table_view.setColumnWidth(1, 500)  # Set width of the second column
        self.table_view.setColumnWidth(2, 300)  # Set width of the third column
        # Add more columns as needed
        
        # Button bar
        button_layout = QHBoxLayout()
        self.scan_button = QPushButton("Scan")
        self.scan_button.clicked.connect(self.scan_vpx_files)
        self.edit_button = QPushButton("Edit Game")
        self.edit_button.clicked.connect(self.edit_game)
        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)
        
        button_layout.addWidget(self.scan_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.exit_button)
        layout.addLayout(button_layout)
        
        # Set main widget
        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    
    def load_csv(self, filepath):
        data = []
        with open(filepath, mode="r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                data.append(row)
        return data

    def scan_vpx_files(self):
        # Implement scanning logic here
        pass

    def edit_game(self):
        # Implement edit game logic here
        if self.table_view.selectionModel().hasSelection():
            selected_row = self.table_view.selectionModel().currentIndex().row()
            # Assuming the first column is the unique identifier for editing
            game_id = self.model.data[selected_row][0]
            self.open_edit_window(game_id)
        else:
            QMessageBox.information(self, "Selection Required", "Please select a game to edit.")

    def open_edit_window(self, game_id):
        #  Redraw the window with the selected game's data from ffiend.csv in an edit window
        # there should be an edit field for each column in ffiend.csv
        self.edit_window = EditGameWindow(game_id)
        self.edit_window.show()
        

        
        
class EditGameWindow(QWidget):
    def __init__(self, game_id):
        super().__init__()
        self.setWindowTitle(f"Edit Game {game_id}")
        self.layout = QFormLayout()
        
        # Example fields for editing, adjust based on your CSV structure
        self.name_field = QLineEdit()
        self.layout.addRow(QLabel("Name:"), self.name_field)
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_changes)
        self.layout.addRow(self.save_button)
        
        self.setLayout(self.layout)
    
    def save_changes(self):
        # Implement save logic
        pass

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
