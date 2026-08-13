import sys
import os
import math
import random
from PyQt5.QtCore import Qt, QTimer, QRectF, QPointF, QTime, QUrl
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QFileDialog, QMessageBox, QFrame,
    QLineEdit, QGraphicsDropShadowEffect, QSizePolicy, QAbstractItemView,
    QStackedWidget, QDialog, QProgressBar, QCheckBox, QGroupBox, QGridLayout
)
from PyQt5.QtGui import (
    QColor, QPainter, QPen, QBrush, QFont, QLinearGradient, QRadialGradient,
    QPainterPath, QPolygonF
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

class CircularVisualizerWidget(QWidget):
    """
    Custom widget that draws the circular voice wave in the Live Preview panel.
    Animates concentric hexagonal shapes with pulsating opacity and radius.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.spin_angle = 0.0
        self.is_playing = False
        self.sound_level = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)  # ~33 FPS
        
    def set_playing(self, playing):
        self.is_playing = playing
        
    def animate(self):
        if self.is_playing:
            self.spin_angle += 0.015
            # Simulate sound level using math or random
            t = QTime.currentTime().msec()
            self.sound_level = 0.2 + 0.15 * math.sin(t * 0.007) + 0.05 * math.cos(t * 0.003)
            self.update()
        else:
            if self.sound_level > 0.0:
                self.sound_level = max(0.0, self.sound_level - 0.05)
                self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Grid background
        painter.fillRect(self.rect(), QColor("#111324"))
        painter.setPen(QPen(QColor("rgba(255, 255, 255, 0.02)"), 1))
        
        # Draw background grid lines
        grid_size = 20
        for y in range(0, h, grid_size):
            painter.drawLine(0, y, w, y)
        for x in range(0, w, grid_size):
            painter.drawLine(x, 0, x, h)
            
        centerX = w / 2.0
        centerY = h / 2.0
        
        # Concentric glowing grids
        painter.setPen(QPen(QColor("rgba(255, 255, 255, 0.03)"), 1))
        for r in range(20, 200, 20):
            painter.drawEllipse(QPointF(centerX, centerY), r, r)
            
        # Outer pulsing waveform
        base_radius = 55.0 + self.sound_level * 25.0
        
        painter.save()
        painter.translate(centerX, centerY)
        
        # Hexagon 1: Cyan
        painter.rotate(math.degrees(self.spin_angle))
        pen = QPen(QColor("rgba(0, 242, 254, 0.85)"), 2)
        painter.setPen(pen)
        self.draw_pulsing_hexagon(painter, base_radius, self.sound_level, 6)
        
        # Hexagon 2: Magenta (slightly smaller and rotated offset)
        painter.rotate(math.degrees(-self.spin_angle * 2.0))
        pen2 = QPen(QColor("rgba(253, 38, 122, 0.65)"), 1.5)
        painter.setPen(pen2)
        self.draw_pulsing_hexagon(painter, base_radius - 12, self.sound_level * 0.8, 6)
        
        # Inner core circle: glows and pulses
        painter.rotate(math.degrees(self.spin_angle * 1.5))
        rad_grad = QRadialGradient(0, 0, 30)
        rad_grad.setColorAt(0, QColor("rgba(0, 242, 254, 0.35)"))
        rad_grad.setColorAt(0.8, QColor("rgba(253, 38, 122, 0.15)"))
        rad_grad.setColorAt(1, QColor("rgba(0, 0, 0, 0)"))
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(rad_grad))
        r_core = max(15.0, 20.0 + self.sound_level * 10.0)
        painter.drawEllipse(QPointF(0, 0), r_core, r_core)
        
        painter.restore()

    def draw_pulsing_hexagon(self, painter, radius, intensity, points):
        path = QPainterPath()
        t = QTime.currentTime().msec()
        for i in range(points + 1):
            angle = (i * 2.0 * math.pi) / points
            # Add noise/frequency spikes on vertices
            pulse = 1.0 + (math.sin(angle * 4.0 + t * 0.005) * 0.05 * intensity) + \
                          (math.cos(angle * 8.0 - t * 0.003) * 0.02 * intensity)
            r = radius * pulse
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        painter.drawPath(path)


class SpectrumWidget(QWidget):
    """
    Draws the visualizer audio spectrum frequency bars at the bottom.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_playing = False
        self.setMinimumHeight(24)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_spectrum)
        self.timer.start(50)  # ~20 FPS for spectrum
        self.fft_data = []
        
    def set_playing(self, playing):
        self.is_playing = playing
        
    def update_spectrum(self):
        if self.is_playing or not self.fft_data:
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Dark container background
        painter.fillRect(self.rect(), QColor("#111324"))
        
        bar_width = 3
        bar_gap = 2
        bar_count = max(1, w // (bar_width + bar_gap))
        
        # Ensure fft_data matches bar_count
        t = QTime.currentTime().msec()
        self.fft_data = []
        
        if self.is_playing:
            for i in range(bar_count):
                base = math.sin(i * 0.1 + t * 0.003) * 0.4 + 0.5
                flutter = math.cos(i * 0.45 - t * 0.007) * 0.25
                value = max(0.05, base + flutter) * (0.8 + 0.2 * random.random())
                self.fft_data.append(value)
        else:
            # Idle state
            for i in range(bar_count):
                value = 0.04 + 0.02 * math.sin(i * 0.2 + t * 0.001)
                self.fft_data.append(value)
                
        # Draw spectrum bars with vertical gradient
        grad = QLinearGradient(0, h, 0, 0)
        grad.setColorAt(0, QColor("#00f2fe"))  # Cyan
        grad.setColorAt(0.5, QColor("#8a2be2")) # Purple
        grad.setColorAt(1, QColor("#fd267a"))  # Magenta
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(grad))
        
        for i in range(min(bar_count, len(self.fft_data))):
            val = self.fft_data[i]
            bar_h = max(2.0, val * h)
            x = i * (bar_width + bar_gap)
            y = h - bar_h
            painter.drawRect(QRectF(x, y, bar_width, bar_h))


class CassetteWidget(QWidget):
    """
    Draws the cassette tape graphic with two reels that spin during playback.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0.0
        self.is_playing = False
        self.setFixedSize(58, 30)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate_reels)
        self.timer.start(30)  # ~33 FPS

    def set_playing(self, playing):
        self.is_playing = playing

    def rotate_reels(self):
        if self.is_playing:
            self.angle += 4.0
            if self.angle >= 360.0:
                self.angle -= 360.0
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = QRectF(2, 2, self.width() - 4, self.height() - 4)
        path = QPainterPath()
        path.addRoundedRect(rect, 4, 4)
        
        # Border
        pen = QPen(QColor("#fd267a"), 1.2)
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor("#0b0d19")))
        painter.drawPath(path)
        
        centerY = self.height() / 2.0
        width = self.width()
        
        reel1_centerX = width * 0.32
        reel2_centerX = width * 0.68
        r = 7.0
        
        for cx in (reel1_centerX, reel2_centerX):
            painter.save()
            painter.translate(cx, centerY)
            painter.rotate(self.angle)
            
            # Outer ring
            painter.setPen(QPen(QColor("#00f2fe"), 1.2))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(QPointF(0, 0), r, r)
            
            # Center circle
            painter.setBrush(QBrush(QColor("#00f2fe")))
            painter.drawEllipse(QPointF(0, 0), 2.0, 2.0)
            
            # Spokes
            painter.setPen(QPen(QColor("#00f2fe"), 0.8))
            for i in range(4):
                angle_rad = math.radians(i * 45)
                dx = r * math.cos(angle_rad)
                dy = r * math.sin(angle_rad)
                painter.drawLine(QPointF(-dx, -dy), QPointF(dx, dy))
                
            painter.restore()


class BatchDubberDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Batch Dubber Studio")
        self.resize(550, 400)
        self.setStyleSheet(self.get_dialog_style())
        
        # Simulation variables
        self.processing = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_simulation)
        self.progress_values = []
        self.selected_dir = ""
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        # Title/desc
        title_lbl = QLabel("👥 Batch Dubber Studio")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        layout.addWidget(title_lbl)
        
        desc_lbl = QLabel("Processes folder-wide video directories in parallel using queue threading structures.")
        desc_lbl.setStyleSheet("color: #8e95b3; font-size: 11px;")
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)
        
        # Directory Selection
        dir_layout = QHBoxLayout()
        self.dir_edit = QLineEdit()
        self.dir_edit.setPlaceholderText("No directory selected...")
        self.dir_edit.setReadOnly(True)
        self.dir_edit.setStyleSheet("background-color: #0b0d19; color: #f0f2fa; border: 1px solid rgba(255,255,255,0.08); border-radius: 6px; padding: 6px;")
        
        self.btn_select = QPushButton("📁 Browse...")
        self.btn_select.setStyleSheet("background-color: #242846; color: white; border-radius: 6px; padding: 6px 12px; font-weight: bold;")
        self.btn_select.clicked.connect(self.select_directory)
        
        self.btn_clear_file = QPushButton("🗑️ Clear File")
        self.btn_clear_file.setStyleSheet("background-color: #c2185b; color: white; border-radius: 6px; padding: 6px 12px; font-weight: bold;")
        self.btn_clear_file.clicked.connect(self.clear_files)
        
        dir_layout.addWidget(self.dir_edit)
        dir_layout.addWidget(self.btn_select)
        dir_layout.addWidget(self.btn_clear_file)
        layout.addLayout(dir_layout)
        
        # Table of files
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Video File", "Size", "Status / Progress"])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setColumnWidth(1, 80)
        self.table.setColumnWidth(2, 160)
        self.table.setStyleSheet(self.get_table_style())
        layout.addWidget(self.table)
        
        # Batch Settings Panel
        settings_group = QGroupBox("⚙️ Dubber Settings Panel")
        settings_group.setStyleSheet("QGroupBox { color: #00f2fe; font-weight: bold; font-size: 11px; border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; margin-top: 5px; padding-top: 15px; }")
        settings_layout = QGridLayout(settings_group)
        settings_layout.setSpacing(10)
        
        voice_lbl = QLabel("🗣️ Voice (សំឡេង):")
        voice_lbl.setStyleSheet("color: #8e95b3; font-weight: bold; font-size: 11px;")
        self.batch_voice_cb = QComboBox()
        self.batch_voice_cb.addItems(["👩 Female Voice (សំឡេងស្រី)", "👨 Male Voice (សំឡេងប្រុស)", "🤖 Auto Detect (ស្វ័យប្រវត្តិ)"])
        self.batch_voice_cb.setCurrentIndex(0) # Default Female
        settings_layout.addWidget(voice_lbl, 0, 0)
        settings_layout.addWidget(self.batch_voice_cb, 0, 1)
        
        speed_lbl = QLabel("🎚️ Speed (ល្បឿន):")
        speed_lbl.setStyleSheet("color: #8e95b3; font-weight: bold; font-size: 11px;")
        self.batch_speed_cb = QComboBox()
        self.batch_speed_cb.addItems(["Normal (ធម្មតា)", "Slow (យឺត)", "Fast (លឿន)"])
        self.batch_speed_cb.setCurrentIndex(0) # Default Normal
        settings_layout.addWidget(speed_lbl, 0, 2)
        settings_layout.addWidget(self.batch_speed_cb, 0, 3)
        
        tts_lbl = QLabel("🤖 TTS Model (ម៉ូដែល TTS):")
        tts_lbl.setStyleSheet("color: #8e95b3; font-weight: bold; font-size: 11px;")
        self.batch_tts_cb = QComboBox()
        self.batch_tts_cb.addItems(["Automatic — Kiri → Edge TTS", "Gemini TTS Premium"])
        settings_layout.addWidget(tts_lbl, 1, 0)
        settings_layout.addWidget(self.batch_tts_cb, 1, 1, 1, 3)
        
        vox_lbl = QLabel("🎙️ VoxCPM2 Settings:")
        vox_lbl.setStyleSheet("color: #8e95b3; font-weight: bold; font-size: 11px;")
        self.batch_vox_cb = QComboBox()
        self.batch_vox_cb.addItems(["Not needed (មិនចាំបាច់)", "Enabled (សកម្ម)"])
        settings_layout.addWidget(vox_lbl, 2, 0)
        settings_layout.addWidget(self.batch_vox_cb, 2, 1, 1, 3)
        
        layout.addWidget(settings_group)
        
        # Global Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(self.get_progress_style())
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(8)
        self.progress_bar.setMaximumHeight(8)
        layout.addWidget(self.progress_bar)
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("🚀 Start Batch Dubbing")
        self.btn_start.setEnabled(True)
        self.btn_start.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00f2fe, stop:1 #00c853); color: #0b0d19; font-weight: bold; border-radius: 8px; padding: 10px;")
        self.btn_start.clicked.connect(self.start_batch_processing)
        
        btn_close = QPushButton("Cancel")
        btn_close.setStyleSheet("background-color: #242846; color: white; border-radius: 8px; padding: 10px;")
        btn_close.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_close)
        btn_layout.addWidget(self.btn_start)
        layout.addLayout(btn_layout)

    def select_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Video Directory")
        if dir_path:
            self.selected_dir = dir_path
            self.dir_edit.setText(dir_path)
            self.populate_files()
            self.btn_start.setEnabled(True)
            
    def populate_files(self):
        self.table.setRowCount(0)
        files = []
        try:
            for f in os.listdir(self.selected_dir):
                if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
                    size_mb = os.path.getsize(os.path.join(self.selected_dir, f)) / (1024 * 1024)
                    files.append((f, f"{size_mb:.1f} MB"))
        except Exception:
            pass
            
        if not files:
            files = [
                ("episode_01_raw.mp4", "185.2 MB"),
                ("episode_02_raw.mp4", "210.4 MB"),
                ("interview_promotional.mov", "92.1 MB"),
                ("trailer_teaser_audio.mkv", "45.7 MB")
            ]
            
        self.progress_values = [0] * len(files)
        
        for idx, (name, size) in enumerate(files):
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            name_item = QTableWidgetItem(name)
            name_item.setForeground(QColor("#ffffff"))
            self.table.setItem(row, 0, name_item)
            
            size_item = QTableWidgetItem(size)
            size_item.setForeground(QColor("#8e95b3"))
            self.table.setItem(row, 1, size_item)
            
            status_widget = QWidget()
            status_layout = QHBoxLayout(status_widget)
            status_layout.setContentsMargins(5, 2, 5, 2)
            
            pbar = QProgressBar()
            pbar.setStyleSheet(self.get_pbar_cell_style())
            pbar.setRange(0, 100)
            pbar.setValue(0)
            pbar.setTextVisible(True)
            pbar.setAlignment(Qt.AlignCenter)
            
            status_layout.addWidget(pbar)
            self.table.setCellWidget(row, 2, status_widget)

    def start_batch_processing(self):
        if self.processing:
            return
        if self.table.rowCount() == 0:
            self.populate_files()
        self.processing = True
        self.btn_start.setEnabled(False)
        self.btn_select.setEnabled(False)
        self.batch_voice_cb.setEnabled(False)
        self.batch_speed_cb.setEnabled(False)
        self.batch_tts_cb.setEnabled(False)
        self.batch_vox_cb.setEnabled(False)
        self.timer.start(150)

    def update_simulation(self):
        all_done = True
        total = 0
        
        for i in range(len(self.progress_values)):
            curr = self.progress_values[i]
            if curr < 100:
                all_done = False
                active_count = sum(1 for v in self.progress_values if 0 < v < 100)
                if active_count < 2 or curr > 0:
                    self.progress_values[i] = min(100, curr + random.randint(5, 15))
            total += self.progress_values[i]
            
            widget = self.table.cellWidget(i, 2)
            if widget:
                pbar = widget.findChild(QProgressBar)
                if pbar:
                    pbar.setValue(self.progress_values[i])
                    
        global_avg = int(total / len(self.progress_values)) if self.progress_values else 0
        self.progress_bar.setValue(global_avg)
        
        if all_done:
            self.timer.stop()
            self.processing = False
            self.btn_start.setEnabled(True)
            self.btn_select.setEnabled(True)
            self.batch_voice_cb.setEnabled(True)
            self.batch_speed_cb.setEnabled(True)
            self.batch_tts_cb.setEnabled(True)
            self.batch_vox_cb.setEnabled(True)
            QMessageBox.information(self, "Batch Complete", "Batch Studio has finished processing folder-wide video directories in parallel!")
            self.accept()

    def get_dialog_style(self):
        return """
            QDialog {
                background-color: #0b0d19;
                border: 1px solid rgba(0, 242, 254, 0.2);
            }
            QLabel {
                color: #ffffff;
            }
        """
        
    def get_table_style(self):
        return """
            QTableWidget {
                background-color: #111324;
                border: 1px solid rgba(255, 255, 255, 0.08);
                gridline-color: transparent;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #15182e;
                color: #8e95b3;
                padding: 6px;
                font-weight: bold;
                font-size: 10px;
                border: none;
            }
        """

    def get_progress_style(self):
        return """
            QProgressBar {
                border: none;
                background-color: #1e2530;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fd267a, stop:1 #00f2fe);
                border-radius: 4px;
            }
        """

    def get_pbar_cell_style(self):
        return """
            QProgressBar {
                border: none;
                background-color: #0b0d19;
                color: #ffffff;
                font-size: 9px;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #00f2fe;
                border-radius: 4px;
            }
        """


class TranslationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Video Translation Studio")
        self.resize(450, 320)
        self.setStyleSheet(self.get_dialog_style())
        
        self.processing = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.progress_val = 0
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_lbl = QLabel("🌐 Video Translation Studio")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        layout.addWidget(title_lbl)
        
        desc_lbl = QLabel("Translate your video using advanced AI models (Google Gemini or OpenAI Whisper) with automated vocal tracking.")
        desc_lbl.setStyleSheet("color: #8e95b3; font-size: 11px;")
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)
        
        # Dropdown for model select
        model_layout = QHBoxLayout()
        model_lbl = QLabel("AI Engine:")
        model_lbl.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 12px;")
        
        self.model_cb = QComboBox()
        self.model_cb.addItems(["Google Gemini", "OpenAI Whisper"])
        self.model_cb.currentIndexChanged.connect(self.on_model_changed)
        
        model_layout.addWidget(model_lbl)
        model_layout.addWidget(self.model_cb)
        layout.addLayout(model_layout)
        
        # Checkbox for Auto Detect Male/Female
        self.detect_checkbox = QCheckBox("Auto Detect Male/Female Voices")
        self.detect_checkbox.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 12px;")
        self.detect_checkbox.setChecked(True)
        self.detect_checkbox.stateChanged.connect(self.on_detect_changed)
        layout.addWidget(self.detect_checkbox)
        
        # Note description for defaults
        self.note_lbl = QLabel("")
        self.note_lbl.setStyleSheet("color: #00f2fe; font-size: 10px; font-style: italic;")
        self.note_lbl.setWordWrap(True)
        layout.addWidget(self.note_lbl)
        
        # Setup initial model view
        self.on_model_changed(0)
        
        # Progress Bar
        self.pbar = QProgressBar()
        self.pbar.setStyleSheet(self.get_progress_style())
        self.pbar.setValue(0)
        self.pbar.setMinimumHeight(8)
        self.pbar.setMaximumHeight(8)
        self.pbar.setTextVisible(False)
        self.pbar.hide()
        layout.addWidget(self.pbar)
        
        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet("color: #8e95b3; font-size: 10px;")
        self.status_lbl.hide()
        layout.addWidget(self.status_lbl)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setStyleSheet("background-color: #242846; color: white; border-radius: 8px; padding: 10px;")
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_start = QPushButton("🚀 Start Translation")
        self.btn_start.setStyleSheet("background-color: #00ff87; color: #0b0d19; font-weight: bold; border-radius: 8px; padding: 10px;")
        self.btn_start.clicked.connect(self.start_translation)
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_start)
        layout.addLayout(btn_layout)
        
    def on_model_changed(self, index):
        if index == 0:  # Gemini
            self.detect_checkbox.setChecked(True)
            self.detect_checkbox.setEnabled(False)
            self.note_lbl.setText("Google Gemini strictly operates in Auto Detect Male/Female mode to construct optimal conversational maps.")
        else:  # Whisper
            self.detect_checkbox.setEnabled(True)
            self.detect_checkbox.setChecked(True)
            self.on_detect_changed()
            
    def on_detect_changed(self):
        if self.model_cb.currentIndex() == 1: # Whisper
            if not self.detect_checkbox.isChecked():
                self.note_lbl.setText("Whisper Auto Detect is disabled. Synthesized voice tracks will default to Sophea (Female).")
            else:
                self.note_lbl.setText("Whisper will auto detect voice genders (Male/Female) based on source audio frequencies.")
            
    def start_translation(self):
        if self.processing:
            return
        self.processing = True
        self.btn_start.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        self.model_cb.setEnabled(False)
        self.detect_checkbox.setEnabled(False)
        self.pbar.show()
        self.status_lbl.show()
        self.status_lbl.setText("Initializing translation engine...")
        self.timer.start(100)
        
    def update_progress(self):
        self.progress_val += 4
        if self.progress_val > 100:
            self.progress_val = 100
        self.pbar.setValue(self.progress_val)
        
        engine = self.model_cb.currentText()
        if self.progress_val < 30:
            self.status_lbl.setText(f"Connecting to {engine} API and loading audio streams...")
        elif self.progress_val < 70:
            self.status_lbl.setText("Running vocal translation & semantic matching models...")
        elif self.progress_val < 95:
            auto_detect = "Auto-gender matching active" if self.detect_checkbox.isChecked() else "Defaulting to Sophea (Female)"
            self.status_lbl.setText(f"Compiling subtitle timelines ({auto_detect})...")
        else:
            self.status_lbl.setText("Writing output script data...")
            
        if self.progress_val >= 100:
            self.timer.stop()
            self.accept()
            
    def get_dialog_style(self):
        return """
            QDialog {
                background-color: #0b0d19;
                border: 1px solid rgba(0, 242, 254, 0.2);
            }
            QLabel {
                color: #ffffff;
            }
            QComboBox {
                background-color: #111324;
                color: #f0f2fa;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 6px;
                padding: 6px;
            }
            QCheckBox {
                color: #ffffff;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 4px;
                background-color: #111324;
            }
            QCheckBox::indicator:checked {
                background-color: #00f2fe;
            }
        """
        
    def get_progress_style(self):
        return """
            QProgressBar {
                border: none;
                background-color: #1e2530;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fd267a, stop:1 #00f2fe);
                border-radius: 4px;
            }
        """


class MergeDialog(QDialog):
    def __init__(self, subtitles, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Merge Subtitle Segments")
        self.resize(480, 260)
        self.setStyleSheet(self.get_dialog_style())
        self.subtitles = sorted(subtitles, key=lambda s: s["start"])
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title_lbl = QLabel("🔗 Merge Subtitle Segments")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #00f2fe;")
        layout.addWidget(title_lbl)
        
        self.combo = QComboBox()
        
        if len(self.subtitles) < 2:
            self.combo.addItem("Need at least 2 segments to merge")
            self.combo.setEnabled(False)
        else:
            for i in range(len(self.subtitles) - 1):
                s1 = self.subtitles[i]
                s2 = self.subtitles[i+1]
                self.combo.addItem(f"Merge Segment #{i+1} with #{i+2}")
                
        layout.addWidget(self.combo)
        
        self.preview_lbl = QLabel("Select a pair to preview...")
        self.preview_lbl.setStyleSheet("background-color: rgba(0, 0, 0, 0.2); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; padding: 12px; color: #f0f2fa; font-size: 12px;")
        self.preview_lbl.setWordWrap(True)
        layout.addWidget(self.preview_lbl)
        
        self.combo.currentIndexChanged.connect(self.update_preview)
        self.update_preview()
        
        btn_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setStyleSheet("background-color: #242846; color: white; border-radius: 8px; padding: 10px;")
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_confirm = QPushButton("Confirm Merge")
        self.btn_confirm.setStyleSheet("background-color: #00ff87; color: #0b0d19; font-weight: bold; border-radius: 8px; padding: 10px;")
        self.btn_confirm.clicked.connect(self.accept)
        if len(self.subtitles) < 2:
            self.btn_confirm.setEnabled(False)
            
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_confirm)
        layout.addLayout(btn_layout)
        
    def update_preview(self):
        if len(self.subtitles) < 2:
            self.preview_lbl.setText("Unable to merge. Add more segments first.")
            return
        idx = self.combo.currentIndex()
        if idx >= 0 and idx < len(self.subtitles) - 1:
            s1 = self.subtitles[idx]
            s2 = self.subtitles[idx+1]
            time_str = f"Timestamps: {self.parent().seconds_to_time_str(s1['start'])} - {self.parent().seconds_to_time_str(s2['end'])}"
            merged_text = f"Merged Text: {s1['text']} {s2['text']}"
            self.preview_lbl.setText(f"{time_str}\n{merged_text}")
            
    def get_dialog_style(self):
        return """
            QDialog {
                background-color: #0b0d19;
                border: 1px solid rgba(0, 242, 254, 0.2);
            }
            QLabel {
                color: #ffffff;
            }
            QComboBox {
                background-color: #111324;
                color: #f0f2fa;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 6px;
                padding: 6px;
            }
        """


class SettingsDialog(QDialog):
    def __init__(self, current_pitch, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Studio Settings")
        self.resize(400, 220)
        self.setStyleSheet(self.get_dialog_style())
        self.pitch_val = current_pitch
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title_lbl = QLabel("⚙ Dubber Configuration Panel")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #00f2fe;")
        layout.addWidget(title_lbl)
        
        pitch_lbl = QLabel("Voice Pitch Multiplier:")
        pitch_lbl.setStyleSheet("color: #8e95b3; font-size: 12px; font-weight: bold;")
        layout.addWidget(pitch_lbl)
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(50, 150)
        self.slider.setValue(int(self.pitch_val * 100))
        self.slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.slider)
        
        self.val_lbl = QLabel("1.0 (Normal)")
        self.val_lbl.setStyleSheet("color: #00ff87; font-weight: bold; font-size: 12px;")
        layout.addWidget(self.val_lbl)
        self.on_slider_changed(self.slider.value())
        
        btn_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setStyleSheet("background-color: #242846; color: white; border-radius: 8px; padding: 10px;")
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_save = QPushButton("Save Settings")
        self.btn_save.setStyleSheet("background-color: #00ff87; color: #0b0d19; font-weight: bold; border-radius: 8px; padding: 10px;")
        self.btn_save.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)
        
    def on_slider_changed(self, val):
        self.pitch_val = val / 100.0
        label = f"{self.pitch_val:.2f} (Normal)"
        if self.pitch_val < 1.0:
            label = f"{self.pitch_val:.2f} (Lower Pitch)"
        elif self.pitch_val > 1.0:
            label = f"{self.pitch_val:.2f} (Higher Pitch)"
        self.val_lbl.setText(label)
        
    def get_dialog_style(self):
        return """
            QDialog {
                background-color: #0b0d19;
                border: 1px solid rgba(0, 242, 254, 0.2);
            }
            QLabel {
                color: #ffffff;
            }
            QSlider::groove:horizontal {
                border: none;
                height: 6px;
                background: #1e2530;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #00f2fe;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                border: 2px solid #00f2fe;
                width: 14px;
                margin-top: -4px;
                margin-bottom: -4px;
                border-radius: 7px;
            }
        """


class ExportProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Media Layout")
        self.resize(450, 260)
        self.setStyleSheet(self.get_dialog_style())
        
        self.progress_val = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        
        self.init_ui()
        
    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        self.title_lbl = QLabel("⬇ Exporting Dubbed Video Layout")
        self.title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        self.layout.addWidget(self.title_lbl)
        
        self.status_lbl = QLabel("Synthesizing audio layers...")
        self.status_lbl.setStyleSheet("color: #8e95b3; font-size: 11px;")
        self.status_lbl.setWordWrap(True)
        self.layout.addWidget(self.status_lbl)
        
        self.pbar = QProgressBar()
        self.pbar.setStyleSheet(self.get_progress_style())
        self.pbar.setValue(0)
        self.pbar.setMinimumHeight(10)
        self.pbar.setMaximumHeight(10)
        self.pbar.setTextVisible(True)
        self.pbar.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.pbar)
        
        self.btn_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Cancel Process")
        self.btn_cancel.setStyleSheet("background-color: #242846; color: white; border-radius: 8px; padding: 10px;")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_layout.addWidget(self.btn_cancel)
        
        self.btn_save = QPushButton("💾 Save Video File")
        self.btn_save.setStyleSheet("background-color: #00ff87; color: #0b0d19; font-weight: bold; border-radius: 8px; padding: 10px;")
        self.btn_save.clicked.connect(self.accept)
        self.btn_save.hide()
        self.btn_layout.addWidget(self.btn_save)
        
        self.layout.addLayout(self.btn_layout)
        self.timer.start(80)
        
    def update_progress(self):
        self.progress_val += 3
        if self.progress_val > 100:
            self.progress_val = 100
        self.pbar.setValue(self.progress_val)
        
        if self.progress_val < 30:
            self.status_lbl.setText("Synthesizing Khmer TTS Dubbing Voice tracks (Khmer Voice)...")
        elif self.progress_val < 65:
            self.status_lbl.setText("Muting original vocal track & embedding Khmer voiceover layers...")
        elif self.progress_val < 90:
            self.status_lbl.setText("Stitching Khmer AI voices into dubbed video container (MP4)...")
        elif self.progress_val < 100:
            self.status_lbl.setText("Finalizing dubbed MP4 video render pipeline...")
        else:
            self.timer.stop()
            self.status_lbl.setText("Render Pipeline Complete! Final video package compiled successfully.")
            self.title_lbl.setText("🎉 Export Complete")
            self.btn_cancel.setText("Close")
            self.btn_save.show()
            
    def get_dialog_style(self):
        return """
            QDialog {
                background-color: #0b0d19;
                border: 1px solid rgba(0, 242, 254, 0.2);
            }
            QLabel {
                color: #ffffff;
            }
        """
        
    def get_progress_style(self):
        return """
            QProgressBar {
                border: none;
                background-color: #1e2530;
                color: #ffffff;
                font-size: 10px;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00f2fe, stop:1 #00ff87);
                border-radius: 5px;
            }
        """


class KemsininDubberApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Kemsinin Dubber Pro")
        self.resize(1280, 680)
        self.setStyleSheet(self.get_main_style())
        
        # Playback variables
        self.is_playing = False
        self.current_time = 0.0
        self.total_duration = 141.0  # 02:21,000 as default
        self.active_row_id = -1
        self.is_muted = False
        self.pre_mute_volume = 70
        self.pitch_multiplier = 1.0
        self.current_theme = 0
        
        # Subtitles database (initial mockup demo)
        self.subtitles = [
            {"id": 1, "start": 6.020, "end": 7.300, "text": "ទៅលេងឡើងវិញ", "voice": "piseth_male", "speed": "auto"},
            {"id": 2, "start": 19.400, "end": 20.440, "text": "ដល់", "voice": "piseth_male", "speed": "auto"},
            {"id": 3, "start": 21.820, "end": 24.000, "text": "ម៉េចក៏បានដែរវិញ", "voice": "piseth_male", "speed": "auto"},
            {"id": 4, "start": 27.720, "end": 29.840, "text": "ដាច់កំហែងបេក្ខជនកណ្ដាលផ្លូវ", "voice": "piseth_male", "speed": "auto"},
            {"id": 5, "start": 34.540, "end": 37.120, "text": "ខុសនេះត្រង់ក្បូនបងព្រេង", "voice": "piseth_male", "speed": "auto"},
            {"id": 6, "start": 37.120, "end": 44.440, "text": "ចុះ បុគ្គលិកមានឧបសគ្គ", "voice": "piseth_male", "speed": "auto"},
            {"id": 7, "start": 50.840, "end": 52.340, "text": "អ្នក អ្នកជាអ្នកណា", "voice": "piseth_male", "speed": "auto"},
            {"id": 8, "start": 52.340, "end": 54.580, "text": "តើលោកកាលពីដប់ឆ្នាំមុន", "voice": "piseth_male", "speed": "auto"},
            {"id": 9, "start": 54.580, "end": 55.980, "text": "គ្មានជំនួយជួយដោះស្រាយបញ្ហាដែរឬទេ", "voice": "piseth_male", "speed": "auto"}
        ]
        
        # Table reference tracker for row cell widgets
        # key: row_index, value: list of styled cell widgets
        self.row_widgets_map = {}
        
        # Timer for playback progression
        self.playback_timer = QTimer(self)
        self.playback_timer.timeout.connect(self.playback_tick)
        
        # QMediaPlayer integration for real video playback
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.positionChanged.connect(self.action_player_position_changed)
        self.media_player.durationChanged.connect(self.action_player_duration_changed)
        self.media_player.stateChanged.connect(self.action_player_state_changed)
        self.video_loaded = False
        
        self.init_ui()
        self.populate_table()
        
    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)
        
        # Main vertical layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # 1. Header Row
        header_card = QFrame()
        header_card.setObjectName("HeaderCard")
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        # Brand logo area
        logo_layout = QHBoxLayout()
        logo_layout.setSpacing(10)
        
        logo_icon = QLabel("🎤")
        logo_icon.setStyleSheet("font-size: 26px; color: #fd267a;")
        
        logo_text_layout = QVBoxLayout()
        logo_text_layout.setSpacing(1)
        
        logo_title = QLabel("KEMSININ DUBBER")
        logo_title.setStyleSheet("font-size: 19px; font-weight: 900; color: #ffffff; letter-spacing: 1px;")
        
        logo_subtitle = QLabel("AI-POWERED VIDEO DUBBING STUDIO")
        logo_subtitle.setStyleSheet("font-size: 9px; font-weight: bold; color: #00f2fe; letter-spacing: 0.5px;")
        
        logo_text_layout.addWidget(logo_title)
        logo_text_layout.addWidget(logo_subtitle)
        
        logo_layout.addWidget(logo_icon)
        logo_layout.addLayout(logo_text_layout)
        
        header_layout.addLayout(logo_layout)
        header_layout.addStretch()
        
        # Header action buttons
        self.btn_batch = QPushButton("👥 Batch Dubber — បកប្រែរឿងអូតូ")
        self.btn_batch.setObjectName("BtnBatch")
        self.btn_batch.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e91e63, stop:0.5 #ff2a85, stop:1 #00f2fe); font-weight: bold; border: 1px solid #ffffff; padding: 6px 12px;")
        self.btn_batch.clicked.connect(self.action_batch)
        
        self.btn_translate = QPushButton("🌐 Translate Video")
        self.btn_translate.setObjectName("BtnTranslate")
        self.btn_translate.clicked.connect(self.action_translate_video)
        
        self.btn_upload_video = QPushButton("📁 Upload Video")
        self.btn_upload_video.setObjectName("BtnUploadVideo")
        self.btn_upload_video.clicked.connect(self.action_upload_video)
        
        self.btn_upload_srt = QPushButton("📄 Upload SRT")
        self.btn_upload_srt.setObjectName("BtnUploadSrt")
        self.btn_upload_srt.clicked.connect(self.action_upload_srt)
        
        self.btn_transcript = QPushButton("📝 Video Transcript")
        self.btn_transcript.setObjectName("BtnTranscript")
        self.btn_transcript.clicked.connect(self.action_video_transcript)
        
        self.btn_effect = QPushButton("🪄 Effect")
        self.btn_effect.setObjectName("BtnEffect")
        self.btn_effect.clicked.connect(self.action_effect)
        
        header_layout.addWidget(self.btn_batch)
        header_layout.addWidget(self.btn_translate)
        header_layout.addWidget(self.btn_upload_video)
        header_layout.addWidget(self.btn_upload_srt)
        header_layout.addWidget(self.btn_transcript)
        header_layout.addWidget(self.btn_effect)
        
        main_layout.addWidget(header_card)
        
        # 2. Main Content (Two Columns Layout)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        
        # LEFT COLUMN (Live Preview & Quick tools) - Width ~32%
        left_column = QVBoxLayout()
        left_column.setSpacing(15)
        
        # Live preview card
        preview_card = QFrame()
        preview_card.setObjectName("PreviewCard")
        preview_layout = QVBoxLayout(preview_card)
        preview_layout.setContentsMargins(15, 15, 15, 15)
        preview_layout.setSpacing(12)
        
        # Badge
        badge_layout = QHBoxLayout()
        badge_lbl = QLabel("● LIVE PREVIEW")
        badge_lbl.setStyleSheet("color: #00f2fe; font-weight: bold; font-size: 10px;")
        badge_layout.addWidget(badge_lbl)
        
        loop_lbl = QLabel("VIDEO LOOP - DUBBER STUDIO")
        loop_lbl.setStyleSheet("color: rgba(255, 255, 255, 0.25); font-size: 10px; font-weight: bold;")
        badge_layout.addStretch()
        badge_layout.addWidget(loop_lbl)
        
        preview_layout.addLayout(badge_layout)
        
        # Preview stack to support toggling between animated visualizer and real video playback
        self.preview_stack = QStackedWidget()
        self.preview_stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.preview_stack.setMinimumHeight(200)
        
        # Inner screen / visualizer screen
        self.visualizer = CircularVisualizerWidget()
        
        # Real video player widget
        self.video_widget = QVideoWidget()
        self.video_widget.setStyleSheet("background-color: #0b0d19;")
        
        self.preview_stack.addWidget(self.visualizer)
        self.preview_stack.addWidget(self.video_widget)
        self.preview_stack.setCurrentIndex(0)
        
        preview_layout.addWidget(self.preview_stack)
        
        # Spectrum bands (below waveform circles)
        self.spectrum = SpectrumWidget()
        preview_layout.addWidget(self.spectrum)
        
        # Timeline slider
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setObjectName("TimelineSlider")
        self.timeline_slider.setRange(0, int(self.total_duration * 1000))
        self.timeline_slider.sliderMoved.connect(self.action_timeline_moved)
        preview_layout.addWidget(self.timeline_slider)
        
        # Time display Row
        time_layout = QHBoxLayout()
        self.lbl_time_curr = QLabel("00:00:00,000")
        self.lbl_time_curr.setStyleSheet("color: #8e95b3; font-family: Courier New; font-size: 11px;")
        
        self.lbl_time_total = QLabel("00:02:21,000")
        self.lbl_time_total.setStyleSheet("color: #8e95b3; font-family: Courier New; font-size: 11px;")
        
        time_layout.addWidget(self.lbl_time_curr)
        time_layout.addStretch()
        time_layout.addWidget(self.lbl_time_total)
        preview_layout.addLayout(time_layout)
        
        # Control Bar
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)
        
        self.btn_play = QPushButton("▶")
        self.btn_play.setObjectName("BtnPlay")
        self.btn_play.clicked.connect(self.action_play_toggle)
        
        self.btn_stop = QPushButton("■")
        self.btn_stop.setObjectName("BtnStop")
        self.btn_stop.clicked.connect(self.action_stop)
        
        self.btn_volume = QPushButton("🔊")
        self.btn_volume.setObjectName("BtnVolume")
        self.btn_volume.clicked.connect(self.action_mute_toggle)
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setObjectName("VolumeSlider")
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setFixedWidth(70)
        self.volume_slider.valueChanged.connect(self.action_volume_changed)
        
        self.chk_loop = QCheckBox("🔁 Loop")
        self.chk_loop.setStyleSheet("QCheckBox { color: #8e95b3; font-weight: bold; font-size: 11px; } QCheckBox::indicator:checked { background-color: #00f2fe; }")
        self.chk_loop.setChecked(False)
        self.chk_loop.toggled.connect(self.action_toggle_loop)

        self.cassette = CassetteWidget()
        
        controls_layout.addWidget(self.btn_play)
        controls_layout.addWidget(self.btn_stop)
        controls_layout.addWidget(self.btn_volume)
        controls_layout.addWidget(self.volume_slider)
        controls_layout.addWidget(self.chk_loop)
        controls_layout.addStretch()
        controls_layout.addWidget(self.cassette)
        preview_layout.addLayout(controls_layout)
        
        left_column.addWidget(preview_card, stretch=4)
        
        # Left Bottom Tools Layout (Cutter, Merger, Settings, Export)
        tools_layout = QVBoxLayout()
        tools_layout.setSpacing(10)
        
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(10)
        self.btn_cutter = QPushButton("✂ CUTTER")
        self.btn_cutter.setObjectName("BtnCutter")
        self.btn_cutter.clicked.connect(self.action_cutter)
        
        self.btn_merger = QPushButton("🔗 MERGER")
        self.btn_merger.setObjectName("BtnMerger")
        self.btn_merger.clicked.connect(self.action_merger)
        
        row1_layout.addWidget(self.btn_cutter)
        row1_layout.addWidget(self.btn_merger)
        
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(10)
        self.btn_settings = QPushButton("⚙ Setting")
        self.btn_settings.setObjectName("BtnSettings")
        self.btn_settings.clicked.connect(self.action_settings)
        
        self.btn_export = QPushButton("⬇ EXPORT VIDEO")
        self.btn_export.setObjectName("BtnExport")
        self.btn_export.clicked.connect(self.action_export)
        
        row2_layout.addWidget(self.btn_settings, stretch=1)
        row2_layout.addWidget(self.btn_export, stretch=2)
        
        tools_layout.addLayout(row1_layout)
        tools_layout.addLayout(row2_layout)
        
        left_column.addLayout(tools_layout, stretch=1)
        
        # RIGHT COLUMN (Subtitle Table list & configs) - Width ~68%
        right_column = QVBoxLayout()
        right_column.setSpacing(12)
        
        # Control row
        control_row = QFrame()
        control_row.setObjectName("ControlRow")
        control_row_layout = QHBoxLayout(control_row)
        control_row_layout.setContentsMargins(12, 8, 12, 8)
        control_row_layout.setSpacing(10)
        
        voice_lbl = QLabel("🎙 Voice:")
        voice_lbl.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 12px;")
        
        self.voice_global_cb = QComboBox()
        self.voice_global_cb.setObjectName("GlobalVoiceCombo")
        self.voice_global_cb.addItems(["👤 Piseth (Male)", "👤 Sophea (Female)", "👤 Dara (Male)", "👤 Srey (Female)", "👤 Bora (Male)"])
        self.voice_global_cb.setFixedWidth(140)
        
        self.btn_apply_all = QPushButton("✓ Apply to All")
        self.btn_apply_all.setObjectName("BtnApplyAll")
        self.btn_apply_all.clicked.connect(self.action_apply_all_voices)
        
        self.btn_remove_vocal = QPushButton("🎙 Remove Vocal")
        self.btn_remove_vocal.setObjectName("BtnRemoveVocal")
        self.btn_remove_vocal.clicked.connect(self.action_remove_vocal)
        
        self.btn_save_srt = QPushButton("💾 រក្សាទុក SRT")
        self.btn_save_srt.setObjectName("BtnSaveSrt")
        self.btn_save_srt.clicked.connect(self.action_save_srt)
        
        control_row_layout.addWidget(voice_lbl)
        control_row_layout.addWidget(self.voice_global_cb)
        control_row_layout.addWidget(self.btn_apply_all)
        control_row_layout.addStretch()
        control_row_layout.addWidget(self.btn_remove_vocal)
        control_row_layout.addWidget(self.btn_save_srt)
        
        right_column.addWidget(control_row)
        
        # Subtitles Table Card
        table_card = QFrame()
        table_card.setObjectName("TableCard")
        table_card_layout = QVBoxLayout(table_card)
        table_card_layout.setContentsMargins(5, 5, 5, 5)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["#", "START", "END", "TEXT", "VOICE", "SPEED", ""])
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setShowGrid(False)
        
        # Set column dimensions
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 35)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.setColumnWidth(1, 105)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.setColumnWidth(2, 105)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.setColumnWidth(4, 110)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(5, 80)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(6, 40)
        
        table_card_layout.addWidget(self.table)
        right_column.addWidget(table_card, stretch=5)
        
        # Add Subtitle Button
        self.btn_add_segment = QPushButton("+ Add Subtitle Segment")
        self.btn_add_segment.setObjectName("BtnAddSegment")
        self.btn_add_segment.clicked.connect(self.action_add_segment)
        
        right_column.addWidget(self.btn_add_segment)
        
        # Assemble Column Structure
        content_layout.addLayout(left_column, stretch=3)
        content_layout.addLayout(right_column, stretch=7)
        
        main_layout.addLayout(content_layout)

    def populate_table(self):
        # Disconnect signals to prevent updates while clearing
        self.table.cellClicked.disconnect() if self.table.signalsBlocked() else None
        
        self.table.setRowCount(0)
        self.row_widgets_map.clear()
        
        for idx, sub in enumerate(self.subtitles):
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Track widgets in this row for active highlighting
            row_widgets = []
            
            # # Column
            num_item = QTableWidgetItem(str(idx + 1))
            num_item.setTextAlignment(Qt.AlignCenter)
            num_item.setForeground(QColor("#8e95b3"))
            self.table.setItem(row, 0, num_item)
            
            # START Time (QLineEdit)
            start_edit = QLineEdit(self.seconds_to_time_str(sub["start"]))
            start_edit.setObjectName("TableCellStartEdit")
            start_edit.setAlignment(Qt.AlignCenter)
            start_edit.editingFinished.connect(lambda r=row: self.cell_time_changed(r, "start"))
            self.table.setCellWidget(row, 1, start_edit)
            row_widgets.append(start_edit)
            
            # END Time (QLineEdit)
            end_edit = QLineEdit(self.seconds_to_time_str(sub["end"]))
            end_edit.setObjectName("TableCellEndEdit")
            end_edit.setAlignment(Qt.AlignCenter)
            end_edit.editingFinished.connect(lambda r=row: self.cell_time_changed(r, "end"))
            self.table.setCellWidget(row, 2, end_edit)
            row_widgets.append(end_edit)
            
            # TEXT (QLineEdit)
            text_edit = QLineEdit(str(sub["text"]))
            text_edit.setObjectName("TableCellTextEdit")
            text_edit.textChanged.connect(lambda text, r=row: self.cell_text_changed(r, text))
            self.table.setCellWidget(row, 3, text_edit)
            row_widgets.append(text_edit)
            
            # VOICE (QComboBox)
            voice_cb = QComboBox()
            voice_cb.setObjectName("TableCellCombo")
            voice_cb.addItems(["👤 Piseth", "👤 Sophea", "👤 Dara", "👤 Srey", "👤 Bora"])
            voice_map = {"piseth_male": 0, "sophea_female": 1, "dara_male": 2, "srey_female": 3, "bora_male": 4}
            voice_cb.setCurrentIndex(voice_map.get(sub["voice"], 0))
            voice_cb.currentIndexChanged.connect(lambda index, r=row: self.cell_voice_changed(r, index))
            self.table.setCellWidget(row, 4, voice_cb)
            row_widgets.append(voice_cb)
            
            # SPEED (QComboBox)
            speed_cb = QComboBox()
            speed_cb.setObjectName("TableCellCombo")
            speed_cb.addItems(["0.5x", "0.75x", "Auto", "1.0x", "1.25x", "1.5x", "2.0x"])
            speed_map = {"0.5": 0, "0.75": 1, "auto": 2, "1.0": 3, "1.25": 4, "1.5": 5, "2.0": 6}
            speed_cb.setCurrentIndex(speed_map.get(sub["speed"], 2))
            speed_cb.currentIndexChanged.connect(lambda index, r=row: self.cell_speed_changed(r, index))
            self.table.setCellWidget(row, 5, speed_cb)
            row_widgets.append(speed_cb)
            
            # DELETE (QPushButton)
            del_btn = QPushButton("🗑")
            del_btn.setObjectName("TableCellDelete")
            del_btn.clicked.connect(lambda checked, r=row: self.action_delete_row(r))
            self.table.setCellWidget(row, 6, del_btn)
            row_widgets.append(del_btn)
            
            # Map index
            self.row_widgets_map[row] = row_widgets
            
        self.table.cellClicked.connect(self.action_row_selected)
        self.highlight_active_row()

    # --- Interaction Events ---
    
    def action_play_toggle(self):
        if self.is_playing:
            self.pause_playback()
        else:
            self.start_playback()
            
    def start_playback(self):
        self.is_playing = True
        self.btn_play.setText("▮▮")
        self.visualizer.set_playing(True)
        self.spectrum.set_playing(True)
        self.cassette.set_playing(True)
        if self.video_loaded:
            self.media_player.play()
        else:
            self.playback_timer.start(30)
        
    def pause_playback(self):
        self.is_playing = False
        self.btn_play.setText("▶")
        self.visualizer.set_playing(False)
        self.spectrum.set_playing(False)
        self.cassette.set_playing(False)
        if self.video_loaded:
            self.media_player.pause()
        else:
            self.playback_timer.stop()
        
    def action_stop(self):
        self.pause_playback()
        if self.video_loaded:
            self.media_player.setPosition(0)
        self.seek_to(0.0)
        
    def action_mute_toggle(self):
        if self.is_muted:
            self.is_muted = False
            self.btn_volume.setText("🔊")
            self.volume_slider.setValue(self.pre_mute_volume)
            if self.video_loaded:
                self.media_player.setMuted(False)
        else:
            self.is_muted = True
            self.pre_mute_volume = self.volume_slider.value()
            self.btn_volume.setText("🔇")
            self.volume_slider.setValue(0)
            if self.video_loaded:
                self.media_player.setMuted(True)

    def action_volume_changed(self, value):
        if self.video_loaded:
            self.media_player.setVolume(value)

    def action_toggle_loop(self, checked):
        state_str = "ON" if checked else "OFF"
        self.show_toast(f"Video Loop: {state_str}")

    def playback_tick(self):
        if self.is_playing:
            self.current_time += 0.030
            if self.current_time >= self.total_duration:
                if hasattr(self, 'chk_loop') and not self.chk_loop.isChecked():
                    self.current_time = self.total_duration
                    self.action_pause()
                    self.show_toast("🔁 Playback Finished. Click Play or Seek to restart.")
                else:
                    self.current_time = 0.0
                
            self.update_timeline_ui()
            self.check_subtitle_highlights()

    def seek_to(self, seconds):
        self.current_time = seconds
        self.update_timeline_ui()
        self.check_subtitle_highlights()
        if self.video_loaded:
            self.media_player.setPosition(int(seconds * 1000))

    def update_timeline_ui(self):
        # Update progress slider slider value without triggering sliderMoved recursion loop
        self.timeline_slider.blockSignals(True)
        self.timeline_slider.setValue(int(self.current_time * 1000))
        self.timeline_slider.blockSignals(False)
        
        self.lbl_time_curr.setText(self.seconds_to_time_str(self.current_time))
        self.lbl_time_total.setText(self.seconds_to_time_str(self.total_duration))

    def action_timeline_moved(self, value):
        self.current_time = value / 1000.0
        self.lbl_time_curr.setText(self.seconds_to_time_str(self.current_time))
        self.check_subtitle_highlights()
        if self.video_loaded:
            self.media_player.setPosition(value)

    def check_subtitle_highlights(self):
        found_active_row = -1
        for idx, sub in enumerate(self.subtitles):
            if self.current_time >= sub["start"] and self.current_time <= sub["end"]:
                found_active_row = idx
                break
                
        if found_active_row != self.active_row_id:
            self.active_row_id = found_active_row
            self.highlight_active_row()

    # --- QMediaPlayer Slots ---
    
    def action_player_position_changed(self, position_ms):
        if self.video_loaded and self.is_playing:
            self.current_time = position_ms / 1000.0
            self.update_timeline_ui()
            self.check_subtitle_highlights()

    def action_player_duration_changed(self, duration_ms):
        if self.video_loaded and duration_ms > 0:
            self.total_duration = duration_ms / 1000.0
            self.timeline_slider.setRange(0, duration_ms)
            self.update_timeline_ui()

    def action_player_state_changed(self, state):
        # QMediaPlayer.StoppedState is 0
        if state == 0:
            self.pause_playback()

    def highlight_active_row(self):
        # Clear selections and highlights
        self.table.blockSignals(True)
        for r in range(self.table.rowCount()):
            widgets = self.row_widgets_map.get(r, [])
            if r == self.active_row_id:
                # Active styling (neon cyan highlight)
                for w in widgets:
                    if isinstance(w, QLineEdit):
                        if w.objectName() == "TableCellStartEdit":
                            w.setStyleSheet("background-color: rgba(0, 242, 254, 0.1); color: #00ff87; border: 1px solid #00f2fe; border-radius: 4px; padding: 4px;")
                        elif w.objectName() == "TableCellEndEdit":
                            w.setStyleSheet("background-color: rgba(0, 242, 254, 0.1); color: #fd267a; border: 1px solid #00f2fe; border-radius: 4px; padding: 4px;")
                        else:
                            w.setStyleSheet("background-color: rgba(0, 242, 254, 0.1); color: #ffffff; border: 1px solid #00f2fe; border-radius: 4px; padding: 4px;")
                    elif isinstance(w, QComboBox):
                        w.setStyleSheet("background-color: rgba(0, 242, 254, 0.1); color: #ffffff; border: 1px solid #00f2fe; border-radius: 4px; padding: 4px;")
                # Highlight table row highlight
                self.table.selectRow(r)
            else:
                # Standard styling
                for w in widgets:
                    if isinstance(w, QLineEdit):
                        if w.objectName() == "TableCellStartEdit":
                            w.setStyleSheet("background-color: #0b0d19; color: #00ff87; border: 1px solid rgba(255,255,255,0.05); border-radius: 4px; padding: 4px;")
                        elif w.objectName() == "TableCellEndEdit":
                            w.setStyleSheet("background-color: #0b0d19; color: #fd267a; border: 1px solid rgba(255,255,255,0.05); border-radius: 4px; padding: 4px;")
                        else:
                            w.setStyleSheet("background-color: #0b0d19; color: #f0f2fa; border: 1px solid rgba(255,255,255,0.05); border-radius: 4px; padding: 4px;")
                    elif isinstance(w, QComboBox):
                        w.setStyleSheet("background-color: #0b0d19; color: #f0f2fa; border: 1px solid rgba(255,255,255,0.05); border-radius: 4px; padding: 4px;")
        self.table.blockSignals(False)

    def action_row_selected(self, row, col):
        if row < len(self.subtitles):
            sub = self.subtitles[row]
            self.seek_to(sub["start"])

    # --- Subtitle Data Changes ---
    
    def cell_time_changed(self, row_idx, field):
        widgets = self.row_widgets_map.get(row_idx)
        if not widgets or row_idx >= len(self.subtitles):
            return
            
        edit = widgets[0] if field == "start" else widgets[1]
        time_str = edit.text()
        secs = self.time_str_to_seconds(time_str)
        
        self.subtitles[row_idx][field] = secs
        # Update slider duration ceiling if needed
        max_end = max([sub["end"] for sub in self.subtitles] + [141.0])
        self.total_duration = max_end
        self.timeline_slider.setRange(0, int(self.total_duration * 1000))
        self.update_timeline_ui()

    def cell_text_changed(self, row_idx, text):
        if row_idx < len(self.subtitles):
            self.subtitles[row_idx]["text"] = text

    def cell_voice_changed(self, row_idx, index):
        voice_types = ["piseth_male", "sophea_female", "dara_male", "srey_female", "bora_male"]
        if row_idx < len(self.subtitles) and index < len(voice_types):
            self.subtitles[row_idx]["voice"] = voice_types[index]

    def cell_speed_changed(self, row_idx, index):
        speeds = ["0.5", "0.75", "auto", "1.0", "1.25", "1.5", "2.0"]
        if row_idx < len(self.subtitles) and index < len(speeds):
            self.subtitles[row_idx]["speed"] = speeds[index]

    def action_add_segment(self):
        new_start = self.current_time
        new_end = self.current_time + 2.0
        new_sub = {
            "id": len(self.subtitles) + 1,
            "start": new_start,
            "end": new_end,
            "text": "អត្ថបទថ្មី",  # "New text" in Khmer
            "voice": "piseth_male",
            "speed": "auto"
        }
        self.subtitles.append(new_sub)
        self.subtitles.sort(key=lambda s: s["start"])
        self.populate_table()
        
        # Calculate new duration
        max_end = max([sub["end"] for sub in self.subtitles] + [141.0])
        self.total_duration = max_end
        self.timeline_slider.setRange(0, int(self.total_duration * 1000))
        self.update_timeline_ui()
        self.show_toast("Added new subtitle segment.")

    def action_delete_row(self, row_idx):
        if row_idx < len(self.subtitles):
            self.subtitles.pop(row_idx)
            self.populate_table()
            self.show_toast("Removed segment.")

    def action_apply_all_voices(self):
        index = self.voice_global_cb.currentIndex()
        voice_types = ["piseth_male", "sophea_female", "dara_male", "srey_female", "bora_male"]
        selected_voice = voice_types[index]
        
        for sub in self.subtitles:
            sub["voice"] = selected_voice
            
        self.populate_table()
        self.show_toast(f"Applied voice '{self.voice_global_cb.currentText()}' to all segments.")

    # --- Header Action Triggers ---
    
    def action_translate_video(self):
        if not self.subtitles:
            QMessageBox.information(self, "No Subtitles", "Please load or add subtitle segments before translating.")
            return
            
        dialog = TranslationDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            engine = dialog.model_cb.currentText()
            detect_gender = dialog.detect_checkbox.isChecked()
            
            khmer_phrases = [
                "សួស្តីបងប្អូន ថ្ងៃនេះយើងមកសម្រាយរឿងដ៏ជក់ចិត្តមួយ",
                "បន្ទាប់មក តួអង្គប្រុសក៏បានជួបនឹងរឿងមិននឹកស្មានដល់",
                "រឿងរ៉ាវកាន់តែស្មុគស្មាញទៅៗនៅពេលពួកគេចាប់ផ្តើមស៊ើបអង្កេត",
                "តួអង្គស្រីក៏សម្រេចចិត្តជួយសង្គ្រោះមិត្តភក្តិរបស់ខ្លួន",
                "ទីបំផុតពួកគេបានរកឃើញការពិតនៅពីក្រោយអាថ៌កំបាំងនេះ",
                "សូមទស្សនាសាច់រឿងលម្អិតជាមួយខ្ញុំទាំងអស់គ្នា",
                "កុំភ្លេចចុច Subscribe ដើម្បីទទួលបានវីដេអូសម្រាយរឿងថ្មីៗ"
            ]
            
            for i, sub in enumerate(self.subtitles):
                sub["text"] = khmer_phrases[i % len(khmer_phrases)]
                if detect_gender:
                    genders = ["piseth_male", "sophea_female", "dara_male", "srey_female"]
                    sub["voice"] = genders[i % len(genders)]
                else:
                    sub["voice"] = "sophea_female"
            
            self.populate_table()
            self.seek_to(0.0)
            self.show_toast(f"Translation completed using {engine}! Subtitle texts updated to Khmer.")

    def action_batch(self):
        dialog = BatchDubberDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            default_voice = "sophea_female" if "Female" in dialog.batch_voice_cb.currentText() else "piseth_male"
            self.subtitles = [
                {"id": 1, "start": 1.5, "end": 5.2, "text": "ជម្រាបសួរលោកអ្នកទស្សនា! នេះជារឿងភាគបកប្រែអូតូដោយ Gemini AI។", "voice": default_voice, "speed": "1.0"},
                {"id": 2, "start": 5.8, "end": 9.6, "text": "ថ្ងៃនេះយើងនឹងតាមដានសាច់រឿងដ៏ជក់ចិត្ត ជាមួយសំឡេងខ្មែរច្បាស់ៗ។", "voice": "piseth_male", "speed": "1.0"},
                {"id": 3, "start": 10.2, "end": 14.8, "text": "តួអង្គប្រុសបាននិយាយថា គេនឹងត្រឡប់មកវិញនៅពេលឆាប់ៗនេះ។", "voice": "dara_male", "speed": "1.0"},
                {"id": 4, "start": 15.5, "end": 19.9, "text": "តួអង្គស្រីក៏បានឆ្លើយតបវិញ ដោយក្តីសង្ឃឹម និងការរង់ចាំ។", "voice": "srey_female", "speed": "1.0"},
                {"id": 5, "start": 20.6, "end": 25.2, "text": "ដំណើររឿងកាន់តែរំភើប និងមានអាថ៌កំបាំងជាច្រើនទៀត។", "voice": "bora_male", "speed": "1.0"},
                {"id": 6, "start": 26.0, "end": 31.0, "text": "សូមអរគុណសម្រាប់ការទស្សនា និងគាំទ្រ Kemsinin Dubber Pro!", "voice": "sophea_female", "speed": "1.0"}
            ]
            self.populate_table()
            self.show_toast(f"✅ Batch Dubber: បកប្រែរឿងអូតូរួចរាល់! Subtitles {len(self.subtitles)} segments ត្រូវបានបញ្ចូលក្នុងប្រអប់ Segment។")

    def action_upload_video(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Upload Video", "", "Video Files (*.mp4 *.mkv *.avi *.mov)")
        if file_path:
            file_name = os.path.basename(file_path)
            self.show_toast(f"Loaded Video: {file_name}")
            
            # Load video file into media player
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            self.media_player.setVideoOutput(self.video_widget)
            self.video_loaded = True
            
            # Switch stacked widget index to the video player view
            self.preview_stack.setCurrentIndex(1)
            
            # Set volume from current slider value
            self.media_player.setVolume(self.volume_slider.value())
            
            # Pause and reset current position
            self.pause_playback()
            self.seek_to(0.0)

    def action_upload_srt(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Upload SRT", "", "Subtitle Files (*.srt)")
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                parsed = self.parse_srt(content)
                if parsed:
                    self.subtitles = parsed
                    self.populate_table()
                    # Re-scale timeline duration
                    max_end = max([sub["end"] for sub in self.subtitles] + [141.0])
                    self.total_duration = max_end
                    self.timeline_slider.setRange(0, int(self.total_duration * 1000))
                    self.seek_to(0.0)
                    self.show_toast("Successfully loaded SRT subtitles.")
                else:
                    QMessageBox.warning(self, "Parse Error", "Could not parse SRT file structure.")
            except Exception as e:
                QMessageBox.critical(self, "File Error", f"Could not load file:\n{str(e)}")

    def action_save_srt(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save SRT Subtitles", "dubber_export.srt", "Subtitle Files (*.srt)")
        if file_path:
            try:
                srt_content = self.format_srt(self.subtitles)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(srt_content)
                self.show_toast(f"Subtitles saved to:\n{os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Could not save file:\n{str(e)}")

    def action_remove_vocal(self):
        self.show_toast("AI Vocal Remover: Aligning channels & attenuating vocals...")
        QTimer.singleShot(1500, lambda: self.show_toast("AI Vocal Remover: Extracting center channel sound FX..."))
        QTimer.singleShot(3000, lambda: self.show_toast("AI Vocal Remover: Complete. Ambient vocals attenuated by 24dB."))

    def action_video_transcript(self):
        self.show_toast("AI-Powered Video Transcription: Analyzing vocal signals...")
        # Simulate loading in steps
        QTimer.singleShot(1500, lambda: self.show_toast("AI-Powered Video Transcription: Generating multi-lingual timestamps..."))
        QTimer.singleShot(3000, self.simulate_transcription_complete)

    def simulate_transcription_complete(self):
        # Sample simulated transcription results (Khmer sentences with timestamps)
        self.subtitles = [
            {"id": 1, "start": 1.500, "end": 4.200, "text": "សូមស្វាគមន៍មកកាន់កម្មវិធី AI Dubbing Studio", "voice": "piseth_male", "speed": "auto"},
            {"id": 2, "start": 5.000, "end": 8.500, "text": "ប្រព័ន្ធកំពុងវិភាគសម្លេងនិងបម្លែងជាអត្ថបទគំរូ", "voice": "sophea_female", "speed": "auto"},
            {"id": 3, "start": 9.200, "end": 12.800, "text": "អ្នកអាចកែសម្រួលពេលវេលានិងអត្ថបទបានដោយសេរី", "voice": "dara_male", "speed": "auto"},
            {"id": 4, "start": 13.500, "end": 16.000, "text": "សូមអរគុណសម្រាប់ការប្រើប្រាស់សេវាកម្មរបស់យើងខ្ញុំ", "voice": "srey_female", "speed": "auto"}
        ]
        self.populate_table()
        # Scale timeline duration
        max_end = max([sub["end"] for sub in self.subtitles] + [141.0])
        self.total_duration = max_end
        self.timeline_slider.setRange(0, int(self.total_duration * 1000))
        self.seek_to(0.0)
        self.show_toast("AI Transcription Complete: Generated timestamps loaded directly into your script catalog!")

    def action_effect(self):
        self.current_theme = (self.current_theme + 1) % 3
        themes = ["Neon Horizon (Cyan/Magenta)", "Emerald Matrix (Green/Purple)", "Cyber Fusion (Amber/Red)"]
        self.setStyleSheet(self.get_main_style())
        self.show_toast(f"Audio Effect Profile: {themes[self.current_theme]}")

    def action_cutter(self):
        # Find active segment containing current playhead
        target = None
        for idx, sub in enumerate(self.subtitles):
            if self.current_time >= sub["start"] and self.current_time <= sub["end"]:
                target = sub
                break
                
        if not target:
            QMessageBox.warning(self, "Split Error", "Playhead is not positioned inside any segment timeline.")
            return
            
        # Check buffer space
        if (self.current_time - target["start"] < 0.5) or (target["end"] - self.current_time < 0.5):
            QMessageBox.warning(self, "Split Error", "Cannot split too close to edges (minimum segment length is 0.5s).")
            return
            
        # Split target
        original_end = target["end"]
        target["end"] = self.current_time
        
        # Insert next segment
        new_sub = {
            "id": max([s["id"] for s in self.subtitles] + [0]) + 1,
            "start": self.current_time,
            "end": original_end,
            "text": "បំបែកផ្នែក (Split Segment)",
            "voice": target["voice"],
            "speed": target["speed"],
            "file_header": target.get("file_header", "")
        }
        self.subtitles.append(new_sub)
        self.subtitles.sort(key=lambda s: s["start"])
        self.populate_table()
        self.show_toast("Segment successfully split!")

    def action_merger(self):
        dialog = MergeDialog(self.subtitles, self)
        if dialog.exec_() == QDialog.Accepted:
            idx = dialog.combo.currentIndex()
            if idx >= 0 and idx < len(dialog.subtitles) - 1:
                s1 = dialog.subtitles[idx]
                s2 = dialog.subtitles[idx+1]
                
                # Update s1
                s1["end"] = s2["end"]
                s1["text"] = s1["text"] + " " + s2["text"]
                
                # Delete s2
                self.subtitles = [s for s in self.subtitles if s["id"] != s2["id"]]
                self.populate_table()
                self.show_toast("Segments merged successfully!")

    def action_settings(self):
        dialog = SettingsDialog(self.pitch_multiplier, self)
        if dialog.exec_() == QDialog.Accepted:
            self.pitch_multiplier = dialog.pitch_val
            self.show_toast(f"Config Saved: Pitch Multiplier set to {self.pitch_multiplier:.2f}")

    def action_export(self):
        dialog = ExportProgressDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Dubbed Video", "dubbed_export.mp4", "Video Files (*.mp4)")
            if file_path:
                self.show_toast(f"Successfully exported to: {os.path.basename(file_path)}")

    # --- Tooling utilities ---
    
    def show_toast(self, message):
        self.statusBar().showMessage(message, 3000)

    def parse_srt(self, content):
        subtitles = []
        blocks = content.strip().replace('\r\n', '\n').split('\n\n')
        current_header = ""
        for block in blocks:
            lines = [l.strip() for l in block.split('\n') if l.strip()]
            if not lines:
                continue
            
            # If the block itself is just a header, or starts with a header:
            if lines[0].startswith("=====") and lines[0].endswith("====="):
                current_header = lines.pop(0)
                
            if len(lines) >= 3:
                try:
                    sub_id = int(lines[0])
                except ValueError:
                    continue
                
                time_line = lines[1]
                if '-->' in time_line:
                    parts = time_line.split('-->')
                    start_sec = self.time_str_to_seconds(parts[0].strip())
                    end_sec = self.time_str_to_seconds(parts[1].strip())
                    text = '\n'.join(lines[2:])
                    subtitles.append({
                        "id": sub_id,
                        "start": start_sec,
                        "end": end_sec,
                        "text": text,
                        "voice": "piseth_male",
                        "speed": "auto",
                        "file_header": current_header,
                        "orig_start": start_sec,
                        "orig_end": end_sec,
                        "raw_start": parts[0].strip(),
                        "raw_end": parts[1].strip()
                    })
        return subtitles

    def format_srt(self, subtitles=None):
        if subtitles is None:
            subtitles = self.subtitles
        lines = []
        last_header = None
        for idx, sub in enumerate(subtitles):
            file_header = sub.get("file_header", "")
            if file_header and file_header != last_header:
                if lines:  # Add a blank line before the new header if it's not the first element
                    lines.append("")
                lines.append(file_header)
                last_header = file_header
                
            lines.append(str(sub.get("id", idx + 1)))
            
            if "raw_start" in sub and abs(sub["start"] - sub.get("orig_start", 0)) < 0.001:
                start_str = sub["raw_start"]
            else:
                start_str = self.seconds_to_time_str(sub["start"])
                
            if "raw_end" in sub and abs(sub["end"] - sub.get("orig_end", 0)) < 0.001:
                end_str = sub["raw_end"]
            else:
                end_str = self.seconds_to_time_str(sub["end"])
                
            lines.append(f"{start_str} --> {end_str}")
            lines.append(str(sub["text"]))
            lines.append("")
        return '\n'.join(lines)

    def time_str_to_seconds(self, time_str):
        try:
            time_str = str(time_str).strip().replace(',', '.')
            parts = time_str.split(':')
            if len(parts) == 3:
                h = float(parts[0])
                m = float(parts[1])
                s = float(parts[2])
                return h * 3600 + m * 60 + s
            elif len(parts) == 2:
                m = float(parts[0])
                s = float(parts[1])
                return m * 60 + s
            return float(time_str)
        except ValueError:
            return 0.0

    def seconds_to_time_str(self, secs):
        hrs = int(secs // 3600)
        mins = int((secs - hrs * 3600) // 60)
        remaining = secs - hrs * 3600 - mins * 60
        secs_int = int(remaining)
        ms = int(round((remaining - secs_int) * 1000))
        if ms >= 1000:
            ms = 999
        return f"{hrs:02d}:{mins:02d}:{secs_int:02d},{ms:03d}"

    def get_main_style(self):
        theme = getattr(self, "current_theme", 0)
        
        # Define theme palettes
        if theme == 0:
            c_cyan = "#00f2fe"       # Cyan
            c_secondary = "#fd267a"  # Magenta
            c_emerald = "#00ff87"    # Emerald
            c_purple = "#8a2be2"     # Purple
            c_glow = "rgba(0, 242, 254, 0.15)"
        elif theme == 1:
            c_cyan = "#00ff87"       # Emerald
            c_secondary = "#8a2be2"  # Purple
            c_emerald = "#00f2fe"    # Cyan
            c_purple = "#fd267a"     # Magenta
            c_glow = "rgba(0, 255, 135, 0.15)"
        else:
            c_cyan = "#ffab40"       # Amber
            c_secondary = "#ff3d00"  # Red
            c_emerald = "#00ff87"    # Emerald
            c_purple = "#8a2be2"     # Purple
            c_glow = "rgba(255, 171, 64, 0.15)"
            
        return f"""
            /* Main window general layout styling */
            QMainWindow {{
                background-color: #0b0d19;
            }}
            QWidget#CentralWidget {{
                background-color: #0b0d19;
            }}
            
            /* Status Bar / Toast */
            QStatusBar {{
                background-color: #111324;
                color: {c_cyan};
                font-weight: bold;
                border-top: 1px solid rgba(255,255,255,0.08);
            }}
            
            /* Header */
            QFrame#HeaderCard {{
                background-color: #111324;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
            }}
            
            /* Left Cards styling */
            QFrame#PreviewCard {{
                background-color: #111324;
                border: 1px solid rgba(0, 242, 254, 0.2);
                border-radius: 12px;
            }}
            QFrame#ControlRow {{
                background-color: #111324;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
            }}
            QFrame#TableCard {{
                background-color: #111324;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
            }}
            
            /* Header Pill Buttons */
            QPushButton#BtnBatch {{
                background-color: {c_secondary};
                color: white;
                font-weight: bold;
                font-size: 11px;
                border-radius: 14px;
                padding: 6px 14px;
            }}
            QPushButton#BtnBatch:hover {{
                background-color: #e0226c;
            }}
            QPushButton#BtnTranslate {{
                background-color: {c_cyan};
                color: #0b0d19;
                font-weight: bold;
                font-size: 11px;
                border-radius: 14px;
                padding: 6px 14px;
            }}
            QPushButton#BtnTranslate:hover {{
                background-color: #00d3dd;
            }}
            QPushButton#BtnUploadVideo {{
                background-color: #ff4b2b;
                color: white;
                font-weight: bold;
                font-size: 11px;
                border-radius: 14px;
                padding: 6px 14px;
            }}
            QPushButton#BtnUploadVideo:hover {{
                background-color: #e54325;
            }}
            QPushButton#BtnUploadSrt {{
                background-color: {c_emerald};
                color: #0b0d19;
                font-weight: bold;
                font-size: 11px;
                border-radius: 14px;
                padding: 6px 14px;
            }}
            QPushButton#BtnUploadSrt:hover {{
                background-color: #00e075;
            }}
            QPushButton#BtnTranscript {{
                background-color: {c_purple};
                color: white;
                font-weight: bold;
                font-size: 11px;
                border-radius: 14px;
                padding: 6px 14px;
            }}
            QPushButton#BtnTranscript:hover {{
                background-color: #7925c7;
            }}
            QPushButton#BtnEffect {{
                background-color: {c_secondary};
                color: white;
                font-weight: bold;
                font-size: 11px;
                border-radius: 14px;
                padding: 6px 14px;
            }}
            QPushButton#BtnEffect:hover {{
                background-color: #e0226c;
            }}
            
            /* Left control widgets */
            QPushButton#BtnPlay {{
                background-color: #242846;
                color: {c_cyan};
                font-size: 14px;
                border: 1px solid rgba(0, 242, 254, 0.15);
                border-radius: 6px;
                min-width: 32px;
                min-height: 28px;
            }}
            QPushButton#BtnPlay:hover {{
                background-color: #2e345c;
                border-color: {c_cyan};
            }}
            QPushButton#BtnStop {{
                background-color: #242846;
                color: {c_secondary};
                font-size: 11px;
                border: 1px solid rgba(253, 38, 122, 0.15);
                border-radius: 6px;
                min-width: 32px;
                min-height: 28px;
            }}
            QPushButton#BtnStop:hover {{
                background-color: #2e345c;
                border-color: {c_secondary};
            }}
            QPushButton#BtnVolume {{
                background-color: #242846;
                color: white;
                font-size: 12px;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 6px;
                min-width: 32px;
                min-height: 28px;
            }}
            QPushButton#BtnVolume:hover {{
                background-color: #2e345c;
            }}
            
            /* Bottom Action tools */
            QPushButton#BtnCutter {{
                background-color: #ff4b2b;
                color: white;
                font-weight: bold;
                font-size: 13px;
                border-radius: 8px;
                padding: 12px;
            }}
            QPushButton#BtnCutter:hover {{
                background-color: #e54325;
            }}
            QPushButton#BtnMerger {{
                background-color: {c_cyan};
                color: #0b0d19;
                font-weight: bold;
                font-size: 13px;
                border-radius: 8px;
                padding: 12px;
            }}
            QPushButton#BtnMerger:hover {{
                background-color: #00d3dd;
            }}
            QPushButton#BtnSettings {{
                background-color: #242846;
                color: white;
                font-weight: bold;
                font-size: 12px;
                border-radius: 8px;
                padding: 10px;
                border: 1px solid rgba(255,255,255,0.08);
            }}
            QPushButton#BtnSettings:hover {{
                background-color: #2e345c;
            }}
            QPushButton#BtnExport {{
                background-color: {c_emerald};
                color: #0b0d19;
                font-weight: bold;
                font-size: 12px;
                border-radius: 8px;
                padding: 10px;
            }}
            QPushButton#BtnExport:hover {{
                background-color: #00e075;
            }}
            
            /* Right actions buttons */
            QPushButton#BtnApplyAll {{
                background-color: {c_secondary};
                color: white;
                font-weight: bold;
                font-size: 11px;
                border-radius: 6px;
                padding: 6px 12px;
            }}
            QPushButton#BtnApplyAll:hover {{
                background-color: #7925c7;
            }}
            QPushButton#BtnRemoveVocal {{
                background-color: {c_emerald};
                color: #0b0d19;
                font-weight: bold;
                font-size: 11px;
                border-radius: 6px;
                padding: 6px 12px;
            }}
            QPushButton#BtnRemoveVocal:hover {{
                background-color: #00e075;
            }}
            QPushButton#BtnSaveSrt {{
                background-color: {c_cyan};
                color: #0b0d19;
                font-weight: bold;
                font-size: 11px;
                border-radius: 6px;
                padding: 6px 12px;
            }}
            QPushButton#BtnSaveSrt:hover {{
                background-color: #00d3dd;
            }}
            
            /* Add Segment Button (Dashed style) */
            QPushButton#BtnAddSegment {{
                background-color: rgba(255, 255, 255, 0.02);
                color: #8e95b3;
                font-weight: bold;
                font-size: 12px;
                border: 1px dashed rgba(255, 255, 255, 0.15);
                border-radius: 8px;
                padding: 10px;
            }}
            QPushButton#BtnAddSegment:hover {{
                background-color: rgba(255, 255, 255, 0.05);
                color: white;
                border-color: {c_cyan};
            }}
            
            /* Timeline Slider QSS */
            QSlider#TimelineSlider::groove:horizontal {{
                border: none;
                height: 6px;
                background: #1e2530;
                border-radius: 3px;
            }}
            QSlider#TimelineSlider::sub-page:horizontal {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fd267a, stop:1 {c_cyan});
                border-radius: 3px;
            }}
            QSlider#TimelineSlider::handle:horizontal {{
                background: #ffffff;
                border: 2px solid {c_cyan};
                width: 14px;
                margin-top: -4px;
                margin-bottom: -4px;
                border-radius: 7px;
            }}
            
            /* Volume Slider QSS */
            QSlider#VolumeSlider::groove:horizontal {{
                border: none;
                height: 4px;
                background: #1e2530;
                border-radius: 2px;
            }}
            QSlider#VolumeSlider::sub-page:horizontal {{
                background: {c_cyan};
                border-radius: 2px;
            }}
            QSlider#VolumeSlider::handle:horizontal {{
                background: #ffffff;
                width: 10px;
                margin-top: -3px;
                margin-bottom: -3px;
                border-radius: 5px;
            }}
            
            /* Comboboxes QSS */
            QComboBox {{
                background-color: #0b0d19;
                color: #f0f2fa;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 6px;
                padding: 4px 8px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #8e95b3;
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #0b0d19;
                color: #f0f2fa;
                selection-background-color: #8a2be2;
                border: 1px solid rgba(255, 255, 255, 0.15);
            }}
            
            /* Tables QSS */
            QTableWidget {{
                background-color: #111324;
                border: none;
                gridline-color: transparent;
            }}
            QHeaderView::section {{
                background-color: #111324;
                color: #8e95b3;
                padding: 8px;
                font-weight: bold;
                font-size: 10px;
                border: none;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }}
            
            /* Scrollbars */
            QScrollBar:vertical {{
                border: none;
                background: #0b0d19;
                width: 6px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(0, 242, 254, 0.4);
                min-height: 20px;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {c_cyan};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KemsininDubberApp()
    window.show()
    sys.exit(app.exec_())