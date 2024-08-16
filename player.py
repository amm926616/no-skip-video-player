import sys, os, json
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

        # Set up the window
        self.setWindowTitle("No Skip Video Player")
        self.setWindowIcon(QIcon("/home/adam178/Programmings/no-skip-video/icon.png"))
        self.setGeometry(100, 100, 800, 500)

        # Timer to stop video after a specific time
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.stopAndClose)
        self.timer_active = True
        self.timer_duration = get_value("timer_set", "/home/adam178/.local/share/no-skip-video-player/last_position.json")  # Default to 5 minutes (in milliseconds)
        
        # Load the last video file
        self.loadLastVideo()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.playVideo()
        elif event.key() == Qt.Key_T and event.modifiers() & Qt.ShiftModifier:
            self.setSleepTimer()
        elif event.key() == Qt.Key_N and event.modifiers() & Qt.ShiftModifier:
            self.loadVideo()
        elif event.key() == Qt.Key_I and event.modifiers() & Qt.ShiftModifier:
            self.showCurrentPoint()
        else:
            super().keyPressEvent(event)
    
    def playVideo(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def setSleepTimer(self):
        # Popup window to set timer
        minutes, ok = QInputDialog.getInt(self, "Set Sleep Timer", "Enter sleep time in minutes:", 5, 1, 120, 1)
        
        if ok:
            self.timer_duration = minutes * 60000  # Convert minutes to milliseconds
            edit_value("timer_set", self.timer_duration, "/home/adam178/.local/share/no-skip-video-player/last_position.json")
            self.timer_active = True
            self.timer.start(self.timer_duration)
            QMessageBox.information(self, "Timer Set", f"Video will stop in {minutes} minutes.")

    def showCurrentPoint(self):
        currentPoint = self.mediaPlayer.position()
        minutePoint = currentPoint / 60000
        QMessageBox.information(self, "You Lasted?", f"How Long Have I lasted? - {minutePoint}")
    
    def savePosition(self, position):
        # Get the current file URL
        file_url = self.mediaPlayer.media().canonicalUrl().toString()

        # Check if the file URL ends with a supported video format and the state is either Playing or Paused
        if self.mediaPlayer.state() in (QMediaPlayer.PlayingState, QMediaPlayer.PausedState):
            last_position = {
                "position": position,
                "file": file_url,
                "timer_active": self.timer_active,  # Save the timer status
                "timer_set": self.timer_duration
            }
            with open(self.position_file, 'w') as f:
                json.dump(last_position, f)
                
            print("Video position saved (Playing or Paused)")

    def loadLastVideo(self):
        # Load the last video file and position if available
        if os.path.exists(self.position_file):
            with open(self.position_file, 'r') as f:
                last_position = json.load(f)

            file_url = last_position.get("file")
            position = last_position.get("position")
            self.timer_active = last_position.get("timer_active", False)

            if file_url and position is not None:
                filename = os.path.basename(QUrl(file_url).toLocalFile())
                self.setWindowTitle(f"Last Loaded: {filename}")
                self.mediaPlayer.setMedia(QMediaContent(QUrl(file_url)))
                self.mediaPlayer.setPosition(position)

                # Start playing the video automatically
                self.mediaPlayer.play()

                if self.timer_active:
                    self.timer.start(self.timer_duration)                
        else:
            # If no position file exists, open a file dialog to select a video file
            self.loadVideo()

    def loadVideo(self):
        # Open a file dialog to select a video file
        fileDialog = QFileDialog(self)
        fileDialog.setNameFilters(["Videos (*.mp4 *.avi *.mkv)"])
        if fileDialog.exec_():
            fileUrl = fileDialog.selectedUrls()[0]
            self.mediaPlayer.setMedia(QMediaContent(fileUrl))

            # Automatically start playing the video
            self.mediaPlayer.play()

            name = os.path.basename(QUrl(fileUrl).toLocalFile())
            self.setWindowTitle(f"Loaded: {name}")

        else:
            exit()
    
    def stopAndClose(self):
        try:
            current_position = self.mediaPlayer.position()
            self.savePosition(current_position)
            self.mediaPlayer.stop()
            exit()
        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            self.close()

    def closeEvent(self, event):
        position = self.mediaPlayer.position()
        self.savePosition(position)
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())
