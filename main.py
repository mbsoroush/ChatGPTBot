import os
import openai
import tiktoken
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QColor, QTextCursor, QKeyEvent
from PyQt5.QtCore import QTimer, Qt, QObject, pyqtSignal
from time import sleep


class ChatBot2:
    def __init__(self, message):
        self.messages = [
            { "role": "system", "content": message }
        ]

    def chat(self, prompt):
        #prompt = input("You: ")

        self.messages.append(
            { "role": "user", "content": prompt}
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages = self.messages,
            temperature = 0.8
        )

        answer = response.choices[0]['message']['content']


        self.messages.append(
           { "role": "assistant", "content": answer}
        )

        tokens = self.num_tokens_from_messages(self.messages)
        #print(f"Total tokens: {tokens}")

        if tokens > 4000:
            #print("WARNING: Number of tokens exceeds 4000. Truncating messages.")
            self.messages = self.messages[2:]

        return answer


    def num_tokens_from_messages(self, messages, model="gpt-3.5-turbo"):
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        if model == "gpt-3.5-turbo":  # note: future models may deviate from this
            num_tokens = 0
            for message in messages:
                num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
                for key, value in message.items():
                    num_tokens += len(encoding.encode(value))
                    if key == "name":  # if there's a name, the role is omitted
                        num_tokens += -1  # role is always required and always 1 token
            num_tokens += 2  # every reply is primed with <im_start>assistant
            return num_tokens
        else:
            raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.""")

class ChatBot(QObject):
    message_received = pyqtSignal(str, str)

    def __init__(self, name):
        super().__init__()
        self.name = name

    def chat(self, user, message):
        self.message_received.emit(user, message)
        

class ChatWindow(QWidget):
    message_received = pyqtSignal(str, str)

    def __init__(self, name):
        super().__init__()
        self.name = name
        self.init_ui()

    def init_ui(self):
        self.chat_box = QTextEdit(self)
        self.chat_box.setReadOnly(True)
        self.chat_box.setFont(QFont("Arial", 12))

        self.input_box = QTextEdit(self)
        self.input_box.setFont(QFont("Arial", 12))

        self.send_button = QPushButton("Send", self)
        self.send_button.setFont(QFont("Arial", 12))
        self.send_button.clicked.connect(self.send_message)

        layout = QVBoxLayout()
        layout.addWidget(self.chat_box)
        # Create a widget for user input
        input_widget = QWidget()
        input_layout = QHBoxLayout()
        input_widget.setLayout(input_layout)
        input_layout.addWidget(self.input_box)
        input_layout.addWidget(self.send_button)
        input_widget.setFixedHeight(60)
        layout.addWidget(input_widget)

        self.setLayout(layout)

    def send_message(self):
        message = self.input_box.toPlainText().strip()
        if message:
            self.append_message("You", message)
            self.input_box.clear()
            self.reply_message(message)
            #self.message_received.emit(self.name, message)

    def reply_message(self, message):
        self.append_message("Bot")
        self.typing_animation(bot.chat(message))

    def typing_animation(self, message):
        for char in message:
            self.append_message_rest_of_sentence(char)
            sleep(0.07)
            QApplication.processEvents()

    def append_message(self, sender, message=""):
        self.chat_box.append(f"{sender}: {message}")

    def append_message_rest_of_sentence(self, message):
        self.chat_box.moveCursor(QTextCursor.End)
        if message == " ":
            self.chat_box.insertPlainText(" ")
        else:
            self.chat_box.insertHtml(message)

    def scroll_to_bottom(self):
        scrollbar = self.chat_box.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

class ChatApplication(QWidget):
    def __init__(self):
        super().__init__()
        self.chat_windows = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Chat Application")
        self.resize(800, 600)

        self.tab_widget = QTabWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

    def add_chat_window(self, name):
        if name not in self.chat_windows:
            chat_window = ChatWindow(name)
            chat_window.message_received.connect(self.send_message_to_bot)
            self.chat_windows.append(chat_window)
            self.tab_widget.addTab(chat_window, name)

    def send_message_to_bot(self, sender, message):
      
        #print(sender)
        bot.chat(message)

        
        # chat_window.append_message("Bot", response)


if __name__ == '__main__':
    openai.api_key = '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'
    bot = ChatBot2("You are an assistant that always answers correctly. If not sure, say 'I don't know'.")
    app = QApplication(sys.argv)
    window = ChatApplication()
    window.add_chat_window("User 1")
    window.add_chat_window("User 2")
    window.add_chat_window("User 3")
    window.add_chat_window("User 4")
    window.show()
    sys.exit(app.exec_())
