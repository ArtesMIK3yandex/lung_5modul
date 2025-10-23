"""
Точка входа в приложение lung1122
Medical Imaging Viewer с ролевой моделью User/Admin
"""

import sys
from pathlib import Path

# Добавить текущую директорию в sys.path
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from gui.main_window import MainWindow


def main():
    """Главная функция запуска приложения"""
    
    # Создание приложения
    app = QApplication(sys.argv)
    app.setApplicationName("lung1122")
    app.setOrganizationName("Medical Imaging")
    
    # Применение стиля (опционально)
    app.setStyle("Fusion")
    
    # Создание главного окна
    main_window = MainWindow()
    main_window.show()
    
    # Запуск event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()