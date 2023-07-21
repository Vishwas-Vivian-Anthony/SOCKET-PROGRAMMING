import socket
import threading
import os

def receive_messages(client_socket):
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            print(data)
            if data.lower() == "goodbye":
                client_socket.close()
                break
        except ConnectionResetError:
            # Server disconnected abruptly
            break

def send_file(client_socket, file_path):
    with open(file_path, "rb") as file:
        filename = file_path.split("/")[-1]
        client_socket.send(("file:" + filename).encode())
        while True:
            file_data = file.read(1024)
            if not file_data:
                break
            client_socket.send(file_data)
        print("File '{}' has been sent successfully.".format(filename))

def main():
    host = '127.0.0.1'
    port = 12345

    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    client_socket.connect((host, port))

    # Get the client's name
    client_name = input("Enter your name: ")
    client_socket.send(("REGISTER:" + client_name).encode())

    # Start a separate thread to handle receiving messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
    receive_thread.start()

    while True:
        message = input("Enter message to send ('Bye' to quit): ")
        if message.lower() == "bye":
            client_socket.send(message.encode())
            # Wait for the GoodBye message from the server before disconnecting
            receive_thread.join()
            break
        elif message.lower().startswith("/file"):
            # Extract the file path from the message
            file_path = message[len("/file"):].strip()
            try:
                send_file(client_socket, file_path)
            except FileNotFoundError:
                print("File not found. Please try again.")
        else:
            client_socket.send(message.encode())

if __name__ == "__main__":
    main()
