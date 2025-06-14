import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QTextEdit, QFileDialog, QMessageBox, QSpinBox,
                           QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from simplex import SolveEquation, PrintColumn

class SimplexSolverGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Linear Programming Solver")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Input section
        input_group = QWidget()
        input_layout = QVBoxLayout(input_group)
        
        # Number of constraints and variables
        size_layout = QHBoxLayout()
        self.n_spin = QSpinBox()
        self.n_spin.setRange(1, 100)
        self.m_spin = QSpinBox()
        self.m_spin.setRange(1, 100)
        size_layout.addWidget(QLabel("Number of constraints:"))
        size_layout.addWidget(self.n_spin)
        size_layout.addWidget(QLabel("Number of variables:"))
        size_layout.addWidget(self.m_spin)
        input_layout.addLayout(size_layout)
        
        # Matrix A input
        self.matrix_a = QTableWidget()
        self.matrix_a.setHorizontalHeaderLabels(["x1", "x2", "x3", "x4", "x5"])
        input_layout.addWidget(QLabel("Matrix A (coefficients):"))
        input_layout.addWidget(self.matrix_a)
        
        # Vector b input
        self.vector_b = QTableWidget()
        self.vector_b.setHorizontalHeaderLabels(["b"])
        input_layout.addWidget(QLabel("Vector b (right-hand side):"))
        input_layout.addWidget(self.vector_b)
        
        # Vector c input
        self.vector_c = QTableWidget()
        self.vector_c.setHorizontalHeaderLabels(["c"])
        input_layout.addWidget(QLabel("Vector c (objective function):"))
        input_layout.addWidget(self.vector_c)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.update_size_btn = QPushButton("Update Size")
        self.update_size_btn.clicked.connect(self.update_table_sizes)
        self.solve_btn = QPushButton("Solve")
        self.solve_btn.clicked.connect(self.solve_problem)
        self.import_btn = QPushButton("Import from File")
        self.import_btn.clicked.connect(self.import_from_file)
        button_layout.addWidget(self.update_size_btn)
        button_layout.addWidget(self.solve_btn)
        button_layout.addWidget(self.import_btn)
        input_layout.addLayout(button_layout)
        
        # Result display
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        input_layout.addWidget(QLabel("Solution:"))
        input_layout.addWidget(self.result_display)
        
        layout.addWidget(input_group)
        
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
                        QMessageBox.warning(self, "Input Error", f"Please enter a value for A[{i+1},{j+1}]")
                        return None
                    try:
                        row.append(float(item.text()))
                    except ValueError:
                        QMessageBox.warning(self, "Input Error", f"Invalid number in A[{i+1},{j+1}]")
                        return None
                a.append(row)
            
            # Get vector b
            b = []
            for i in range(n):
                item = self.vector_b.item(i, 0)
                if not item or not item.text().strip():
                    QMessageBox.warning(self, "Input Error", f"Please enter a value for b[{i+1}]")
                    return None
                try:
                    b.append(float(item.text()))
                except ValueError:
                    QMessageBox.warning(self, "Input Error", f"Invalid number in b[{i+1}]")
                    return None
            
            # Get vector c
            c = []
            for j in range(m):
                item = self.vector_c.item(0, j)
                if not item or not item.text().strip():
                    QMessageBox.warning(self, "Input Error", f"Please enter a value for c[{j+1}]")
                    return None
                try:
                    c.append(float(item.text()))
                except ValueError:
                    QMessageBox.warning(self, "Input Error", f"Invalid number in c[{j+1}]")
                    return None
            
            return a, b, c, n, m
        except Exception as e:
            QMessageBox.warning(self, "Input Error", f"An unexpected error occurred: {str(e)}")
            return None
    
    def solve_problem(self):
        data = self.get_input_data()
        if data:
            a, b, c, n, m = data
            solution = SolveEquation(a, b, c, n, m)
            
            # Display solution
            self.result_display.clear()
            if solution[0] == -1:
                self.result_display.setText("No solution")
            elif solution[0] == float("inf"):
                self.result_display.setText("Infinity")
            else:
                self.result_display.setText("Bounded solution\n")
                self.result_display.append(" ".join([f"{x:.18f}" for x in solution]))
    
    def import_from_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Import Problem", "", "Text Files (*.txt)")
        if file_name:
            try:
                with open(file_name, 'r') as f:
                    # Read n and m
                    first_line = f.readline().strip()
                    if not first_line:
                        raise ValueError("Empty file")
                    
                    try:
                        n, m = map(int, first_line.split())
                        if n <= 0 or m <= 0:
                            raise ValueError("n and m must be positive integers")
                    except ValueError as e:
                        raise ValueError(f"Invalid n,m format: {str(e)}")
                    
                    self.n_spin.setValue(n)
                    self.m_spin.setValue(m)
                    self.update_table_sizes()
                    
                    # Read matrix A
                    for i in range(n):
                        line = f.readline().strip()
                        if not line:
                            raise ValueError(f"Missing row {i+1} in matrix A")
                        try:
                            row = list(map(float, line.split()))
                            if len(row) != m:
                                raise ValueError(f"Row {i+1} in matrix A has wrong number of values")
                            for j in range(m):
                                self.matrix_a.setItem(i, j, QTableWidgetItem(str(row[j])))
                        except ValueError as e:
                            raise ValueError(f"Invalid number in matrix A row {i+1}: {str(e)}")
                    
                    # Read vector b
                    line = f.readline().strip()
                    if not line:
                        raise ValueError("Missing vector b")
                    try:
                        b = list(map(float, line.split()))
                        if len(b) != n:
                            raise ValueError("Vector b has wrong number of values")
                        for i in range(n):
                            self.vector_b.setItem(i, 0, QTableWidgetItem(str(b[i])))
                    except ValueError as e:
                        raise ValueError(f"Invalid number in vector b: {str(e)}")
                    
                    # Read vector c
                    line = f.readline().strip()
                    if not line:
                        raise ValueError("Missing vector c")
                    try:
                        c = list(map(float, line.split()))
                        if len(c) != m:
                            raise ValueError("Vector c has wrong number of values")
                        for j in range(m):
                            self.vector_c.setItem(0, j, QTableWidgetItem(str(c[j])))
                    except ValueError as e:
                        raise ValueError(f"Invalid number in vector c: {str(e)}")
                        
            except Exception as e:
                QMessageBox.warning(self, "Import Error", f"Error reading file: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SimplexSolverGUI()
    window.show()
    sys.exit(app.exec_()) 