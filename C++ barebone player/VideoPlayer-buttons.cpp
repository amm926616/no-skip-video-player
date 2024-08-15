#include <QApplication>
#include <QWidget>
#include <QVBoxLayout>
#include <QPushButton>
#include <QFileDialog>
#include <QMediaPlayer>
#include <QVideoWidget>
#include <QUrl>
#include <QHBoxLayout>

class VideoPlayer : public QWidget {
    Q_OBJECT

public:
    VideoPlayer(QWidget *parent = nullptr) : QWidget(parent) {
        // Initialize QMediaPlayer
        mediaPlayer = new QMediaPlayer(this);

        // Create Video Widget
        QVideoWidget *videoWidget = new QVideoWidget(this);

        // Create buttons
        QPushButton *loadButton = new QPushButton("Load Video", this);
        QPushButton *forwardButton = new QPushButton("Forward 3s", this);
        QPushButton *backwardButton = new QPushButton("Backward 3s", this);

        // Connect buttons to slots
        connect(loadButton, &QPushButton::clicked, this, &VideoPlayer::loadVideo);
        connect(forwardButton, &QPushButton::clicked, this, &VideoPlayer::seekForward);
        connect(backwardButton, &QPushButton::clicked, this, &VideoPlayer::seekBackward);

        // Set up the layout
        QVBoxLayout *mainLayout = new QVBoxLayout(this);
        mainLayout->addWidget(videoWidget);
        mainLayout->addWidget(loadButton);

        QHBoxLayout *seekLayout = new QHBoxLayout();
        seekLayout->addWidget(backwardButton);
        seekLayout->addWidget(forwardButton);

        mainLayout->addLayout(seekLayout);

        setLayout(mainLayout);

        // Connect mediaPlayer to videoWidget
        mediaPlayer->setVideoOutput(videoWidget);

        // Set up the window
        setWindowTitle("Video Player with Seeking");
        setGeometry(100, 100, 600, 400);
    }

private slots:
    void loadVideo() {
        // Open a file dialog to select a video file
        QString fileUrl = QFileDialog::getOpenFileName(this, "Open Video", "", "Videos (*.mp4 *.avi *.mkv)");
        if (!fileUrl.isEmpty()) {
            mediaPlayer->setMedia(QUrl::fromLocalFile(fileUrl));
            mediaPlayer->play();
        }
    }

    void seekForward() {
        // Seek forward by 3 seconds
        mediaPlayer->setPosition(mediaPlayer->position() + 3000);
    }

    void seekBackward() {
        // Seek backward by 3 seconds
        mediaPlayer->setPosition(mediaPlayer->position() - 3000);
    }

private:
    QMediaPlayer *mediaPlayer;
};

#include "main.moc"

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    VideoPlayer player;
    player.show();
    return app.exec();
}
