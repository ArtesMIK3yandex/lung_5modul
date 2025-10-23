"""
Диалог выбора серии DICOM
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QListWidget, QPushButton)


class SeriesSelectorDialog(QDialog):
    """Диалог выбора серии DICOM"""
    
    def __init__(self, series_list: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор серии DICOM")
        self.setModal(True)
        self.series_list = series_list
        self.selected_uid = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        info_label = QLabel("Найдено несколько серий. Выберите серию для загрузки:")
        layout.addWidget(info_label)
        
        self.series_listwidget = QListWidget()
        for uid, description in self.series_list:
            self.series_listwidget.addItem(description)
        
        if self.series_list:
            self.series_listwidget.setCurrentRow(0)
        
        self.series_listwidget.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.series_listwidget)
        
        buttons_layout = QHBoxLayout()
        
        ok_btn = QPushButton("Загрузить")
        ok_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        self.resize(500, 300)
    
    def get_selected_series(self) -> str:
        """Возвращает UID выбранной серии"""
        current_row = self.series_listwidget.currentRow()
        if 0 <= current_row < len(self.series_list):
            return self.series_list[current_row][0]
        return None