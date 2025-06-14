# Linear Programming Solver Interface

This is a graphical user interface for solving linear programming problems using the Simplex method and Two-Phase Simplex method.

## Installation

1. Make sure you have Python 3.x installed
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the interface:
```bash
python simplex_interface.py
```

2. You can input your linear programming problem in two ways:

   a. Manual Input:
   - Set the number of constraints (n) and variables (m)
   - Click "Update Size" to adjust the input tables
   - Fill in the coefficients in Matrix A (constraints)
   - Fill in the right-hand side values in Vector b
   - Fill in the objective function coefficients in Vector c
   - Click "Solve" to get the solution

   b. Import from File:
   - Prepare a text file with the following format:
     ```
     n m
     a11 a12 ... a1m
     a21 a22 ... a2m
     ...
     an1 an2 ... anm
     b1 b2 ... bn
     c1 c2 ... cm
     ```
   - Click "Import from File" and select your file

## Example

For the problem:
```
Maximize: x + 6y - 3z
Subject to:
x + y - 3z ≤ 10
-5x + 10y ≤ 50
3x - 2y - 4z ≤ 9
```

The input file would be:
```
3 3
1 1 -3
-5 10 0
3 -2 -4
10 50 9
1 6 -3
```

## Features

- Supports both Simplex and Two-Phase Simplex methods
- Interactive table input
- File import capability
- Clear solution display
- Error handling for invalid inputs 