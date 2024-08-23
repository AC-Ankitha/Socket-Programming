import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog, messagebox

# Client class using tkinter for GUI
class Client:
    def __init__(self, host='localhost', port=12345):
        self.nickname = None
        
        # Start tkinter GUI
        self.gui_done = False
        self.running = True

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        self.gui_thread = threading.Thread(target=self.gui_loop)
        self.receive_thread = threading.Thread(target=self.receive)

        self.gui_thread.start()
        self.receive_thread.start()

    def gui_loop(self):
        self.root = tkinter.Tk()
        self.root.configure(bg="lightgray")

        self.chat_label = tkinter.Label(self.root, text="Chat:", bg="lightgray")
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.root)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disabled')

        self.msg_label = tkinter.Label(self.root, text="Message:", bg="lightgray")
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.root, height=3)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.root, text="Send", command=self.write)
        self.send_button.pack(padx=20, pady=5)

        self.guide_button = tkinter.Button(self.root, text="Guide", command=self.show_guide)
        self.guide_button.pack(padx=20, pady=5)

        self.gui_done = True
        self.root.protocol("WM_DELETE_WINDOW", self.stop)
        self.root.mainloop()

    def show_guide(self):
        guide_text = (
            "Welcome to the Group Chat!\n\n"
            "1. Type your message in the box and click 'Send' to send it.\n"
            "2. You can see all the messages in the chat log above.\n"
            "3. The 'Guide' button will bring you back to this help screen.\n"
            "4. Enjoy chatting!"
        )
        messagebox.showinfo("Guide", guide_text)

    def write(self):
        if self.nickname:  # Ensure nickname is set
            message = f"{self.nickname}: {self.input_area.get('1.0', 'end').strip()}"
            try:
                self.sock.send(message.encode('utf-8'))
            except OSError as e:
                print(f"Socket error: {e}")
        else:
            print("Nickname is not set.")
        self.input_area.delete('1.0', 'end')

    def stop(self):
        self.running = False
        self.root.destroy()
        try:
            self.sock.close()
        except OSError:
            pass
        exit(0)

    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                if message == 'NICKNAME':
                    if self.nickname:
                        self.sock.send(self.nickname.encode('utf-8'))
                else:
                    if self.gui_done:
                        self.text_area.config(state='normal')
                        self.text_area.insert('end', message + '\n')
                        self.text_area.yview('end')
                        self.text_area.config(state='disabled')
            except ConnectionAbortedError:
                break
            except OSError as e:
                print(f"Socket error during receive: {e}")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                break

if __name__ == "__main__":
    nickname_prompt = tkinter.Tk()
    nickname_prompt.withdraw()
    nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=nickname_prompt)

    if nickname:
        client = Client()
        client.nickname = nickname
    else:
        print("Nickname is required to start the client.")
