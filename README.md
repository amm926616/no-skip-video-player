No Skip Video Player in Python (PyQt)

A minimalist, no-skip video experience.

Like eating a whole cake — no skipping allowed.
This player encourages full consumption: from start to finish, no fast-forwarding.
✨ Features

    ❌ No seeking — You have to watch the video entirely.

    ⏲️ Sleep Timer — Automatically stop playback after a set time.

    🔁 Resume playback — Starts from where you left off, even after closing.

    🎥 Fullscreen toggle — Pure video mode without distractions.

    📁 Toolbar with icons — Optional button-based control (icons bundled or from theme).

    💾 Auto-save state — File and position saved to ~/.config/no-skip-video-player/config.json.

    🖥️ Cross-platform — Works on Linux, Windows, and macOS with Python and PyQt5.

🎮 Shortcuts
Action	Shortcut
Load video	Shift + N
Set sleep timer	Shift + T
Toggle timer ON/OFF	Ctrl + T
Show current position	Shift + I
Toggle always on top	Shift + A
Toggle fullscreen	F or Ctrl + F
Play/Pause video	Space
Quit	Ctrl + Q
🗃️ Config Storage

Configuration and state are saved to:

~/.config/no-skip-video-player/config.json

This includes:

    Last played file

    Playback position

    Timer status and duration

    Fullscreen and "Always on top" settings

🖼️ Icons

To ensure toolbar icons work across platforms:

    You can bundle your own PNG icons in an icons/ folder.

    Replace QIcon.fromTheme(...) with QIcon("icons/icon-name.png").

    Or install a full icon theme (e.g. Adwaita or Papirus) on Linux.

📝 Tip

To enhance your workflow:

    Create a desktop shortcut or script launcher.

    Bind it to a global hotkey (e.g., with AutoHotKey on Windows or custom shortcuts on GNOME/KDE).

🚧 Requirements

    Python 3.7+

    PyQt5 (pip install PyQt5)

Let me know if you'd like a requirements.txt or packaged version (e.g., .deb, .exe, or .app).