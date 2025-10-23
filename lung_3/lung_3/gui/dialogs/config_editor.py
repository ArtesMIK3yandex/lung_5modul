"""
Редактор конфигурации для администратора
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTabWidget, QWidget, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QInputDialog, QLabel)
from PyQt5.QtCore import Qt


class ConfigEditorDialog(QDialog):
    """Редактор конфигурации для администратора"""
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки администратора")
        self.setModal(True)
        self.config_manager = config_manager
        
        self._setup_ui()
        self.resize(700, 500)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        tabs = QTabWidget()
        
        processing_tab = self._create_processing_modes_tab()
        tabs.addTab(processing_tab, "Режимы обработки")
        
        modules_tab = self._create_modules_tab()
        tabs.addTab(modules_tab, "Модули")
        
        layout_tab = self._create_layout_tab()
        tabs.addTab(layout_tab, "Компоновка")
        
        layout.addWidget(tabs)
        
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self._on_save)
        buttons_layout.addWidget(save_btn)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
    
    def _create_processing_modes_tab(self):
        """Вкладка управления режимами обработки"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.modes_table = QTableWidget()
        self.modes_table.setColumnCount(3)
        self.modes_table.setHorizontalHeaderLabels(["ID", "Название", "Параметры"])
        self.modes_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self._load_processing_modes()
        
        layout.addWidget(self.modes_table)
        
        buttons_layout = QHBoxLayout()
        
        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self._on_add_mode)
        buttons_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self._on_edit_mode)
        buttons_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self._on_delete_mode)
        buttons_layout.addWidget(delete_btn)
        
        layout.addLayout(buttons_layout)
        
        return widget
    
    def _load_processing_modes(self):
        """Загружает режимы обработки в таблицу"""
        modes = self.config_manager.get_processing_modes()
        self.modes_table.setRowCount(len(modes))
        
        for i, mode in enumerate(modes):
            self.modes_table.setItem(i, 0, QTableWidgetItem(mode['id']))
            self.modes_table.setItem(i, 1, QTableWidgetItem(mode['name']))
            self.modes_table.setItem(i, 2, QTableWidgetItem(str(mode['parameters'])))
    
    def _create_modules_tab(self):
        """Вкладка управления модулями"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.modules_table = QTableWidget()
        self.modules_table.setColumnCount(4)
        self.modules_table.setHorizontalHeaderLabels(["ID", "Название", "Видимость", "Порядок"])
        self.modules_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self._load_modules()
        
        layout.addWidget(self.modules_table)
        
        return widget
    
    def _load_modules(self):
        """Загружает модули в таблицу"""
        modules = self.config_manager.get_modules()
        self.modules_table.setRowCount(len(modules))
        
        for i, (module_id, config) in enumerate(modules.items()):
            self.modules_table.setItem(i, 0, QTableWidgetItem(module_id))
            self.modules_table.setItem(i, 1, QTableWidgetItem(config['name']))
            
            visible_item = QTableWidgetItem("Да" if config['visible'] else "Нет")
            self.modules_table.setItem(i, 2, visible_item)
            
            self.modules_table.setItem(i, 3, QTableWidgetItem(str(config['order'])))
    
    def _create_layout_tab(self):
        """Вкладка управления компоновкой"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        info_label = QLabel("Настройка порядка элементов интерфейса")
        layout.addWidget(info_label)
        
        placeholder = QLabel("Функционал в разработке")
        placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(placeholder)
        
        return widget
    
    def _on_add_mode(self):
        """Добавление нового режима"""
        name, ok = QInputDialog.getText(self, "Новый режим", "Введите название:")
        if ok and name:
            mode_id = self.config_manager.add_processing_mode(name, {})
            QMessageBox.information(self, "Успех", f"Режим '{name}' добавлен")
            self._load_processing_modes()
    
    def _on_edit_mode(self):
        """Редактирование режима"""
        current_row = self.modes_table.currentRow()
        if current_row >= 0:
            QMessageBox.information(self, "Информация", "Функция редактирования в разработке")
    
    def _on_delete_mode(self):
        """Удаление режима"""
        current_row = self.modes_table.currentRow()
        if current_row >= 0:
            mode_id = self.modes_table.item(current_row, 0).text()
            
            reply = QMessageBox.question(
                self, "Подтверждение", 
                f"Удалить режим '{mode_id}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.config_manager.delete_processing_mode(mode_id)
                self._load_processing_modes()
    
    def _on_save(self):
        """Сохранение изменений"""
        self.config_manager.save()
        QMessageBox.information(self, "Успех", "Конфигурация сохранена")