#!/usr/bin/env python3

import sys
import os
import json

from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QInputDialog,
                             QMessageBox, QFileDialog, QToolBar)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QUrl, Qt, QTimer
from PyQt6.QtGui import QIcon, QAction


class NoSkipVideoPlayer(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: black;")

        self.script_path = os.path.dirname(os.path.abspath(__file__))

        self.play_icon = QIcon.fromTheme("media-playback-start")
        self.pause_icon = QIcon.fromTheme("media-playback-pause")

        self.timer_on_icon = QIcon(os.path.join(self.script_path, "icons", "timer-on.png"))
        self.timer_off_icon = QIcon(os.path.join(self.script_path, "icons", "timer-off.png"))

        self.config_dir = os.path.expanduser("~/.config/no-skip-video-player")
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.ensure_config_exists()

        self.config = self.load_config()

        self.mediaPlayer = QMediaPlayer()
        self.audioOutput = QAudioOutput()
        self.mediaPlayer.setAudioOutput(self.audioOutput)

        self.videoWidget = QVideoWidget()
        self.mediaPlayer.setVideoOutput(self.videoWidget)

        self.setup_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close)

        self.current_file = ""

        self.mediaPlayer.mediaStatusChanged.connect(self.handle_media_status)
        self.mediaPlayer.positionChanged.connect(self.save_position_auto)

        self.load_last_session()

    def ensure_config_exists(self):
        os.makedirs(self.config_dir, exist_ok=True)
        if not os.path.exists(self.config_file):
            default_config = {
                "always_on_top": False,
                "timer_active": False,
                "timer_duration": 300000,
                "last_file": "",
                "last_position": 0,
                "fullscreen": False
            }
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f)

    def load_config(self):
        with open(self.config_file, 'r') as f:
            return json.load(f)

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.toolbar = QToolBar("Main Toolbar")
        layout.addWidget(self.toolbar)

        self.create_actions()

        layout.addWidget(self.videoWidget)

        self.setWindowTitle("No Skip Video Player")
        self.setGeometry(100, 100, 800, 450)

        if self.config["always_on_top"]:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        if self.config["fullscreen"]:
            self.toggle_fullscreen()

    def create_actions(self):
        self.play_action = QAction(self.pause_icon, "Play/Pause (Space)", self)
        self.play_action.triggered.connect(self.toggle_playback)
        self.toolbar.addAction(self.play_action)

        self.toggle_timer_action = QAction(self.timer_on_icon, "Toggle Timer (Ctrl+T)", self)
        self.toggle_timer_action.triggered.connect(self.toggle_timer)
        self.toolbar.addAction(self.toggle_timer_action)

        self.load_action = QAction(QIcon.fromTheme("document-open"), "Load Video (Shift+N)", self)
        self.load_action.triggered.connect(self.load_video)
        self.toolbar.addAction(self.load_action)

        self.timer_action = QAction(QIcon.fromTheme("chronometer"), "Set Sleep Timer (Shift+T)", self)
        self.timer_action.triggered.connect(self.set_sleep_timer)
        self.toolbar.addAction(self.timer_action)

        self.position_action = QAction(QIcon.fromTheme("preferences-system-time"), "Show Position (Shift+I)", self)
        self.position_action.triggered.connect(self.show_current_position)
        self.toolbar.addAction(self.position_action)

        self.always_top_action = QAction(QIcon.fromTheme("window-pin"), "Always On Top (Shift+A)", self)
        self.always_top_action.triggered.connect(self.toggle_always_on_top)
        self.toolbar.addAction(self.always_top_action)

        self.fullscreen_action = QAction(QIcon.fromTheme("view-fullscreen"), "Toggle Fullscreen (F or Ctrl+F)", self)
        self.fullscreen_action.triggered.connect(self.toggle_fullscreen)
        self.toolbar.addAction(self.fullscreen_action)

        self.quit_action = QAction(QIcon.fromTheme("application-exit"), "Quit (Ctrl+Q)", self)
        self.quit_action.setShortcut("Ctrl+Q")
        self.quit_action.triggered.connect(self.close)
        self.toolbar.addAction(self.quit_action)

    def handle_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.mediaPlayer.setPosition(0)
            self.mediaPlayer.play()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.toggle_playback()
        elif event.key() == Qt.Key.Key_T and event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            self.set_sleep_timer()
        elif event.key() == Qt.Key.Key_T and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.toggle_timer()
        elif event.key() == Qt.Key.Key_N and event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            self.load_video()
        elif event.key() == Qt.Key.Key_I and event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            self.show_current_position()
        elif event.key() == Qt.Key.Key_A and event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            self.toggle_always_on_top()
        elif event.key() == Qt.Key.Key_F or (event.key() == Qt.Key.Key_F and event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self.toggle_fullscreen()
        elif event.key() == Qt.Key.Key_Escape and self.isFullScreen():
            self.toggle_fullscreen()
        elif event.key() == Qt.Key.Key_Q and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.close()
        else:
            super().keyPressEvent(event)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.setWindowFlag(Qt.WindowType.FramelessWindowHint, False)
            self.toolbar.show()
            if self.config["always_on_top"]:
                self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
            self.show()
            self.config["fullscreen"] = False
        else:
            self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
            self.toolbar.hide()
            self.showFullScreen()
            self.config["fullscreen"] = True
        self.save_config()

    def toggle_playback(self):
        if self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.mediaPlayer.pause()
            self.play_action.setIcon(self.play_icon)
        else:
            self.mediaPlayer.play()
            self.play_action.setIcon(self.pause_icon)

    def toggle_timer(self):
        self.config["timer_active"] = not self.config["timer_active"]
        if self.config["timer_active"]:
            self.timer.start(self.config["timer_duration"])
            self.toggle_timer_action.setIcon(self.timer_on_icon)
        else:
            self.timer.stop()
            self.toggle_timer_action.setIcon(self.timer_off_icon)
        self.update_window_title()
        self.save_config()

    def set_sleep_timer(self):
        minutes, ok = QInputDialog.getInt(
            self, "Set Sleep Timer",
            "Enter sleep time in minutes:",
            self.config["timer_duration"] // 60000, 1, 120, 1
        )
        if ok:
            self.config["timer_duration"] = minutes * 60000
            self.config["timer_active"] = True
            self.timer.start(self.config["timer_duration"])
            self.update_window_title()
            self.save_config()
            QMessageBox.information(self, "Timer Set", f"Video will stop in {minutes} minutes.")

    def show_current_position(self):
        minutes = self.mediaPlayer.position() / 60000
        QMessageBox.information(self, "Current Position", f"Current position: {minutes:.2f} minutes")

    def save_position_auto(self, position):
        if self.mediaPlayer.playbackState() in (
            QMediaPlayer.PlaybackState.PlayingState,
            QMediaPlayer.PlaybackState.PausedState
        ):
            self.config["last_position"] = position
            self.config["last_file"] = self.current_file
            self.save_config()

    def load_last_session(self):
        if self.config["last_file"] and os.path.exists(self.config["last_file"]):
            self.current_file = self.config["last_file"]
            self.mediaPlayer.setSource(QUrl.fromLocalFile(self.current_file))
            self.mediaPlayer.setPosition(self.config["last_position"])
            self.mediaPlayer.play()
            self.update_window_title()
            if self.config["timer_active"]:
                self.timer.start(self.config["timer_duration"])
        else:
            self.load_video()

    def load_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv *.mov)"
        )
        if file_path:
            self.current_file = file_path
            self.mediaPlayer.setSource(QUrl.fromLocalFile(file_path))
            self.mediaPlayer.play()
            self.update_window_title()
            self.config["last_file"] = file_path
            self.config["last_position"] = 0
            self.save_config()
        elif not self.config["last_file"]:
            sys.exit()

    def update_window_title(self):
        timer_status = "ON" if self.config["timer_active"] else "OFF"
        duration = self.config["timer_duration"] // 60000
        filename = os.path.basename(self.current_file) if self.current_file else "No File"
        self.setWindowTitle(f"No Skip Video Player | Timer: {timer_status} ({duration}min) | {filename}")

    def toggle_always_on_top(self):
        self.config["always_on_top"] = not self.config["always_on_top"]
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, self.config["always_on_top"])
        self.show()
        self.save_config()
        QMessageBox.information(
            self, "Always On Top",
            f"Always on top: {'Enabled' if self.config['always_on_top'] else 'Disabled'}"
        )

    def closeEvent(self, event):
        self.save_position_auto(self.mediaPlayer.position())
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = NoSkipVideoPlayer()
    player.show()
    sys.exit(app.exec())
