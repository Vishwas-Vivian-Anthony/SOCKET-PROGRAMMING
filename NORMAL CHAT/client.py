import socket
import threading
import os

# Function to continuously receive messages from the server
def receive_messages(client_socket):
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            print(data)
            if data.lower() == "goodbye":
                # Close the client socket if the server sends a Goodbye message
                client_socket.close()
                break
        except ConnectionResetError:
            # Server disconnected abruptly
            break

# Function to send a file to the server
def send_file(client_socket, file_path):
    with open(file_path, "rb") as file:
        filename = file_path.split("/")[-1]
        # Send a message to the server indicating the file transfer
        client_socket.send(("file:" + filename).encode())
        while True:
            file_data = file.read(1024)
            if not file_data:
                break
            client_socket.send(file_data)
        print("File '{}' has been sent successfully.".format(filename))

# Main function to initiate the client
def main():
    host = '127.0.0.1'
    port = 12345

    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    client_socket.connect((host, port))

    # Get the client's name and register with the server
    client_name = input("Enter your name: ")
    client_socket.send(("REGISTER:" + client_name).encode())

    # Start a separate thread to handle receiving messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
    receive_thread.start()

    while True:
        message = input("Enter message to send ('Bye' to quit): ")
        if message.lower() == "bye":
            # Send the "Bye" message to the server
            client_socket.send(message.encode())
            # Wait for the Goodbye message from the server before disconnecting
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
            # Send regular chat messages to the server
            client_socket.send(message.encode())

if __name__ == "__main__":
    main()
