import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QTextEdit, QFileDialog, QMessageBox, QSpinBox,
                           QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from simplex import SolveEquation, PrintColumn, CreateTableau, SelectPivotElement, ProcessPivotElement, solveTableau, valid_answer, determine_answer, Position, EPS

# Epsilon functions for comparison
def epsilon_greater_than(a, b):
    return ((a > b) and not isclose(a, b))

def epsilon_greater_than_equal_to(a, b):
    return ((a > b) or isclose(a, b))

def epsilon_less_than(a, b):
    return ((a < b) and not isclose(a, b))

def epsilon_less_than_equal_to(a, b):
    return ((a < b) or isclose(a, b))

def isclose(a, b):
    return abs(a-b) <= EPS

# Enhanced functions for detailed solving process
def format_tableau(tableau, m, n):
    """Format tableau for display"""
    result = []
    for i, row in enumerate(tableau):
        if i < len(tableau) - 1:
            result.append(f"Contrainte {i+1}: {row}")
        else:
            result.append(f"Fonction objectif: {row}")
    return "\n".join(result)

def enhanced_solve_equation(a, b, c, n, m, inequality_types, callback=None):
    """Enhanced version of SolveEquation that provides detailed output"""
    if callback:
        callback("=== DÉBUT DE LA RÉSOLUTION ===\n")
        callback("Paramètres du problème:")
        callback(f"- Nombre de contraintes: {n}")
        callback(f"- Nombre de variables: {m}")
        callback(f"- Types d'inégalités: {inequality_types}")
        callback(f"- Vecteur b: {b}")
        callback(f"- Vecteur c: {c}\n")
    
    # First attempt: Standard simplex
    if callback:
        callback("=== TENTATIVE: MÉTHODE DU SIMPLEXE STANDARD ===\n")
    
    tableau, phase_one_row = CreateTableau(a, b, c, n, False, inequality_types)
    
    if callback:
        callback("Tableau initial créé pour la méthode standard")
        callback(format_tableau(tableau, m, n))
        callback("\n")
    
    steps = []
    ans, phase_one_answer = solveTableau(tableau, a, b, m, n, False, phase_one_row, steps=steps)
    
    # Display step-by-step for standard simplex
    if callback:
        for step in steps:
            callback(f"Itération {step['iteration']} (Méthode standard):")
            callback(format_tableau(step['tableau'], m, n))
            if step['pivot'] is not None:
                callback(f"Pivot: ligne {step['pivot'][0]+1}, colonne {step['pivot'][1]+1}")
            callback(f"Variables de base: {step['slack_rows']}")
            callback("\n")
    
    if ans == [-1] or ans == [float("inf")]:
        if callback:
            callback(f"Résultat de la méthode standard: {'Pas de solution' if ans == [-1] else 'Solution non bornée'}\n")
        return ans
    
    invalid_answer = valid_answer(ans, a, b, m, n, inequality_types)
    
    if callback:
        callback("Vérification de la validité de la solution standard...")
        if invalid_answer:
            callback("❌ Solution standard invalide détectée")
            callback("La solution viole au moins une contrainte")
        else:
            callback("✅ Solution standard valide")
        callback("\n")
    
    # Second attempt: Two-phase simplex if needed
    if invalid_answer:
        if callback:
            callback("=== PASSAGE À LA MÉTHODE DU SIMPLEXE EN DEUX PHASES ===\n")
        
        tableau, phase_one_row = CreateTableau(a, b, c, n, True, inequality_types)
        
        if callback:
            callback("Nouveau tableau créé pour la méthode en deux phases")
            callback(format_tableau(tableau, m, n))
            callback(f"Ligne de phase 1: {phase_one_row}")
            callback("\n")
        
        steps2 = []
        ans, phase_one_answer = solveTableau(tableau, a, b, m, n, True, phase_one_row, steps=steps2)
        
        # Display step-by-step for two-phase simplex
        if callback:
            for step in steps2:
                callback(f"Itération {step['iteration']} (Deux phases):")
                callback(format_tableau(step['tableau'], m, n))
                if step['pivot'] is not None:
                    callback(f"Pivot: ligne {step['pivot'][0]+1}, colonne {step['pivot'][1]+1}")
                callback(f"Variables de base: {step['slack_rows']}")
                callback("\n")
        
        phase_one_answer_invalid = valid_answer(phase_one_answer, a, b, m, n, inequality_types)
        
        if ans == [-1] or ans == [float("inf")]:
            if callback:
                callback(f"Résultat de la méthode en deux phases: {'Pas de solution' if ans == [-1] else 'Solution non bornée'}\n")
            return ans
        
        invalid_answer = valid_answer(ans, a, b, m, n, inequality_types)
        
        if callback:
            callback("Vérification de la validité de la solution en deux phases...")
            if invalid_answer:
                callback("❌ Solution en deux phases invalide")
            else:
                callback("✅ Solution en deux phases valide")
            callback("\n")
    
    if invalid_answer:
        if not phase_one_answer_invalid:
            if callback:
                callback("Utilisation de la solution de phase 1 comme solution finale")
            return phase_one_answer
        else:
            if callback:
                callback("Aucune solution valide trouvée")
            return [-1]
    
    if callback:
        callback("=== SOLUTION FINALE TROUVÉE ===\n")
    
    return ans

def enhanced_solve_tableau(tableau, a, b, m, n, phase_one_optimization, phase_one_row, callback=None, method_name="Standard"):
    """Enhanced version of solveTableau with detailed output"""
    slack_rows = list(range(m, n+m))
    phase_one_complete = False
    phase_one_answer = [0] * m
    iteration = 0
    
    if callback:
        callback(f"--- Début de la résolution ({method_name}) ---")
        callback(f"Variables de base initiales: {slack_rows}")
        callback("\n")
    
    while (phase_one_optimization or not all(epsilon_greater_than_equal_to(i, 0) for i in tableau[len(tableau)-1][:-1])):
        iteration += 1
        
        if callback:
            callback(f"--- Itération {iteration} ---")
            callback("Tableau actuel:")
            callback(format_tableau(tableau, m, n))
            callback(f"Variables de base: {slack_rows}")
            callback(f"Ligne de phase 1: {phase_one_row if phase_one_optimization else 'N/A'}")
            callback("\n")
        
        if phase_one_optimization and all(epsilon_less_than_equal_to(k, 0) for k in phase_one_row[:-1]):
            phase_one_optimization = False
            phase_one_complete = True
            phase_one_answer = determine_answer(tableau, slack_rows, m)
            
            if callback:
                callback("✅ Phase 1 terminée avec succès")
                callback(f"Solution de phase 1: {phase_one_answer}")
                callback("\n")
            
            if all(epsilon_greater_than_equal_to(i, 0) for i in tableau[len(tableau)-1][:-1]):
                if callback:
                    callback("✅ Solution optimale trouvée après phase 1")
                break
        
        no_solution, pivot_element = SelectPivotElement(tableau, m, slack_rows, phase_one_optimization, phase_one_row)
        
        if callback:
            callback("Sélection de l'élément pivot:")
            if no_solution:
                callback("❌ Aucun élément pivot trouvé")
            else:
                callback(f"Pivot: ligne {pivot_element.row + 1}, colonne {pivot_element.column + 1}")
                callback(f"Valeur du pivot: {tableau[pivot_element.row][pivot_element.column]}")
            callback("\n")
        
        if no_solution:
            if phase_one_complete:
                if callback:
                    callback("❌ Pas de solution réalisable")
                return [-1], phase_one_answer
            else:
                if callback:
                    callback("❌ Solution non bornée")
                return [float("inf")], phase_one_answer
        
        # Update basic variables
        old_basic = slack_rows[pivot_element.row]
        slack_rows[pivot_element.row] = pivot_element.column
        
        if callback:
            callback("Mise à jour des variables de base:")
            callback(f"Variable sortante: x{old_basic + 1}")
            callback(f"Variable entrante: x{pivot_element.column + 1}")
            callback(f"Nouvelles variables de base: {slack_rows}")
            callback("\n")
        
        # Process pivot
        tableau, phase_one_row = ProcessPivotElement(tableau, pivot_element, phase_one_optimization, phase_one_row)
        
        if callback:
            callback("Tableau après pivot:")
            callback(format_tableau(tableau, m, n))
            callback("\n")
    
    final_answer = determine_answer(tableau, slack_rows, m)
    
    if callback:
        callback(f"--- Fin de la résolution ({method_name}) ---")
        callback(f"Solution finale: {final_answer}")
        callback(f"Nombre total d'itérations: {iteration}")
        callback("\n")
    
    return final_answer, phase_one_answer

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
        main_layout = QHBoxLayout(central_widget)  # Changed to horizontal layout
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Left side - Input controls
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(15)
        
        # Fix: Define size_layout before using it
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Type de problème:"))
        self.problem_type_combo = QComboBox()
        self.problem_type_combo.addItems(["Maximisation", "Minimisation"])
        self.problem_type_combo.setFixedWidth(150)
        size_layout.addWidget(self.problem_type_combo)        
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
        # Add problem type selection to size group
        size_layout.addWidget(QLabel("Type de problème:"))
        self.problem_type_combo = QComboBox()
        self.problem_type_combo.addItems(["Maximisation", "Minimisation"])
        self.problem_type_combo.setFixedWidth(150)
        size_layout.addWidget(self.problem_type_combo)
        size_layout.addStretch()
        
        input_layout.addWidget(size_group)
        
        # Matrix A input
        matrix_group = QGroupBox("Matrice A (coefficients)")
        matrix_layout = QVBoxLayout(matrix_group)
        self.matrix_a = QTableWidget()
        self.matrix_a.setHorizontalHeaderLabels(["x1", "x2", "x3", "x4", "x5"])
        matrix_layout.addWidget(self.matrix_a)
        input_layout.addWidget(matrix_group)
        
        # Inequality types
        inequality_group = QGroupBox("Types d'inégalités")
        inequality_layout = QVBoxLayout(inequality_group)
        self.inequality_types = QTableWidget()
        self.inequality_types.setHorizontalHeaderLabels(["Type"])
        self.inequality_types.setColumnCount(1)
        inequality_layout.addWidget(self.inequality_types)
        input_layout.addWidget(inequality_group)
        
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
        
        # Add input section to left layout
        left_layout.addWidget(input_group)
        
        # Right side - Result display
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)
        
        result_group = QGroupBox("Solution")
        result_layout = QVBoxLayout(result_group)
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setMinimumHeight(600)  # Increased height for better visibility
        self.result_display.setFont(QFont('Consolas', 11))
        result_layout.addWidget(self.result_display)
        
        right_layout.addWidget(result_group)
        
        # Add widgets to main layout with proportions
        main_layout.addWidget(left_widget, 2)  # Left side takes 2/3 of the space
        main_layout.addWidget(right_widget, 1)  # Right side takes 1/3 of the space
        
        # Initialize table sizes
        self.update_table_sizes()
        
    def update_table_sizes(self):
        n = self.n_spin.value()
        m = self.m_spin.value()
        
        # Update matrix A
        self.matrix_a.setRowCount(n)
        self.matrix_a.setColumnCount(m)
        self.matrix_a.setHorizontalHeaderLabels([f"x{i+1}" for i in range(m)])
        
        # Update inequality types
        self.inequality_types.setRowCount(n)
        self.inequality_types.setColumnCount(1)
        for i in range(n):
            if not self.inequality_types.item(i, 0):
                combo = QComboBox()
                combo.addItems(["≤", "≥", "="])
                self.inequality_types.setCellWidget(i, 0, combo)
        
        # Update vector b
        self.vector_b.setRowCount(n)
        self.vector_b.setColumnCount(1)
        
        # Update vector c
        self.vector_c.setRowCount(1)
        self.vector_c.setColumnCount(m)
        
        # Resize columns to content
        for table in [self.matrix_a, self.vector_b, self.vector_c, self.inequality_types]:
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
            
            # Get inequality types
            inequality_types = []
            for i in range(n):
                combo = self.inequality_types.cellWidget(i, 0)
                if not combo:
                    QMessageBox.warning(self, "Erreur de saisie", f"Type d'inégalité manquant pour la contrainte {i+1}")
                    return None
                inequality_types.append(combo.currentText())
            
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
            
            return a, b, c, n, m, inequality_types
        except Exception as e:
            QMessageBox.warning(self, "Erreur de saisie", f"Une erreur inattendue s'est produite: {str(e)}")
            return None
    
    def solve_problem(self):
        data = self.get_input_data()
        if data:
            a, b, c, n, m, inequality_types = data
            problem_type = self.problem_type_combo.currentText()            
            # Adjust objective function for minimization
            if problem_type == "Minimisation":
                c = [-x for x in c]  # Convert min to max by negating coefficients
            
            self.result_display.clear()

            # Use enhanced solving function with detailed output
            solution = enhanced_solve_equation(a, b, c, n, m, inequality_types, callback=self.result_display.append)
            
            # Display final solution summary
            self.result_display.append("\n" + "="*50)
            self.result_display.append("RÉSUMÉ DE LA SOLUTION")
            self.result_display.append("="*50)
            
            if solution[0] == -1:
                self.result_display.append("\n❌ PAS DE SOLUTION RÉALISABLE")
                self.result_display.append("Le problème n'admet pas de solution qui satisfait toutes les contraintes.")
            elif solution[0] == float("inf"):
                self.result_display.append("\n❌ SOLUTION NON BORNÉE")
                self.result_display.append("La fonction objectif peut prendre des valeurs arbitrairement grandes.")
            else:
                # Calculate and display objective value
                objective_value = sum(c_i * x_i for c_i, x_i in zip(c, solution))
                if problem_type == "Minimisation":
                    objective_value = -objective_value  # Convert back to minimization value
                
                self.result_display.append("\n✅ SOLUTION OPTIMALE TROUVÉE")
                self.result_display.append("\n📊 Valeurs des variables:")
                for i in range(m):
                    self.result_display.append(f"   x{i+1} = {solution[i]:.6f}")
                
                self.result_display.append(f"\n🎯 Valeur optimale de la fonction objectif: {objective_value:.6f}")
                
                # Verify constraints
                self.result_display.append("\n🔍 Vérification des contraintes:")
                for i in range(n):
                    valid_ans = sum(a[i][j] * solution[j] for j in range(m))
                    status = "✅" if (
                        (inequality_types[i] == "≤" and valid_ans <= b[i] + 1e-4) or
                        (inequality_types[i] == "≥" and valid_ans >= b[i] - 1e-4) or
                        (inequality_types[i] == "=" and abs(valid_ans - b[i]) <= 1e-4)
                    ) else "❌"
                    self.result_display.append(f"   Contrainte {i+1}: {valid_ans:.6f} {inequality_types[i]} {b[i]} {status}")
    
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
                    
                    # Read problem type
                    problem_type_line = f.readline().strip()
                    if problem_type_line == "min":
                        self.problem_type_combo.setCurrentText("Minimisation")
                    else:
                        self.problem_type_combo.setCurrentText("Maximisation")                    
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
                    
                    # Read inequality types
                    for i in range(n):
                        line = f.readline().strip()
                        if not line:
                            raise ValueError(f"Ligne {i+1} manquante pour les types d'inégalités")
                        try:
                            inequality_type = line.strip()
                            # Convert common ASCII forms to Unicode
                            if inequality_type in ["==", "="]:
                                inequality_type = "="
                            if inequality_type in ["<=", "=<"]:
                                inequality_type = "≤"
                            elif inequality_type in [">=", "=>"]:
                                inequality_type = "≥"
                            if inequality_type not in ["≤", "≥", "="]:
                                raise ValueError(f"Type d'inégalité invalide pour la contrainte {i+1}: {inequality_type}")
                            combo = self.inequality_types.cellWidget(i, 0)
                            if combo is not None:
                                combo.setCurrentText(inequality_type)
                            else:
                                self.inequality_types.setItem(i, 0, QTableWidgetItem(inequality_type))
                        except ValueError as e:
                            raise ValueError(f"Erreur lors de la lecture du type d'inégalité pour la contrainte {i+1}: {str(e)}")
                    
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