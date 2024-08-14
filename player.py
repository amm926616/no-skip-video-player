import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QIcon

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()

        # File to save the last position
        self.position_file = "last_position.json"
        
        # Initialize QMediaPlayer
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        
        # Create Video Widget
        videoWidget = QVideoWidget()

        # Create Play Button
        self.playButton = QPushButton('Play')
        self.playButton.setEnabled(False)
        self.playButton.clicked.connect(self.playVideo)

        # Create a label to show the video status
        self.statusLabel = QLabel()
        self.statusLabel.setAlignment(Qt.AlignCenter)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
        layout.addWidget(self.playButton)
        layout.addWidget(self.statusLabel)

        self.setLayout(layout)

        # Connect mediaPlayer to videoWidget
        self.mediaPlayer.setVideoOutput(videoWidget)

        # Disable seeking by blocking position change
        self.mediaPlayer.positionChanged.connect(self.disableSeeking)

        # Save position when closing
        self.mediaPlayer.positionChanged.connect(self.savePosition)

        # Set up the window
        self.setWindowTitle("No-Skip Video Player")
        self.setWindowIcon(QIcon("icon.png"))  # Add this line to set the window icon
        self.setGeometry(100, 100, 800, 600)

        # Load the video file
        self.loadVideo()

    def loadVideo(self):
        # Open a file dialog to select a video file
        fileDialog = QFileDialog(self)
        fileDialog.setNameFilters(["Videos (*.mp4 *.avi *.mkv)"])
        if fileDialog.exec_():
            fileUrl = fileDialog.selectedUrls()[0]
            self.mediaPlayer.setMedia(QMediaContent(fileUrl))
            self.playButton.setEnabled(True)
            self.statusLabel.setText(f"Loaded: {fileUrl.fileName()}")

            # Check if there's a saved position
            self.resumePosition()

            # Automatically start playing the video
            self.mediaPlayer.play()
            self.playButton.setText("Pause")  # Update button text to reflect the current state

        else:
            exit()

    def playVideo(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
            self.playButton.setText("Play")
        else:
            self.mediaPlayer.play()
            self.playButton.setText("Pause")

    def disableSeeking(self, position):
        # Disable seeking by resetting the position to the current position
        if abs(position - self.mediaPlayer.position()) > 1000:  # If attempted seek detected
            self.mediaPlayer.setPosition(self.mediaPlayer.position())

    def savePosition(self, position):
        # Save the current position to a file
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            last_position = {
                "position": position,
                "file": self.mediaPlayer.media().canonicalUrl().toString()
            }
            with open(self.position_file, 'w') as f:
                json.dump(last_position, f)

    def resumePosition(self):
        # Resume from the last saved position if available
        if os.path.exists(self.position_file):
            with open(self.position_file, 'r') as f:
                last_position = json.load(f)

            if last_position.get("file") == self.mediaPlayer.media().canonicalUrl().toString():
                self.mediaPlayer.setPosition(last_position.get("position"))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())
