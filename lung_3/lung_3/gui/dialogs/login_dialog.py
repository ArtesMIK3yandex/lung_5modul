"""
Диалог входа администратора
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton)


class LoginDialog(QDialog):
    """Диалог входа администратора"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Вход администратора")
        self.setModal(True)
        self.password = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        info_label = QLabel("Введите пароль администратора:")
        layout.addWidget(info_label)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self.accept)
        layout.addWidget(self.password_input)
        
        buttons_layout = QHBoxLayout()
        
        ok_btn = QPushButton("Войти")
        ok_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setFixedWidth(300)
    
    def get_password(self) -> str:
        """Возвращает введенный пароль"""
        return self.password_input.text()