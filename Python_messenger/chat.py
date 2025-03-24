from tkinter import *
from socket import *

def messageFilter(messageText):
    """
    Lọc bỏ các dòng trắng không cần thiết ở cuối chuỗi,
    trả về một chuỗi đã được làm sạch.
    """
    EndFiltered = ''
    for i in range(len(messageText)-1, -1, -1):
        if messageText[i] != '\n':
            EndFiltered = messageText[0:i+1]
            break
    for i in range(len(EndFiltered)):
        if EndFiltered[i] != "\n":
            return EndFiltered[i:] + '\n'
    return ''

def displayLocalMessage(chatBox, messageText):
    """
    Hiển thị tin nhắn từ người dùng.
    """
    if messageText.strip():
        chatBox.config(state=NORMAL)
        LineNumber = chatBox.index('end-1c')
        chatBox.insert(END, "YOU: " + messageText)
        chatBox.tag_add("YOU", LineNumber, LineNumber + " lineend")
        chatBox.tag_config("YOU", foreground="#AA3939", font=("Courier", 12, "bold"), justify="right")
        chatBox.config(state=DISABLED)
        chatBox.yview(END)

def displayRemoteMessage(chatBox, messageText):
    """
    Hiển thị tin nhắn từ người dùng khác.
    """
    if messageText.strip():
        chatBox.config(state=NORMAL)
        LineNumber = chatBox.index('end-1c')
        chatBox.insert(END, "OTHER: " + messageText)
        chatBox.tag_add("OTHER", LineNumber, LineNumber + " lineend")
        chatBox.tag_config("OTHER", foreground="#255E69", font=("Courier", 12, "bold"))
        chatBox.config(state=DISABLED)
        chatBox.yview(END)

def getConnectionInfo(chatBox, messageText):
    """
    Hiển thị thông tin kết nối.
    """
    if messageText.strip():
        chatBox.config(state=NORMAL)
        chatBox.insert(END, messageText + '\n')
        chatBox.config(state=DISABLED)
        chatBox.yview(END)
