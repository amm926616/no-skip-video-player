### Steps to Compile

1. **Create a `.pro` File**:
    
    Create a `.pro` file for the project:
    
    pro
    
    Copy code
    
    `QT += widgets multimedia multimediawidgets  TARGET = SimpleVideoPlayer TEMPLATE = app  SOURCES += main.cpp`
    
2. **Run qmake**:
    
    Generate a Makefile using `qmake`:
    
    bash
    
    Copy code
    
    `qmake SimpleVideoPlayer.pro`
    
3. **Compile with make**:
    
    Compile the project with:
    
    bash
    
    Copy code
    
    `make`
    
4. **Run the Application**:
    
    If the compilation is successful, run the application:
    
    bash
    
    Copy code
    
    `./SimpleVideoPlayer`
    

This will open a simple window where you can load and play a video file.