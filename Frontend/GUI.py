from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTextEdit,
    QStackedWidget,
    QHBoxLayout,
    QLabel,
    QGridLayout,
    QLineEdit,
    QFrame,
    QSizePolicy,
)
from PyQt5.QtGui import (
    QIcon,
    QFont,
    QColor,
    QMovie,
    QPainter,
    QTextCharFormat,
    QPixmap,
    QTextBlockFormat,
)
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

env_vars = dotenv_values(".env")
assistant_name = env_vars.get("ASSISTANT_NAME", "Assistant")
current_dir = os.getcwd()
old_chat_message = ""
TempDirpath = rf"{current_dir}\Frontend\Files"
GraphicsDirpath = rf"{current_dir}\Frontend\Graphics"


def AnswerModifire(Answer):
    lines = Answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = "\n".join(non_empty_lines)
    return modified_answer


def QueryModifire(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = [
        "what",
        "who",
        "where",
        "when",
        "why",
        "how",
        "is",
        "are",
        "do",
        "does",
        "did",
        "can",
        "could",
        "should",
        "would",
        "will",
        "may",
        "might",
        "shall",
        "has",
        "have",
        "had",
        "am",
        "isn't",
        "aren't",
        "wasn't",
        "weren't",
        "won't",
        "can't",
        "couldn't",
        "shouldn't",
        "wouldn't",
        "must",
        "need",
        "ought",
        "used",
        "to",
        "if",
        "that",
        "which",
        "who's",
        "whose",
        "whom",
        "what's",
        "where's",
        "when's",
        "why's",
        "how's",
    ]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in [".", "?", "!"]:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in [".", "?", "!"]:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
    return new_query.capitalize()


def SetMicrophoneStatus(Command):
    try:
        os.makedirs(os.path.dirname(TempDirpath), exist_ok=True)
        with open(rf"{TempDirpath}\Mic.data", "w", encoding="utf-8") as file:
            file.write(Command)
    except Exception as e:
        print(f"Error setting microphone status: {e}")


def GetMicrophoneStatus():
    try:
        with open(rf"{TempDirpath}\Mic.data", "r", encoding="utf-8") as file:
            Status = file.read()
        return Status
    except Exception as e:
        print(f"Error getting microphone status: {e}")
        return "False"


def SetAssistantStatus(Status):
    try:
        os.makedirs(os.path.dirname(TempDirpath), exist_ok=True)
        with open(rf"{TempDirpath}\Status.data", "w", encoding="utf-8") as file:
            file.write(Status)
    except Exception as e:
        print(f"Error setting assistant status: {e}")


def GetAssistantStatus():
    try:
        with open(rf"{TempDirpath}\Status.data", "r", encoding="utf-8") as file:
            Status = file.read()
        return Status
    except Exception as e:
        print(f"Error getting assistant status: {e}")
        return ""


def MicButtonInitialed():
    SetMicrophoneStatus("False")


def MicButtonClosed():
    SetMicrophoneStatus("True")


def GraphicsDirectoryPath(Filename):
    path = rf"{GraphicsDirpath}\{Filename}"
    return path


def TempDirectoryPath(Filename):
    path = rf"{TempDirpath}\{Filename}"
    return path


def ShowTextToScreen(Text):
    try:
        os.makedirs(os.path.dirname(TempDirpath), exist_ok=True)
        with open(rf"{TempDirpath}\Responses.data", "w", encoding="utf-8") as file:
            file.write(Text)
    except Exception as e:
        print(f"Error showing text to screen: {e}")


class ChatSection(QWidget):

    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)

        self.setStyleSheet("background-color: black;")

        # Allow the widget to expand properly
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add GIF and status label at the bottom
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(10, 10, 10, 10)

        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")

        # Check if GIF file exists before loading
        gif_path = GraphicsDirectoryPath("Jarvis.gif")
        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            max_gif_size_W = 240
            max_gif_size_H = 135
            movie.setScaledSize(QSize(max_gif_size_W, max_gif_size_H))
            self.gif_label.setAlignment(Qt.AlignCenter)
            self.gif_label.setMovie(movie)
            movie.start()
        else:
            self.gif_label.setText("GIF not found")
            self.gif_label.setStyleSheet("color: white; background-color: black;")

        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; border: none;")
        self.label.setAlignment(Qt.AlignCenter)

        bottom_layout.addStretch()
        bottom_layout.addWidget(self.gif_label)
        bottom_layout.addWidget(self.label)
        bottom_layout.addStretch()

        layout.addWidget(bottom_widget)

        # Set text color and formatting
        text_color = QColor(Qt.blue)
        text_color_text = QTextCharFormat()
        text_color_text.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_color_text)

        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)

        self.timer = QTimer(self)
        # Fixed: Method names should be consistent
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.speechRecogText)
        self.timer.start(5)

        self.chat_text_edit.viewport().installEventFilter(self)
        self.setStyleSheet(
            """
            QScrollBar:vertical { 
            background: black; 
            margin: 0px 0px 0px 0px;
            border: none;
            width: 10px;
            }
            QScrollBar::handle:vertical {
            background: white;
            min-height: 20px;
            }
            QScrollBar::add-line:vertical { 
            background: black; 
            subcontrol-position: bottom; 
            subcontrol-origin: margin; 
            height: 10px; 
            }

            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
            border: none;
            background: none;
            color: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
            }
        """
        )

    # Fixed: Method name consistency
    def loadMessages(self):
        global old_chat_message
        try:
            with open(
                TempDirectoryPath("Responses.data"), "r", encoding="utf-8"
            ) as file:
                messages = file.read()
            if messages is None:
                pass
            elif len(messages) <= 1:
                pass
            elif str(old_chat_message) == str(messages):
                pass
            else:
                self.addMessage(message=messages, color="white")
                old_chat_message = messages
        except Exception as e:
            print(f"Error loading messages: {e}")

    # Fixed: Method name consistency
    def speechRecogText(self):
        try:
            with open(TempDirectoryPath("Status.data"), "r", encoding="utf-8") as file:
                messages = file.read()
            self.label.setText(messages)
        except Exception as e:
            print(f"Error reading speech recognition text: {e}")

    def load_icon(self, path, width=60, height=60):
        if hasattr(self, "icon_label") and os.path.exists(path):
            pixmap = QPixmap(path)
            new_pixmap = pixmap.scaled(width, height)
            self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if hasattr(self, "toggled"):
            if self.toggled:
                self.load_icon(GraphicsDirectoryPath("voice.png"), 60, 60)
                MicButtonInitialed()
            else:
                self.load_icon(GraphicsDirectoryPath("mic.png"), 60, 60)
                MicButtonClosed()
            self.toggled = not self.toggled

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        formatm = QTextBlockFormat()
        formatm.setTopMargin(10)
        formatm.setLeftMargin(10)
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.setBlockFormat(formatm)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)


class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)

        gif_label = QLabel()
        gif_path = GraphicsDirectoryPath("Jarvis.gif")

        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            gif_label.setMovie(movie)
            max_gif_size_H = int(screen_width / 16 * 9)
            movie.setScaledSize(QSize(screen_width, max_gif_size_H))
            gif_label.setAlignment(Qt.AlignCenter)
            movie.start()
        else:
            gif_label.setText("GIF not found")
            gif_label.setStyleSheet("color: white; background-color: black;")

        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.icon_label = QLabel()
        mic_path = GraphicsDirectoryPath("Mic_on.png")

        if os.path.exists(mic_path):
            pixmap = QPixmap(mic_path)
            new_pixmap = pixmap.scaled(60, 60)
            self.icon_label.setPixmap(new_pixmap)
        else:
            self.icon_label.setText("Mic Icon")
            self.icon_label.setStyleSheet("color: white; background-color: black;")

        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.toggled = True
        self.toggle_icon()

        # Fixed: Correct event handler assignment
        self.icon_label.mousePressEvent = self.toggle_icon

        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-bottom:0;")

        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        content_layout.setContentsMargins(0, 0, 0, 150)

        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black;")

        self.timer = QTimer(self)
        # Fixed: Method name consistency
        self.timer.timeout.connect(self.speechRecogText)
        self.timer.start(5)

    # Fixed: Method name consistency
    def speechRecogText(self):
        try:
            with open(TempDirectoryPath("Status.data"), "r", encoding="utf-8") as file:
                messages = file.read()
            self.label.setText(messages)
        except Exception as e:
            print(f"Error reading speech recognition text: {e}")

    def load_icon(self, path, width=60, height=60):
        if os.path.exists(path):
            pixmap = QPixmap(path)
            new_pixmap = pixmap.scaled(width, height)
            self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath("Mic_on.png"), 60, 60)
            MicButtonInitialed()
        else:
            self.load_icon(GraphicsDirectoryPath("Mic_off.png"), 60, 60)
            MicButtonClosed()
        self.toggled = not self.toggled


class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        # Main layout with no margins to use full area
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        chat_section = ChatSection()
        layout.addWidget(chat_section)

        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)


class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.initUI()
        self.current_screen = None
        self.stacked_widget = stacked_widget

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)

        home_button = QPushButton()
        home_icon_path = GraphicsDirectoryPath("Home.png")
        if os.path.exists(home_icon_path):
            home_icon = QIcon(home_icon_path)
            home_button.setIcon(home_icon)
        home_button.setText(" Home")
        home_button.setStyleSheet(
            "height:40px; line-height:40px; background-color:white; color: black"
        )

        message_button = QPushButton()
        message_icon_path = GraphicsDirectoryPath("Chats.png")
        if os.path.exists(message_icon_path):
            message_icon = QIcon(message_icon_path)
            message_button.setIcon(message_icon)
        message_button.setText(" Chat")
        message_button.setStyleSheet(
            "height:40px; line-height:40px; background-color:white; color: black"
        )

        minimize_button = QPushButton()
        minimize_icon_path = GraphicsDirectoryPath("Minimize2.png")
        if os.path.exists(minimize_icon_path):
            minimize_icon = QIcon(minimize_icon_path)
            minimize_button.setIcon(minimize_icon)
        minimize_button.setStyleSheet("background-color:white")
        minimize_button.clicked.connect(self.minimizeWindow)

        self.maximize_button = QPushButton()
        maximize_icon_path = GraphicsDirectoryPath("Maximize.png")
        restore_icon_path = GraphicsDirectoryPath("Minimize.png")

        if os.path.exists(maximize_icon_path):
            self.maximize_icon = QIcon(maximize_icon_path)
            self.maximize_button.setIcon(self.maximize_icon)
        if os.path.exists(restore_icon_path):
            self.restore_icon = QIcon(restore_icon_path)

        self.maximize_button.setFlat(True)
        self.maximize_button.setStyleSheet("background-color:white")
        self.maximize_button.clicked.connect(self.maximizeWindow)

        close_button = QPushButton()
        close_icon_path = GraphicsDirectoryPath("Close.png")
        if os.path.exists(close_icon_path):
            close_icon = QIcon(close_icon_path)
            close_button.setIcon(close_icon)
        close_button.setStyleSheet("background-color:white")
        close_button.clicked.connect(self.closeWindow)

        line_frame = QFrame()
        line_frame.setFixedHeight(1)
        line_frame.setFrameShape(QFrame.HLine)
        line_frame.setFrameShadow(QFrame.Sunken)
        line_frame.setStyleSheet("border-color: black;")

        title_label = QLabel(f" {str(assistant_name).capitalize()} AI ")
        title_label.setStyleSheet(
            "color: black; font-size: 18px; background-color:white"
        )

        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)
        layout.addWidget(line_frame)

        self.draggable = True
        self.offset = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        super().paintEvent(event)

    def minimizeWindow(self):
        self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            if hasattr(self, "maximize_icon"):
                self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            if hasattr(self, "restore_icon"):
                self.maximize_button.setIcon(self.restore_icon)

    def closeWindow(self):
        self.parent().close()

    def mousePressEvent(self, event):
        if self.draggable:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            new_pos = event.globalPos() - self.offset
            self.parent().move(new_pos)

    def showMessageScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()
        message_screen = MessageScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(message_screen)
        self.current_screen = message_screen

    def showInitialScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()
        initial_screen = InitialScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(initial_screen)
        self.current_screen = initial_screen


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen()
        message_screen = MessageScreen()

        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)

        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")

        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)


def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    GraphicalUserInterface()
