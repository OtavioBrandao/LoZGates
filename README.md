# LoZ Gates: Educational Logic Tool

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2.0-blue)
![Pygame](https://img.shields.io/badge/Pygame-2.5.2-green)
![Pillow](https://img.shields.io/badge/Pillow-10.0-orange)

A desktop application developed to assist in the study of Propositional Logic, Boolean Algebra, and Digital Circuits. The tool offers a user-friendly graphical interface where users can input logical expressions and visualize their representations, simplifications, and properties in an interactive way.

## 📜 Table of Contents

- [Overview](#-overview)
- [Main Features](#-main-features)
- [Technologies Used](#-technologies-used)
- [How to Run the Project](#-how-to-run-the-project)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Execution](#execution)
- [Project Structure](#-project-structure)
- [Authors](#-authors)
- [Acknowledgments](#-acknowledgments)

## 🖼️ Overview

"LoZ Gates" was created as a learning support tool, allowing students to practice and better understand the concepts that connect mathematical logic and digital electronics.

## ✨ Main Features

-   **Logic Circuit Visualization:** Generates and displays the digital circuit corresponding to a propositional logic expression.
-   **Truth Table:** Creates the complete truth table for any expression, identifying whether it's a tautology, contradiction, or contingency.
-   **Expression Simplification:** Simplifies logical expressions step by step, showing the equivalence laws (De Morgan, Distributive, etc.) applied at each stage.
-   **Equivalence Verification:** Compares two logical expressions and determines if they are equivalent.
-   **Boolean Algebra Conversion:** Converts expressions from propositional logic (with symbols like `&`, `|`, `!`) to Boolean Algebra format (`*`, `+`, `~`).
-   **Intuitive Graphical Interface:** All functionalities are accessible through a modern and easy-to-use interface.
-   **AI Help:** One-click integration to send the expression to an AI (like ChatGPT) for detailed explanations.

## 🛠️ Technologies Used

-   **Python:** Main programming language of the project.
-   **CustomTkinter:** Library for creating modern graphical interfaces.
-   **Pygame:** Used to draw and dynamically render logic circuits.
-   **Pillow (PIL):** Used for image manipulation, such as saving generated circuits and creating icons.

## 🚀 How to Run the Project

Follow the steps below to run the application on your local machine.

### Prerequisites

-   Python 3.8 or higher
-   `pip` (Python package manager)

### Installation

To install the necessary dependencies, use the following command:

```bash
pip install -r requirements.txt
```

### Execution

To start the application, run the main interface file:

```bash
python main.py
```

## 📁 Project Structure

```
LoZ-Gates/
├── main.py                 # Main application file
├── requirements.txt        # Project dependencies
├── assets/                 # Images and icons
├── modules/               # Core logic modules
│   ├── circuit_generator.py
│   ├── truth_table.py
│   └── expression_parser.py
└── gui/                   # Interface components
    ├── main_window.py
    └── dialogs.py
```

## 👨‍💻 Authors

**Larissa de Souza**

**Otávio Menezes**

**Zilderlan Santos**

**David Oliveira**

## 🙏 Acknowledgments

Special thanks to Professor Dr. Evandro de Barros Costa and the Federal University of Alagoas (UFAL) - Institute of Computing, for their support and guidance during the development of this project.

---

<div align="center">

**📚 Educational Tool | 🎓 UFAL | 💻 Open Source**

*Bridging the gap between theoretical logic and practical digital circuits*

</div>