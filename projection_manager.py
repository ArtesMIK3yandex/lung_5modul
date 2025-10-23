"""
Менеджер окон проекций - динамическая система отображения срезов.
С слайдерами и Zoom/Pan для каждой проекции.
"""

from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout, QSlider
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QPixmap, QImage, QPainter, QTransform, QWheelEvent, QMouseEvent
import numpy as np


class ProjectionView(QWidget):
    """Виджет отображения одной проекции"""
    
    slice_changed = pyqtSignal(int)
    
    def __init__(self, orientation: str, parent=None):
        super().__init__(parent)
        self.orientation = orientation
        self.current_slice = 0
        self.max_slices = 0
        self.image_data = None
        
        # Window/Level
        self.window_center = 40
        self.window_width = 400
        
        # Zoom & Pan
        self.zoom_factor = 1.0
        self.pan_offset = QPoint(0, 0)
        self.last_mouse_pos = None
        self.is_panning = False
        
        self._setup_ui()
        self.setMouseTracking(True)
    
    def _setup_ui(self):
        """Настройка UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        
        # Заголовок
        self.title_label = QLabel(self.orientation.upper())
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-weight: bold; background: #333; color: white; padding: 2px;")
        layout.addWidget(self.title_label)
        
        # Область отображения
        self.image_label = QLabel()
        self.image_label.setMinimumSize(200, 200)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("QLabel { background-color: black; border: 1px solid #555; }")
        self.image_label.setText(f"Нет данных")
        layout.addWidget(self.image_label)
        
        # Слайдер
        self.slice_slider = QSlider(Qt.Horizontal)
        self.slice_slider.setMinimum(0)
        self.slice_slider.setMaximum(0)
        self.slice_slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self.slice_slider)
        
        # Информация о срезе
        self.info_label = QLabel("Срез: 0 / 0")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("font-size: 10px; color: #888;")
        layout.addWidget(self.info_label)
    
    def set_data(self, volume: np.ndarray):
        """Устанавливает 3D-объем для отображения"""
        self.image_data = volume
        
        if self.orientation == 'axial':
            self.max_slices = volume.shape[0]
            self.current_slice = volume.shape[0] // 2
        elif self.orientation == 'sagittal':
            self.max_slices = volume.shape[2]
            self.current_slice = volume.shape[2] // 2
        elif self.orientation == 'coronal':
            self.max_slices = volume.shape[1]
            self.current_slice = volume.shape[1] // 2
        
        self.slice_slider.setMaximum(self.max_slices - 1)
        self.slice_slider.setValue(self.current_slice)
        self.update_display()
    
    def get_current_slice_data(self) -> np.ndarray:
        """Возвращает текущий срез"""
        if self.image_data is None:
            return None
        
        try:
            if self.orientation == 'axial':
                return self.image_data[self.current_slice, :, :]
            elif self.orientation == 'sagittal':
                return self.image_data[:, :, self.current_slice]
            elif self.orientation == 'coronal':
                return self.image_data[:, self.current_slice, :]
        except IndexError:
            return None
    
    def set_slice(self, slice_idx: int):
        """Устанавливает текущий срез"""
        if 0 <= slice_idx < self.max_slices:
            self.current_slice = slice_idx
            self.slice_slider.setValue(slice_idx)
            self.update_display()
    
    def _on_slider_changed(self, value):
        """Обработка изменения слайдера"""
        self.current_slice = value
        self.update_display()
        self.slice_changed.emit(value)
    
    def set_window_level(self, center: int, width: int):
        """Устанавливает Window/Level"""
        self.window_center = center
        self.window_width = width
        self.update_display()
    
    def update_display(self):
        """Обновляет отображение"""
        slice_data = self.get_current_slice_data()
        
        if slice_data is None:
            return
        
        # Применяем Window/Level
        img_normalized = self._apply_window_level(slice_data)
        
        # Конвертируем в QPixmap
        height, width = img_normalized.shape
        bytes_per_line = width
        q_img = QImage(img_normalized.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        
        pixmap = QPixmap.fromImage(q_img)
        
        # Применяем zoom
        if self.zoom_factor != 1.0:
            transform = QTransform()
            transform.scale(self.zoom_factor, self.zoom_factor)
            pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
        
        self.image_label.setPixmap(pixmap)
        
        # Обновляем инфо
        self.info_label.setText(f"Срез: {self.current_slice + 1} / {self.max_slices}")
    
    def _apply_window_level(self, data: np.ndarray) -> np.ndarray:
        """Применяет Window/Level к данным"""
        min_val = self.window_center - self.window_width / 2
        max_val = self.window_center + self.window_width / 2
        
        windowed = np.clip(data, min_val, max_val)
        normalized = ((windowed - min_val) / (max_val - min_val) * 255).astype(np.uint8)
        
        return normalized
    
    def wheelEvent(self, event: QWheelEvent):
        """Прокрутка колесом: Ctrl - zoom, без Ctrl - смена среза"""
        if event.modifiers() & Qt.ControlModifier:
            # Zoom
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_factor *= 1.1
            else:
                self.zoom_factor /= 1.1
            
            self.zoom_factor = max(0.1, min(10.0, self.zoom_factor))
            self.update_display()
        else:
            # Смена среза
            delta = event.angleDelta().y()
            if delta > 0:
                self.set_slice(self.current_slice + 1)
            else:
                self.set_slice(self.current_slice - 1)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Начало панорамирования"""
        if event.button() == Qt.LeftButton:
            self.is_panning = True
            self.last_mouse_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Панорамирование"""
        if self.is_panning and self.last_mouse_pos:
            delta = event.pos() - self.last_mouse_pos
            self.pan_offset += delta
            self.last_mouse_pos = event.pos()
            # TODO: реализовать отрисовку со смещением
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Конец панорамирования"""
        if event.button() == Qt.LeftButton:
            self.is_panning = False
            self.setCursor(Qt.ArrowCursor)
    
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Двойной клик - сброс zoom"""
        if event.button() == Qt.LeftButton:
            self.zoom_factor = 1.0
            self.pan_offset = QPoint(0, 0)
            self.update_display()
    
    def resizeEvent(self, event):
        """Обновляем отображение при изменении размера"""
        super().resizeEvent(event)
        if self.image_label.pixmap():
            self.update_display()


class ProjectionManager(QWidget):
    """
    Менеджер окон проекций.
    Динамическая компоновка - легко добавлять/удалять проекции.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dicom_loader = None
        self.projections = {}
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Настройка UI"""
        layout = QGridLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Создаем 3 стандартные проекции
        self._create_projection('axial', 0, 0)
        self._create_projection('sagittal', 0, 1)
        self._create_projection('coronal', 1, 0)
        
        # Резервное место для 4-й проекции
        placeholder = QLabel("Резерв для\n3D / 4-й проекции")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                color: #666;
                border: 2px dashed #444;
            }
        """)
        layout.addWidget(placeholder, 1, 1)
    
    def _create_projection(self, orientation: str, row: int, col: int):
        """Создает виджет проекции"""
        projection = ProjectionView(orientation, self)
        self.projections[orientation] = projection
        self.layout().addWidget(projection, row, col)
    
    def set_dicom_loader(self, loader):
        """Устанавливает загрузчик DICOM"""
        self.dicom_loader = loader
    
    def update_views(self):
        """Обновляет все проекции с новыми данными"""
        if self.dicom_loader is None or self.dicom_loader.get_volume() is None:
            return
        
        volume = self.dicom_loader.get_volume()
        
        for projection in self.projections.values():
            projection.set_data(volume)
    
    def set_window_level(self, center: int, width: int):
        """Устанавливает Window/Level для всех проекций"""
        for projection in self.projections.values():
            projection.set_window_level(center, width)
    
    def add_projection(self, orientation: str, row: int, col: int):
        """Добавляет новую проекцию"""
        if orientation not in self.projections:
            self._create_projection(orientation, row, col)
    
    def remove_projection(self, orientation: str):
        """Удаляет проекцию"""
        if orientation in self.projections:
            projection = self.projections.pop(orientation)
            self.layout().removeWidget(projection)
            projection.deleteLater()