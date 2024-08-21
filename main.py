#! /usr/bin/env python

import sys, os, json
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QInputDialog, QMessageBox, QFileDialog, QDockWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, Qt, QTimer
from PyQt5.QtGui import QIcon, QTransform
from easy_json import get_value, edit_value, check_file_path

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        # for .json file location
        self.config_file = "/home/adam178/.local/share/no-skip-video-player/last_position.json"

        # wtf always on top worked!
        check_file_path(self.config_file)
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
        self.videoWidget = QVideoWidget()

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.videoWidget)
        self.setLayout(layout)

        # Connect mediaPlayer to videoWidget
        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.mediaStatusChanged.connect(self.handleMediaStatusChanged)

        # Set up the window
        self.setWindowTitle("No Skip Video Player")
        self.setWindowIcon(QIcon("/home/adam178/MyGitRepos/no-skip-video-player/icon.png"))
        self.setGeometry(100, 100, 800, 450)

        # Timer to stop video after a specific time
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.stopAndClose)
        self.timer_active = get_value("timer_active", self.config_file)
        self.timer_duration = get_value("timer_set", self.config_file)  # Default to 5 minutes (in milliseconds)
        
        # filename for addition << emergency bad code
        self.filename = ""

        # Load the last video file
        self.loadLastVideo()

        # for alwaysontop global key, implement later
        # with keyboard.Listener(on_press=self.on_presses, on_release=self.on_release) as listener:
        #     listener.join()

    # def on_presses(self, key):
    #     try:
    #         if key.char == 'a' and keyboard.Controller().shift:
    #             self.setAlwaysOnTop()
    #     except AttributeError:
    #         pass  # Handle other non-character keys here if needed

    # def on_release(self, key):
    #     # Stop listener on `esc` key press
    #     if key == keyboard.Key.esc:
    #         return False
    
    def mirrorVideo(self):
        transform = QTransform().scale(-1, 1)  # Horizontal flip
        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.videoWidget.setTransform(transform)


    def setAlwaysOnTop(self):
        if self.alwaysOnTopState:
            self.alwaysOnTopState = False
        else:
            self.alwaysOnTopState = True
        QMessageBox.information(self, 
                                "Always On Top State",  # Title of the message box
                                f"alwaysOnTopState: {self.alwaysOnTopState}")  # Text to display

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
        message = ""
        if (self.timer_active == True):
            self.timer_active = False
            self.timer.stop()
        else:
            self.timer.start(self.timer_duration)
            self.timer_active = True
        
        self.setTitle(self.filename)

    def setSleepTimer(self):
        # Popup window to set timer
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
        # Get the current file URL
        file_url = self.mediaPlayer.media().canonicalUrl().toString()

        # Check if the file URL ends with a supported video format and the state is either Playing or Paused
        if self.mediaPlayer.state() in (QMediaPlayer.PlayingState, QMediaPlayer.PausedState):
            last_position = {
                "position": position,
                "file": file_url,
                "timer_active": self.timer_active,  # Save the timer status
                "timer_set": self.timer_duration,
                "alwaysOnTopState": self.alwaysOnTopState
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
                self.filename = filename
                self.setTitle(filename)
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
            self.filename = name
            self.setTitle(name)

        else:
            exit()
            
    def setTitle(self, filename):
        timerState = ""
        if self.timer_active:
            timerState = "TimerOn"
        else:
            timerState = "TimerOff"     
        self.setWindowTitle(f"{timerState}:{int(self.timer_duration/1000)}s - {filename}")
               
    
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
