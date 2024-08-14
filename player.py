import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, Qt, QTimer
from PyQt5.QtGui import QIcon

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

        # Create Play Button
        self.playButton = QPushButton('Play')
        self.playButton.setEnabled(False)
        self.playButton.clicked.connect(self.playVideo)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
        layout.addWidget(self.playButton)

        self.setLayout(layout)

        # Connect mediaPlayer to videoWidget
        self.mediaPlayer.setVideoOutput(videoWidget)

        # Set up the window
        self.setWindowTitle("No Skip Video Player")
        self.setWindowIcon(QIcon("/home/adam178/Programmings/no-skip-video/icon.png"))
        self.setGeometry(100, 100, 800, 600)
        
        # Timer to stop video after a specific time
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.stopAndClose)
        self.timer_duration = 300000  # Duration in milliseconds (e.g., 60000 ms = 60 seconds)

        # Load the last video file
        self.loadLastVideo()
                
    def closeEvent(self, event):
        position = self.mediaPlayer.position()
        self.savePosition(position)
        event.accept()

    def loadLastVideo(self):
        # Load the last video file and position if available
        if os.path.exists(self.position_file):
            with open(self.position_file, 'r') as f:
                last_position = json.load(f)

            file_url = last_position.get("file")
            position = last_position.get("position")

            if file_url and position:
                self.mediaPlayer.setMedia(QMediaContent(QUrl(file_url)))
                self.mediaPlayer.setPosition(position)
                filename = os.path.basename(file_url)
                self.playButton.setEnabled(True)

                # Start playing the video automatically
                self.mediaPlayer.play()
                self.playButton.setText("Pause")
                
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
            self.playButton.setEnabled(True)

            # Automatically start playing the video
            self.mediaPlayer.play()
            self.playButton.setText("Pause")
        else:
            exit()

    def playVideo(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
            self.playButton.setText("Play")
        else:
            self.mediaPlayer.play()
            self.playButton.setText("Pause")

    def savePosition(self, position):
        # Define supported video formats
        supported_formats = [".mp4", ".avi", ".mkv", ".mov", ".flv"]

        # Get the current file URL
        file_url = self.mediaPlayer.media().canonicalUrl().toString()
        
        # Check if the file URL ends with a supported video format
        if any(file_url.lower().endswith(fmt) for fmt in supported_formats):
            # Save the current position and file to a file
            if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
                last_position = {
                    "position": position,
                    "file": file_url
                }
                with open(self.position_file, 'w') as f:
                    json.dump(last_position, f)
                    
                print("Video Stopped Point Recorded")
        else:
            # Optionally, handle the case where the file is not a supported video
            print("Error: The file is not a supported video format.")

    def keyPressEvent(self, event):
        # Check if Shift + N is pressed
        if event.key() == Qt.Key_N and event.modifiers() & Qt.ShiftModifier:
            self.loadVideo()
        else:
            super().keyPressEvent(event)
            
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())