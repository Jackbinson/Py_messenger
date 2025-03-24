import socket
import threading
import tkinter as tk
import pyaudio
import speech_recognition as sr
from tkinter import simpledialog, Toplevel, Button, messagebox

client = None  # Global socket connection
AUDIO_FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

def open_emoji_picker():
    emoji_window = Toplevel(root)
    emoji_window.title("Chọn Emoji")
    emoji_list = ["😊", "😂", "❤️", "👍", "😢", "🎉", "🔥", "🙌"]
    for emo in emoji_list:
        Button(emoji_window, text=emo, command=lambda e=emo: insert_emoji(e)).pack(side=tk.LEFT)

def insert_emoji(emoji_char):
    message_box.insert(tk.END, emoji_char)

def connect_to_server():
    global client, send_button
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(10)
        client.connect((server_ip, 9003))
        client.settimeout(None)
        client.send(username.encode('utf-8'))
        send_button.config(state=tk.NORMAL)
        voice_button.config(state=tk.NORMAL)
        reconnect_button.pack_forget()

        chat_box.config(state=tk.NORMAL)
        chat_box.delete("1.0", tk.END)
        chat_box.config(state=tk.DISABLED)
    
        threading.Thread(target=receive_messages, daemon=True).start()

    except Exception as e:
        messagebox.showerror("Connection Error", f"Could not connect to server: {e}")
        reconnect_button.pack(pady=5)

def receive_messages():
    global client
    while client:
        try:
            message = client.recv(1024).decode('utf-8')
            if not message:
                raise ConnectionResetError  # Simulate a clean disconnect

            chat_box.config(state=tk.NORMAL)
            chat_box.insert(tk.END, message + "\n")
            chat_box.yview(tk.END)
            chat_box.config(state=tk.DISABLED)

        except (BlockingIOError, socket.timeout):
            continue
        except (ConnectionResetError, BrokenPipeError):
            messagebox.showerror("Error", "Lost connection to server.")
            close_connection()
            reconnect_button.pack(pady=5)
            break
        except Exception as e:
            print(f"[Client] Error in receive_messages: {e}")
            break

def send_message(event=None):
    global client
    message = message_box.get("1.0", tk.END).strip()
    if message:
        if len(message) > 500:
            messagebox.showwarning("Warning", "Message too long (max 500 characters).")
            return
        try:
            if client:
                client.send(message.encode('utf-8'))
                message_box.delete("1.0", tk.END)
        except Exception as e:
            print(f"[Client] Error sending message: {e}")
            close_connection()
            reconnect_button.pack(pady=5)

def check_microphone():
    """Check if a microphone is available before recording."""
    audio = pyaudio.PyAudio()
    try:
        device_info = audio.get_default_input_device_info()
        return device_info is not None
    except:
        return False

def record_and_transcribe():
    """Record audio and transcribe using Google and Sphinx (offline fallback)."""
    if not check_microphone():
        messagebox.showerror("Microphone Error", "No microphone detected!")
        return
    
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            messagebox.showinfo("Voice Input", "Listening...")
            audio_data = recognizer.listen(source, timeout=8, phrase_time_limit=10)
            try:
                text = recognizer.recognize_google(audio_data, language="vi-VN")
            except sr.RequestError:
                messagebox.showerror("Voice Error", "Google API connection failed, trying offline recognition...")
                text = recognizer.recognize_sphinx(audio_data, language="vi-VN")

            message_box.insert(tk.END, text)
            send_message()
        except sr.UnknownValueError:
            messagebox.showerror("Voice Error", "Could not understand your voice.")
        except Exception as e:
            messagebox.showerror("Voice Error", f"Error: {e}")

def close_connection():
    global client
    if client:
        client.close()
        client = None
    send_button.config(state=tk.DISABLED)
    voice_button.config(state=tk.DISABLED)

def exit_chat():
    close_connection()
    root.quit()

def reconnect():
    reconnect_button.pack_forget()
    connect_to_server()

root = tk.Tk()
root.withdraw()
server_ip = simpledialog.askstring("Server IP", "Enter Server IP Address:")
if not server_ip:
    exit()
username = simpledialog.askstring("Username", "Enter your name:")
if not username:
    exit()

root.deiconify()
root.title(f"Chat Client - {username}")
root.geometry("400x500")

chat_box = tk.Text(root, state=tk.DISABLED, height=20, width=50)
chat_box.pack(padx=10, pady=5)
chat_box.tag_config("old_msg", foreground="gray")

message_box = tk.Text(root, height=3, width=40)
message_box.pack(padx=10, pady=5)
message_box.bind("<Return>", lambda event: send_message())

button_frame = tk.Frame(root)
button_frame.pack()

send_button = tk.Button(button_frame, text="Send", command=send_message, state=tk.DISABLED)
send_button.pack(side=tk.LEFT, padx=4)

emoji_button = tk.Button(button_frame, text="😊", command=open_emoji_picker)
emoji_button.pack(side=tk.LEFT, padx=4)

voice_button = tk.Button(button_frame, text="🎤", command=record_and_transcribe, state=tk.DISABLED)
voice_button.pack(side=tk.LEFT, padx=4)

exit_button = tk.Button(button_frame, text="Exit", command=exit_chat)
exit_button.pack(side=tk.LEFT, padx=4)

reconnect_button = tk.Button(root, text="Reconnect", command=reconnect)
reconnect_button.pack_forget()

connect_to_server()

root.mainloop()