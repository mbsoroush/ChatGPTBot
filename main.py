"""
Mohammad Bagher Soroosh - 400130273
Alireza Naghavi - 400130523
Ali Shojaeian - 400130303
"""


from ui import *

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ChatApplication()
    window.add_chat_window("User 1")
    window.add_chat_window("User 2")
    window.add_chat_window("User 3")
    window.add_chat_window("User 4")
    window.show()
    sys.exit(app.exec_())