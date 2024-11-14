import socket
import os
from tkinter import Tk, Label, Button, Entry, StringVar, Radiobutton, filedialog, messagebox

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
                    s.connect((ip, 12345))
                    s.sendall(file_name.encode())
                    with open(file_path, 'rb') as f:
                        data = f.read(1024)
                        while data:
                            s.sendall(data)
                            data = f.read(1024)
            else:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.sendto(file_name.encode(), (ip, 12345))
                    with open(file_path, 'rb') as f:
                        data = f.read(1024)
                        while data:
                            s.sendto(data, (ip, 12345))
                            data = f.read(1024)

            messagebox.showinfo("Success", "File transferred successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"File transfer failed: {e}")

if __name__ == "__main__":
    root = Tk()
    client = FileTransferClient(root)
    root.mainloop()
