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
        self.videoWidget = QVideoWidget()

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.videoWidget)
        self.setLayout(layout)

        # Connect mediaPlayer to videoWidget
        self.mediaPlayer.setVideoOutput(self.videoWidget)

        # Set up the window
        self.setWindowTitle("No Skip Video Player")
        self.setWindowIcon(QIcon("/home/adam178/Programmings/no-skip-video/icon.png"))
        
        # Connect the signal to adjust window size when video is available
        self.mediaPlayer.videoAvailableChanged.connect(self.adjustWindowSize)

        # Load the last video file
        self.loadLastVideo()

        # Make the window always on top after setup
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

    def adjustWindowSize(self):
        if self.mediaPlayer.isVideoAvailable():
            # Adjust window size based on the video size
            self.resize(self.videoWidget.sizeHint())

    def loadLastVideo(self):
        if os.path.exists(self.position_file):
            with open(self.position_file, 'r') as f:
                last_position = json.load(f)

            file_url = last_position.get("file")
            position = last_position.get("position")
            self.timer_active = last_position.get("timer_active", False)

            if file_url and position is not None:
                self.mediaPlayer.setMedia(QMediaContent(QUrl(file_url)))
                self.mediaPlayer.setPosition(position)
                self.setWindowTitleFromFilename(file_url)  # Set the window title

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
            self.setWindowTitleFromFilename(fileUrl.toString())  # Set the window title

            self.mediaPlayer.play()
        else:
            exit()

    def setWindowTitleFromFilename(self, file_url):
        filename = os.path.basename(QUrl(file_url).toLocalFile())
        self.setWindowTitle(f"No Skip Video Player - {filename}")
