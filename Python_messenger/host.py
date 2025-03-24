import socket
import threading
import tkinter as tk
import mysql.connector
import os
import emoji
import speech_recognition as sr
from tkinter import messagebox

# === Configurations ===
HOST = "26.243.24.127"
PORT = 9003
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "xuanhungduong2005",
    "database": "messages_db",
    "pool_name": "mypool",
    "pool_size": 5
}

# === Directory for Voice Messages ===
VOICE_DIR = "voice_messages"
os.makedirs(VOICE_DIR, exist_ok=True)

# === Database Connection Setup ===
try:
    db_pool = mysql.connector.pooling.MySQLConnectionPool(**DB_CONFIG)
except mysql.connector.Error as err:
    print("[Server] Database Pool Error:", err)
    exit()

def get_db_connection():
    """ Get a database connection from the pool. """
    try:
        return db_pool.get_connection()
    except mysql.connector.Error as err:
        print("[Server] DB Connection Error:", err)
        return None

def create_table():
    """ Creates the message table if it does not exist. """
    db = get_db_connection()
    if db:
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.commit()
        cursor.close()
        db.close()

def fetch_old_messages():
    """ Fetch old messages from the database. """
    db = get_db_connection()
    if db:
        cursor = db.cursor()
        cursor.execute("SELECT username, message FROM messages ORDER BY timestamp ASC")
        messages = cursor.fetchall()
        cursor.close()
        db.close()
        return messages
    return []

def save_message(username, message):
    """ Save messages to the database. """
    db = get_db_connection()
    if db:
        try:
            cursor = db.cursor()
            cursor.execute("INSERT INTO messages (username, message) VALUES (%s, %s)", (username, message))
            db.commit()
        except mysql.connector.Error as err:
            print("[Server] Error saving message:", err)
        finally:
            cursor.close()
            db.close()

# === Socket Server Setup ===
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
clients = {}

def update_client_count():
    """ Update the number of connected clients. """
    client_count_label.config(text=f"Online: {len(clients)}")

def display_message(sender, message_text, color):
    """ Display messages in the GUI. """
    chat_box.config(state=tk.NORMAL)
    chat_box.insert(tk.END, f"{sender}: {message_text}\n", sender)
    chat_box.tag_config(sender, foreground=color, font=("Courier", 12, "bold"))
    chat_box.config(state=tk.DISABLED)
    chat_box.yview(tk.END)

def broadcast(message):
    """ Send a message to all connected clients. """
    for client in list(clients.keys()):
        try:
            client.sendall(message.encode('utf-8'))
        except:
            handle_disconnection(client)

def transcribe_audio(filename):
    """ Convert voice message to text using Speech Recognition. """
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(filename) as source:
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data, language="vi-VN")
    except sr.UnknownValueError:
        return "[Không thể nhận diện giọng nói]"
    except sr.RequestError:
        return "[Lỗi kết nối dịch vụ nhận diện giọng nói]"

def handle_disconnection(client):
    """ Handle client disconnections. """
    if client in clients:
        username = clients[client]
        del clients[client]
        update_client_count()
        display_message("SYSTEM", f"{username} left chat.", "red")
        broadcast(f"SYSTEM: {username} left chat.")
    client.close()

def handle_client(conn, addr):
    """ Handle incoming client connections. """
    try:
        conn.settimeout(10)  # Set timeout for initial connection
        username = conn.recv(1024).decode('utf-8').strip()
        if not username:
            conn.close()
            return

        clients[conn] = username
        update_client_count()
        display_message("SYSTEM", f"{username} joined chat", "#255E69")
        broadcast(f"SYSTEM: {username} joined chat.")

        # Send old messages to the new client
        for user, msg in fetch_old_messages():
            conn.sendall(f"{user}: {msg}\n".encode('utf-8'))

        conn.settimeout(None)  # Remove timeout for normal operation

        while True:
            try:
                header = conn.recv(1024).decode('utf-8').strip()
                if not header:
                    break

                if header == "VOICE_MESSAGE":
                    filename = f"{VOICE_DIR}/{username}_{threading.get_ident()}.wav"
                    with open(filename, "wb") as f:
                        while True:
                            data = conn.recv(4096)
                            if data == b"END":
                                break
                            f.write(data)

                    transcribed_text = transcribe_audio(filename)
                    display_message(username, transcribed_text, "blue")
                    broadcast(f"{username}: {transcribed_text}")
                    save_message(username, transcribed_text)
                else:
                    message_with_emoji = emoji.emojize(header, language='alias')
                    display_message(username, message_with_emoji, "#255E69")
                    broadcast(f"{username}: {message_with_emoji}")
                    save_message(username, message_with_emoji)
            except (socket.timeout, ConnectionResetError):
                break
    except Exception as e:
        print(f"[Server] Error handling client: {e}")
    finally:
        handle_disconnection(conn)

def start_server():
    """ Start the server and listen for connections. """
    server.listen(5)
    print(f"[Server] Running on {HOST}:{PORT}...")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

# === Tkinter GUI ===
base = tk.Tk()
base.title("PyChat Host")
base.geometry("600x450")
base.configure(bg="#716664")

client_count_label = tk.Label(base, text="Online: 0", bg="#716664", fg="white", font=("Arial", 12, "bold"))
client_count_label.pack(pady=5)

chat_box = tk.Text(base, state=tk.DISABLED, bg="#689099", font="Helvetica")
scrollbar = tk.Scrollbar(base, command=chat_box.yview)
chat_box.config(yscrollcommand=scrollbar.set)
chat_box.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

threading.Thread(target=start_server, daemon=True).start()
base.mainloop()
