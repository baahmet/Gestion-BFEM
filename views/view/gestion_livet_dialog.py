import sqlite3
from dataclasses import dataclass
from typing import Optional, List, Tuple
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QFormLayout, 
    QLineEdit, QPushButton, QHBoxLayout, QMessageBox,
    QLabel, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

@dataclass
class StudentRecord:
    """Data class to represent a student's academic record."""
    student_id: int
    repetition_count: int
    grades: dict[str, float]
    cycle_average: float

class GradeInput(QDoubleSpinBox):
    """Custom spinbox for grade input with validation."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 20)
        self.setDecimals(2)
        self.setAlignment(Qt.AlignRight)
        self.setButtonSymbols(self.NoButtons)
        self.setStyleSheet("""
            QDoubleSpinBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #fff;
            }
            QDoubleSpinBox:focus {
                border-color: #007bff;
            }
        """)

class GestionLivretDialog(QDialog):
    """Dialog for managing student academic records."""
    
    recordSaved = pyqtSignal(int)  # Signal emitted when record is saved

    def __init__(self, parent=None, student_id: Optional[int] = None):
        super().__init__(parent)
        self.student_id = student_id
        self.setup_ui()
        self.setup_connections()
        if student_id:
            self.load_record()

    def setup_ui(self):
        """Initialize the UI components."""
        self.setWindowTitle("Gestion du Livret Scolaire")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QLabel {
                font-weight: bold;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton[primary="true"] {
                background-color: #007bff;
                color: white;
                border: none;
            }
            QPushButton[primary="true"]:hover {
                background-color: #0056b3;
            }
            QPushButton[secondary="true"] {
                background-color: #6c757d;
                color: white;
                border: none;
            }
            QPushButton[secondary="true"]:hover {
                background-color: #545b62;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Header
        header = QLabel("Livret Scolaire")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        # Input fields
        self.repetition_count = QDoubleSpinBox()
        self.repetition_count.setRange(0, 5)
        self.repetition_count.setDecimals(0)

        self.grade_inputs = {
            '6e': GradeInput(),
            '5e': GradeInput(),
            '4e': GradeInput(),
            '3e': GradeInput()
        }

        self.cycle_average = QLineEdit()
        self.cycle_average.setReadOnly(True)
        self.cycle_average.setStyleSheet("""
            QLineEdit {
                background-color: #e9ecef;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)

        # Add fields to form layout
        form_layout.addRow("Nombre de redoublements:", self.repetition_count)
        for grade_level, input_field in self.grade_inputs.items():
            form_layout.addRow(f"Moyenne {grade_level}:", input_field)
        form_layout.addRow("Moyenne du Cycle:", self.cycle_average)

        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Enregistrer")
        self.save_button.setProperty("primary", True)
        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.setProperty("secondary", True)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)

    def setup_connections(self):
        """Setup signal connections."""
        for input_field in self.grade_inputs.values():
            input_field.valueChanged.connect(self.calculate_cycle_average)
        
        self.save_button.clicked.connect(self.save_record)
        self.cancel_button.clicked.connect(self.reject)

    def calculate_cycle_average(self):
        """Calculate the cycle average from valid grades."""
        valid_grades = [
            input_field.value()
            for input_field in self.grade_inputs.values()
            if input_field.value() > 0
        ]
        
        if valid_grades:
            average = round(sum(valid_grades) / len(valid_grades), 2)
            self.cycle_average.setText(f"{average:.2f}")
        else:
            self.cycle_average.clear()

    def load_record(self):
        """Load existing student record from database."""
        try:
            cursor = self.parent().cur
            cursor.execute(
                "SELECT * FROM Livret_Scolaire WHERE id_candidat = ?", 
                (self.student_id,)
            )
            record = cursor.fetchone()

            if record:
                self.repetition_count.setValue(record[2])
                self.grade_inputs['6e'].setValue(record[3] or 0)
                self.grade_inputs['5e'].setValue(record[4] or 0)
                self.grade_inputs['4e'].setValue(record[5] or 0)
                self.grade_inputs['3e'].setValue(record[6] or 0)
                self.calculate_cycle_average()
        except sqlite3.Error as e:
            QMessageBox.critical(
                self,
                "Erreur de chargement",
                f"Impossible de charger le livret scolaire: {str(e)}"
            )

    def validate_input(self) -> Tuple[bool, str]:
        """Validate user input before saving."""
        if not any(input_field.value() > 0 for input_field in self.grade_inputs.values()):
            return False, "Au moins une moyenne doit être saisie"
        
        for grade_level, input_field in self.grade_inputs.items():
            if input_field.value() > 0 and (input_field.value() < 0 or input_field.value() > 20):
                return False, f"La moyenne de {grade_level} doit être entre 0 et 20"

        return True, ""

    def save_record(self):
        """Save the student record to database."""
        is_valid, error_message = self.validate_input()
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", error_message)
            return

        try:
            cursor = self.parent().cur
            record_data = (
                self.repetition_count.value(),
                self.grade_inputs['6e'].value(),
                self.grade_inputs['5e'].value(),
                self.grade_inputs['4e'].value(),
                self.grade_inputs['3e'].value(),
                float(self.cycle_average.text() or 0),
                self.student_id
            )

            cursor.execute("""
                INSERT OR REPLACE INTO Livret_Scolaire 
                (nombre_de_fois, moyenne_6e, moyenne_5e, moyenne_4e, moyenne_3e, 
                moyenne_cycle, id_candidat)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, record_data)

            self.parent().conn.commit()
            self.recordSaved.emit(self.student_id)
            QMessageBox.information(
                self,
                "Succès",
                "Livret scolaire enregistré avec succès"
            )
            self.accept()

        except sqlite3.Error as e:
            QMessageBox.critical(
                self,
                "Erreur d'enregistrement",
                f"Impossible d'enregistrer le livret scolaire: {str(e)}"
            )

