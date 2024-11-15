import socket
import os
import threading

# Define the host and port
host = '192.168.89.6'
port = 12345

# Create a directory to store received files
received_folder = 'received_files'
if not os.path.exists(received_folder):
    os.makedirs(received_folder)

# TCP Server
def tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f'TCP Server listening on {host}:{port}')

    while True:
        conn, addr = server_socket.accept()
        print(f'Connection from {addr}')

        # Receive the file name
        file_name = conn.recv(1024).decode()
        print(f'Receiving file: {file_name}')
        file_path = os.path.join(received_folder, file_name)

        # Receive the file data
        with open(file_path, 'wb') as f:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                f.write(data)

        print(f'File {file_name} received and saved as {file_path}')
        conn.close()

# UDP Server
def udp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    print(f'UDP Server listening on {host}:{port}')

    while True:
        file_name, addr = server_socket.recvfrom(1024)
        file_name = file_name.decode()
        print(f'Receiving file: {file_name} from {addr}')
        file_path = os.path.join(received_folder, file_name)

        with open(file_path, 'wb') as f:
            while True:
                data, addr = server_socket.recvfrom(1024)
                if not data:
                    break
                f.write(data)

        print(f'File {file_name} received and saved as {file_path}')

# Start both TCP and UDP servers simultaneously
if __name__ == "__main__":
    tcp_thread = threading.Thread(target=tcp_server)
    udp_thread = threading.Thread(target=udp_server)

    tcp_thread.start()
    udp_thread.start()

    tcp_thread.join()
    udp_thread.join()
