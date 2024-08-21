#! /usr/bin/env python

import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QInputDialog, QMessageBox, QFileDialog
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, Qt, QTimer
from PyQt5.QtGui import QIcon
from easy_json import get_value, edit_value

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        # for .json file location
        self.config_file = os.path.expanduser("~/.local/share/no-skip-video-player/last_position.json")

        # Check always on top state
        self.alwaysOnTopState = get_value("alwaysOnTopState", self.config_file)
        if self.alwaysOnTopState:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        # Define the path to store resume history
        self.data_dir = os.path.expanduser("~/.local/share/no-skip-video-player/")
        self.position_file = os.path.join(self.data_dir, "last_position.json")

        # Ensure the directory exists
        os.makedirs(self.data_dir, exist_ok=True)

        # Initialize QMediaPlayer
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        # Create Video Widget
        videoWidget = QVideoWidget()

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
        self.setLayout(layout)

        # Connect mediaPlayer to videoWidget
        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.mediaStatusChanged.connect(self.handleMediaStatusChanged)

        # Set up the window
        self.setWindowTitle("No Skip Video Player")
        self.setWindowIcon(QIcon(os.path.expanduser("~/MyGitRepos/no-skip-video-player/icon.png")))
        self.setGeometry(100, 100, 800, 450)

        # Timer to stop video after a specific time
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.stopAndClose)
        self.timer_active = get_value("timer_active", self.config_file)
        self.timer_duration = get_value("timer_set", self.config_file)  # Default to 5 minutes (in milliseconds)

        # filename for addition
        self.filename = ""

        # Load the last video file
        self.loadLastVideo()

    def setAlwaysOnTop(self):
        self.alwaysOnTopState = not self.alwaysOnTopState
        if self.alwaysOnTopState:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()
        QMessageBox.information(self, "Always On Top State", f"alwaysOnTopState: {self.alwaysOnTopState}")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.playVideo()
        elif event.key() == Qt.Key_T and event.modifiers() & Qt.ShiftModifier:
            self.setSleepTimer()
        elif event.key() == Qt.Key_T and event.modifiers() & Qt.ControlModifier:
            self.setTimerState()
        elif event.key() == Qt.Key_N and event.modifiers() & Qt.ShiftModifier:
            self.loadVideo()
        elif event.key() == Qt.Key_I and event.modifiers() & Qt.ShiftModifier:
            self.showCurrentPoint()
        elif event.key() == Qt.Key_A and event.modifiers() & Qt.ShiftModifier:
            self.setAlwaysOnTop()
        else:
            super().keyPressEvent(event)

    def playVideo(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def handleMediaStatusChanged(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.mediaPlayer.setPosition(0)  # Reset position to start
            self.mediaPlayer.play()

    def setTimerState(self):
        if self.timer_active:
            self.timer_active = False
            self.timer.stop()
        else:
            self.timer.start(self.timer_duration)
            self.timer_active = True
        
        self.setTitle(self.filename)

    def setSleepTimer(self):
        minutes, ok = QInputDialog.getInt(self, "Set Sleep Timer", "Enter sleep time in minutes:", 5, 1, 120, 1)
        if ok:
            self.timer_duration = minutes * 60000  # Convert minutes to milliseconds
            edit_value("timer_set", self.timer_duration, self.config_file)
            self.timer_active = True
            self.setTitle(self.filename)
            self.timer.start(self.timer_duration)
            QMessageBox.information(self, "Timer Set", f"Video will stop in {minutes} minutes.")

    def showCurrentPoint(self):
        currentPoint = self.mediaPlayer.position()
        minutePoint = currentPoint / 60000
        QMessageBox.information(self, "You Lasted?", f"How Long Have I lasted? - {minutePoint}")

    def savePosition(self, position):
        file_url = self.mediaPlayer.media().canonicalUrl().toString()
        if self.mediaPlayer.state() in (QMediaPlayer.PlayingState, QMediaPlayer.PausedState):
            last_position = {
                "position": position,
                "file": file_url,
                "timer_active": self.timer_active,
                "timer_set": self.timer_duration,
                "alwaysOnTopState": self.alwaysOnTopState
            }
            with open(self.position_file, 'w') as f:
                json.dump(last_position, f)
            print("Video position saved (Playing or Paused)")

    def loadLastVideo(self):
        if os.path.exists(self.position_file):
            with open(self.position_file, 'r') as f:
                last_position = json.load(f)

            file_url = last_position.get("file")
            position = last_position.get("position")
            self.timer_active = last_position.get("timer_active", False)

            if file_url and position is not None:
                filename = os.path.basename(QUrl(file_url).toLocalFile())
                self.filename = filename
                self.setTitle(filename)
                self.mediaPlayer.setMedia(QMediaContent(QUrl(file_url)))
                self.mediaPlayer.setPosition(position)
                self.mediaPlayer.play()

                if self.timer_active:
                    self.timer.start(self.timer_duration)
        else:
            self.loadVideo()

    def loadVideo(self):
        fileDialog = QFileDialog(self)
        fileDialog.setNameFilters(["Videos (*.mp4 *.avi *.mkv)"])
        if fileDialog.exec_():
            fileUrl = fileDialog.selectedUrls()[0]
            self.mediaPlayer.setMedia(QMediaContent(fileUrl))
            self.mediaPlayer.play()
            name = os.path.basename(QUrl(fileUrl).toLocalFile())
            self.filename = name
            self.setTitle(name)
        else:
            QApplication.quit()

    def setTitle(self, filename):
        timerState = "TimerOn" if self.timer_active else "TimerOff"
        self.setWindowTitle(f"{timerState}:{int(self.timer_duration / 1000)}s - {filename}")

    def stopAndClose(self):
        try:
            current_position = self.mediaPlayer.position()
            self.savePosition(current_position)
            self.mediaPlayer.stop()
        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            QApplication.quit()

    def closeEvent(self, event):
        position = self.mediaPlayer.position()
        self.savePosition(position)
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())
