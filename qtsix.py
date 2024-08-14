import sys
import os
import json
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QUrl, Qt, QTimer
from PyQt6.QtGui import QIcon

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()

        # Define the path to store resume history
        self.data_dir = os.path.expanduser("~/.local/share/no-skip-video-player/")
        self.position_file = os.path.join(self.data_dir, "last_position.json")

        # Ensure the directory exists
        os.makedirs(self.data_dir, exist_ok=True)

        # Initialize QMediaPlayer and QAudioOutput
        self.audioOutput = QAudioOutput()
        self.mediaPlayer = QMediaPlayer()
        self.mediaPlayer.setAudioOutput(self.audioOutput)
        
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
        self.setWindowTitle("No-Skip Video Player")
        self.setWindowIcon(QIcon("icon.png"))
        self.setGeometry(100, 100, 500, 400)

        # Timer to stop video after a specific time
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.stopAndClose)
        self.timer_duration = 6000  # Duration in milliseconds

        # Load the last video file
        self.loadLastVideo()

    def closeEvent(self, event):
        position = self.mediaPlayer.position()
        self.savePosition(position)
        
        # Stop the media player and release resources
        self.mediaPlayer.stop()
        self.mediaPlayer.setSource(QUrl())  # Unload media
        self.mediaPlayer.deleteLater()
        
        event.accept()
        
    def loadLastVideo(self):
        # Load the last video file and position if available
        if os.path.exists(self.position_file):
            with open(self.position_file, 'r') as f:
                last_position = json.load(f)

            file_url = last_position.get("file")
            position = last_position.gNet("position")

            if file_url and position:
                self.mediaPlayer.setSource(QUrl(file_url))

                # Connect to mediaStatusChanged to set the position once the media is loaded
                def set_position_when_loaded(media_status):
                    if media_status == QMediaPlayer.MediaStatus.LoadedMedia:
                        self.mediaPlayer.setPosition(position)
                        self.mediaPlayer.play()
                        self.playButton.setText("Pause")
                        self.timer.start(self.timer_duration)

                self.mediaPlayer.mediaStatusChanged.connect(set_position_when_loaded)

                self.playButton.setEnabled(True)
            else:
                self.loadVideo()
        else:
            # If no position file exists, open a file dialog to select a video file
            self.loadVideo()


    def loadVideo(self):
        # Open a file dialog to select a video file
        fileDialog = QFileDialog(self)
        fileDialog.setNameFilters(["Videos (*.mp4 *.avi *.mkv)"])
        if fileDialog.exec():
            fileUrl = fileDialog.selectedUrls()[0]
            self.mediaPlayer.setSource(fileUrl)
            self.playButton.setEnabled(True)
            filename = fileUrl.fileName()

            # Set the window title to the filename
            self.setWindowTitle(f"No-Skip Video Player - {filename}")

            # Automatically start playing the video
            self.mediaPlayer.play()
            self.playButton.setText("Pause")
        else:
            self.close()


    def playVideo(self):
        if self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.mediaPlayer.pause()
            self.playButton.setText("Play")
        else:
            self.mediaPlayer.play()
            self.playButton.setText("Pause")

    def savePosition(self, position):
        # Get the current file URL
        file_url = self.mediaPlayer.source().toString()
        print("IN saving ", file_url)
        print(position)
        
        if self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            last_position = {
                "position": position,
                "file": file_url
            }
            with open(self.position_file, 'w') as f:
                json.dump(last_position, f)
                
            print("Video Stopped Point Recorded")

    def keyPressEvent(self, event):
        # Check if Shift + N is pressed
        if event.key() == Qt.Key.Key_N and event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            self.loadVideo()
        else:
            super().keyPressEvent(event)
            
    def stopAndClose(self):
        try:
            current_position = self.mediaPlayer.position()
            self.savePosition(current_position)
            self.mediaPlayer.stop()
        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            # Explicitly release media player resources
            self.mediaPlayer.setSource(QUrl())  # Unload media
            self.mediaPlayer.deleteLater()
            
            self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())
