#include <QApplication>
#include <QWidget>
#include <QVBoxLayout>
#include <QPushButton>
#include <QFileDialog>
#include <QMediaPlayer>
#include <QVideoWidget>
#include <QUrl>

class VideoPlayer : public QWidget {
    Q_OBJECT

public:
    VideoPlayer(QWidget *parent = nullptr) : QWidget(parent) {
        // Initialize QMediaPlayer
        mediaPlayer = new QMediaPlayer(this);

        // Create Video Widget
        QVideoWidget *videoWidget = new QVideoWidget(this);

        // Create Play Button
        QPushButton *loadButton = new QPushButton("Load Video", this);
        connect(loadButton, &QPushButton::clicked, this, &VideoPlayer::loadVideo);

        // Set up the layout
        QVBoxLayout *layout = new QVBoxLayout(this);
        layout->addWidget(videoWidget);
        layout->addWidget(loadButton);

        setLayout(layout);

        // Connect mediaPlayer to videoWidget
        mediaPlayer->setVideoOutput(videoWidget);

        // Set up the window
        setWindowTitle("Simple Video Player");
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
