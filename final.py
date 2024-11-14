import socket
import os
import threading
from tkinter import Tk, Label, Button, Entry, StringVar, Radiobutton, filedialog, messagebox

# Define the host and port
host = '192.168.98.28'  # Replace this with your server IP
port = 12345

# Create a directory to store received files (on the server side)
received_folder = 'received_files'
if not os.path.exists(received_folder):
    os.makedirs(received_folder)

class FileTransferClient:
    def __init__(self, master):
        self.master = master
        master.title("File Transfer Client")

        self.server_ip = StringVar()
        self.protocol = StringVar(value='TCP')

        Label(master, text="Server IP:").pack()
        Entry(master, textvariable=self.server_ip).pack()

        Label(master, text="Select Protocol:").pack()
        Radiobutton(master, text='TCP', variable=self.protocol, value='TCP').pack()
        Radiobutton(master, text='UDP', variable=self.protocol, value='UDP').pack()

        Button(master, text='Send File', command=self.send_file).pack()

    def send_file(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return

        file_name = os.path.basename(file_path)
        ip = self.server_ip.get()
        protocol = self.protocol.get()
        try:
            if protocol == 'TCP':
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((ip, port))
                    s.sendall(file_name.encode())
                    with open(file_path, 'rb') as f:
                        data = f.read(1024)
                        while data:
                            s.sendall(data)
                            data = f.read(1024)
            else:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.sendto(file_name.encode(), (ip, port))
                    with open(file_path, 'rb') as f:
                        data = f.read(1024)
                        while data:
                            s.sendto(data, (ip, port))
                            data = f.read(1024)

            messagebox.showinfo("Success", "File transferred successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"File transfer failed: {e}")

def tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f'TCP Server listening on {host}:{port}')

    while True:
        conn, addr = server_socket.accept()
        print(f'Connection from {addr}')

        # Receive the file name
        file_name = conn.recv(1024).decode().splitlines()[0]  # Split and use only the first line
        print(f'Receiving file: {file_name}')
        
        # Validate file name to avoid invalid arguments in file path
        if not file_name or '..' in file_name or '/' in file_name:
            print("Invalid file name received.")
            conn.close()
            continue
        
        file_path = os.path.join(received_folder, file_name.strip())  # Clean up file name

        # Receive the file data
        with open(file_path, 'wb') as f:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                f.write(data)

        print(f'File {file_name} received and saved as {file_path}')
        conn.close()

def udp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    print(f'UDP Server listening on {host}:{port}')

    while True:
        file_name, addr = server_socket.recvfrom(1024)
        file_name = file_name.decode().splitlines()[0]  # Extract just the file name
        print(f'Receiving file: {file_name} from {addr}')
        
        # Ensure the directory exists
        if not os.path.exists(received_folder):
            os.makedirs(received_folder)
        
        # Validate file name to avoid invalid arguments in file path
        if not file_name or '..' in file_name or '/' in file_name:
            print("Invalid file name received.")
            continue
        
        file_path = os.path.join(received_folder, file_name.strip())  # Clean up file name

        with open(file_path, 'wb') as f:
            while True:
                data, addr = server_socket.recvfrom(1024)
                if not data:
                    break
                f.write(data)

        print(f'File {file_name} received and saved as {file_path}')

def start_servers():
    tcp_thread = threading.Thread(target=tcp_server)
    udp_thread = threading.Thread(target=udp_server)

    tcp_thread.start()
    udp_thread.start()

    tcp_thread.join()
    udp_thread.join()

# Main function to either start the client or server
if __name__ == "__main__":
    mode = input("Do you want to start the client or server? (client/server): ").strip().lower()

    if mode == 'client':
        root = Tk()
        client = FileTransferClient(root)
        root.mainloop()
    elif mode == 'server':
        start_servers()
    else:
        print("Invalid mode. Please choose 'client' or 'server'.")

