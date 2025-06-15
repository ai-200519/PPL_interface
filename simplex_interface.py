import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QTextEdit, QFileDialog, QMessageBox, QSpinBox,
                           QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from simplex import SolveEquation, PrintColumn

class SimplexSolverGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Solveur de Programmation Linéaire")
        self.setGeometry(100, 100, 1000, 800)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QSpinBox {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
            }
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                gridline-color: #ecf0f1;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                padding: 10px;
                font-family: 'Consolas', monospace;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Input section
        input_group = QGroupBox("Paramètres du problème")
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(10)
        
        # Number of constraints and variables
        size_group = QGroupBox("Dimensions")
        size_layout = QHBoxLayout(size_group)
        size_layout.setSpacing(20)
        
        self.n_spin = QSpinBox()
        self.n_spin.setRange(1, 100)
        self.n_spin.setFixedWidth(100)
        self.m_spin = QSpinBox()
        self.m_spin.setRange(1, 100)
        self.m_spin.setFixedWidth(100)
        
        size_layout.addWidget(QLabel("Nombre de contraintes:"))
        size_layout.addWidget(self.n_spin)
        size_layout.addWidget(QLabel("Nombre de variables:"))
        size_layout.addWidget(self.m_spin)
        size_layout.addStretch()
        
        input_layout.addWidget(size_group)
        
        # Matrix A input
        matrix_group = QGroupBox("Matrice A (coefficients)")
        matrix_layout = QVBoxLayout(matrix_group)
        self.matrix_a = QTableWidget()
        self.matrix_a.setHorizontalHeaderLabels(["x1", "x2", "x3", "x4", "x5"])
        matrix_layout.addWidget(self.matrix_a)
        input_layout.addWidget(matrix_group)
        
        # Vector b input
        vector_b_group = QGroupBox("Vecteur b (membre droit)")
        vector_b_layout = QVBoxLayout(vector_b_group)
        self.vector_b = QTableWidget()
        self.vector_b.setHorizontalHeaderLabels(["b"])
        vector_b_layout.addWidget(self.vector_b)
        input_layout.addWidget(vector_b_group)
        
        # Vector c input
        vector_c_group = QGroupBox("Vecteur c (fonction objectif)")
        vector_c_layout = QVBoxLayout(vector_c_group)
        self.vector_c = QTableWidget()
        self.vector_c.setHorizontalHeaderLabels(["c"])
        vector_c_layout.addWidget(self.vector_c)
        input_layout.addWidget(vector_c_group)
        
        # Buttons
        button_group = QGroupBox("Actions")
        button_layout = QHBoxLayout(button_group)
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignCenter)  # Center the buttons
        
        self.update_size_btn = QPushButton("Mettre à jour la taille")
        self.update_size_btn.setFixedWidth(200)
        self.update_size_btn.clicked.connect(self.update_table_sizes)
        
        self.solve_btn = QPushButton("Résoudre")
        self.solve_btn.setFixedWidth(200)
        self.solve_btn.clicked.connect(self.solve_problem)
        
        self.import_btn = QPushButton("Importer depuis un fichier")
        self.import_btn.setFixedWidth(200)
        self.import_btn.clicked.connect(self.import_from_file)
        
        button_layout.addStretch(1)  # Add stretch before buttons
        button_layout.addWidget(self.update_size_btn)
        button_layout.addWidget(self.solve_btn)
        button_layout.addWidget(self.import_btn)
        button_layout.addStretch(1)  # Add stretch after buttons
        
        input_layout.addWidget(button_group)
        
        # Result display
        result_group = QGroupBox("Solution")
        result_layout = QVBoxLayout(result_group)
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setMinimumHeight(150)
        self.result_display.setFont(QFont('Consolas', 11))
        result_layout.addWidget(self.result_display)
        
        layout.addWidget(input_group)
        layout.addWidget(result_group)
        
        # Initialize table sizes
        self.update_table_sizes()
        
    def update_table_sizes(self):
        n = self.n_spin.value()
        m = self.m_spin.value()
        
        # Update matrix A
        self.matrix_a.setRowCount(n)
        self.matrix_a.setColumnCount(m)
        self.matrix_a.setHorizontalHeaderLabels([f"x{i+1}" for i in range(m)])
        
        # Update vector b
        self.vector_b.setRowCount(n)
        self.vector_b.setColumnCount(1)
        
        # Update vector c
        self.vector_c.setRowCount(1)
        self.vector_c.setColumnCount(m)
        
        # Resize columns to content
        for table in [self.matrix_a, self.vector_b, self.vector_c]:
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def get_input_data(self):
        try:
            n = self.n_spin.value()
            m = self.m_spin.value()
            
            # Get matrix A
            a = []
            for i in range(n):
                row = []
                for j in range(m):
                    item = self.matrix_a.item(i, j)
                    if not item or not item.text().strip():
                        QMessageBox.warning(self, "Erreur de saisie", f"Veuillez entrer une valeur pour A[{i+1},{j+1}]")
                        return None
                    try:
                        row.append(float(item.text()))
                    except ValueError:
                        QMessageBox.warning(self, "Erreur de saisie", f"Nombre invalide dans A[{i+1},{j+1}]")
                        return None
                a.append(row)
            
            # Get vector b
            b = []
            for i in range(n):
                item = self.vector_b.item(i, 0)
                if not item or not item.text().strip():
                    QMessageBox.warning(self, "Erreur de saisie", f"Veuillez entrer une valeur pour b[{i+1}]")
                    return None
                try:
                    b.append(float(item.text()))
                except ValueError:
                    QMessageBox.warning(self, "Erreur de saisie", f"Nombre invalide dans b[{i+1}]")
                    return None
            
            # Get vector c
            c = []
            for j in range(m):
                item = self.vector_c.item(0, j)
                if not item or not item.text().strip():
                    QMessageBox.warning(self, "Erreur de saisie", f"Veuillez entrer une valeur pour c[{j+1}]")
                    return None
                try:
                    c.append(float(item.text()))
                except ValueError:
                    QMessageBox.warning(self, "Erreur de saisie", f"Nombre invalide dans c[{j+1}]")
                    return None
            
            return a, b, c, n, m
        except Exception as e:
            QMessageBox.warning(self, "Erreur de saisie", f"Une erreur inattendue s'est produite: {str(e)}")
            return None
    
    def solve_problem(self):
        data = self.get_input_data()
        if data:
            a, b, c, n, m = data
            self.result_display.clear()
            self.result_display.setText("Tentative de résolution par la méthode du simplexe standard...\n")
            
            # First attempt with standard simplex
            solution = SolveEquation(a, b, c, n, m)
            
            # Check if we need to switch to two-phase
            if solution[0] != -1 and solution[0] != float("inf"):
                # Verify if the solution is valid
                invalid_answer = False
                for i in range(n):
                    valid_ans = 0
                    for j in range(m):
                        valid_ans += a[i][j] * solution[j]
                    if valid_ans > b[i] + 1e-4:  # Using same epsilon as in simplex.py
                        invalid_answer = True
                        break
                
                if invalid_answer:
                    self.result_display.append("\nSolution initiale invalide détectée.\nPassage à la méthode du simplexe en deux phases...\n")
                    # Second attempt with two-phase
                    solution = SolveEquation(a, b, c, n, m)
            
            # Display final solution
            if solution[0] == -1:
                self.result_display.append("\nRésultat: Pas de solution")
            elif solution[0] == float("inf"):
                self.result_display.append("\nRésultat: Infini")
            else:
                self.result_display.append("\nRésultat: Solution bornée\n")
                self.result_display.append(" ".join([f"{x:.18f}" for x in solution]))
    
    def import_from_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Importer un problème", "", "Fichiers texte (*.txt)")
        if file_name:
            try:
                with open(file_name, 'r') as f:
                    # Read n and m
                    first_line = f.readline().strip()
                    if not first_line:
                        raise ValueError("Fichier vide")
                    
                    try:
                        n, m = map(int, first_line.split())
                        if n <= 0 or m <= 0:
                            raise ValueError("n et m doivent être des entiers positifs")
                    except ValueError as e:
                        raise ValueError(f"Format n,m invalide: {str(e)}")
                    
                    self.n_spin.setValue(n)
                    self.m_spin.setValue(m)
                    self.update_table_sizes()
                    
                    # Read matrix A
                    for i in range(n):
                        line = f.readline().strip()
                        if not line:
                            raise ValueError(f"Ligne {i+1} manquante dans la matrice A")
                        try:
                            row = list(map(float, line.split()))
                            if len(row) != m:
                                raise ValueError(f"La ligne {i+1} de la matrice A a un nombre incorrect de valeurs")
                            for j in range(m):
                                self.matrix_a.setItem(i, j, QTableWidgetItem(str(row[j])))
                        except ValueError as e:
                            raise ValueError(f"Nombre invalide dans la ligne {i+1} de la matrice A: {str(e)}")
                    
                    # Read vector b
                    line = f.readline().strip()
                    if not line:
                        raise ValueError("Vecteur b manquant")
                    try:
                        b = list(map(float, line.split()))
                        if len(b) != n:
                            raise ValueError("Le vecteur b a un nombre incorrect de valeurs")
                        for i in range(n):
                            self.vector_b.setItem(i, 0, QTableWidgetItem(str(b[i])))
                    except ValueError as e:
                        raise ValueError(f"Nombre invalide dans le vecteur b: {str(e)}")
                    
                    # Read vector c
                    line = f.readline().strip()
                    if not line:
                        raise ValueError("Vecteur c manquant")
                    try:
                        c = list(map(float, line.split()))
                        if len(c) != m:
                            raise ValueError("Le vecteur c a un nombre incorrect de valeurs")
                        for j in range(m):
                            self.vector_c.setItem(0, j, QTableWidgetItem(str(c[j])))
                    except ValueError as e:
                        raise ValueError(f"Nombre invalide dans le vecteur c: {str(e)}")
                        
            except Exception as e:
                QMessageBox.warning(self, "Erreur d'importation", f"Erreur lors de la lecture du fichier: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SimplexSolverGUI()
    window.show()
    sys.exit(app.exec_()) 