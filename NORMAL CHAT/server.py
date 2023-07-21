import socket
import threading
import os

# Function to broadcast a message to all connected clients, except the sender
def broadcast(message, client_sockets, sender_socket):
    for client_socket in client_sockets.copy():  # Use a copy to avoid concurrent modification errors
        if client_socket != sender_socket:
            try:
                client_socket.send(message.encode())
            except ConnectionResetError:
                # Client disconnected abruptly
                pass

# Function to handle communication with a connected client
def handle_client(client_socket, address, client_names, client_sockets, lock):
    while True:
        try:
            data = client_socket.recv(1024).decode()
        except ConnectionResetError:
            # Client disconnected abruptly
            break

        if not data:
            # Client has disconnected
            with lock:
                if address in client_names:
                    print("{} has been disconnected".format(client_names[address]))
                    del client_names[address]
                if client_socket in client_sockets:
                    client_sockets.remove(client_socket)
                broadcast("{} has been disconnected".format(client_names.get(address, address)), client_sockets, client_socket)
            break

        if data.startswith("REGISTER:"):
            # Client wants to register its name
            client_name = data.split(":", 1)[1]
            with lock:
                client_names[address] = client_name
                response = "Name registered as: {}".format(client_name)
                client_socket.send(response.encode())
                print("{} registered as: {}".format(address, client_name))
        elif data.lower() == "bye":
            # Client wants to disconnect
            with lock:
                print("{} has been disconnected".format(client_names[address]))
                client_socket.send("GoodBye".encode())
                client_socket.close()
                if address in client_names:
                    del client_names[address]
                if client_socket in client_sockets:
                    client_sockets.remove(client_socket)
                broadcast("{} has been disconnected".format(client_names.get(address, address)), client_sockets, client_socket)
            break
        elif data.startswith("file:"):
            # Client is sending a file
            _, filename, filesize = data.split(":")
            filename = filename.strip()
            filesize = int(filesize.strip())

            # Save the file in the server_files directory
            server_file_directory = './FILES'
            if not os.path.exists(server_file_directory):
                os.makedirs(server_file_directory)

            file_path = os.path.join(server_file_directory, filename)
            with open(file_path, "wb") as file:
                remaining_bytes = filesize
                while remaining_bytes > 0:
                    file_data = client_socket.recv(min(4096, remaining_bytes))
                    if not file_data:
                        break
                    file.write(file_data)
                    remaining_bytes -= len(file_data)

            print("Received file '{}' from {}".format(filename, client_names[address]))
            broadcast("Received file '{}' from {}".format(filename, client_names[address]), client_sockets, client_socket)
        else:
            # Display received message and respond with acknowledgment
            print("Received from {}: {}".format(client_names[address], data))
            response = "Server: Message received!"
            client_socket.send(response.encode())

# Main function to run the server
def main():
    host = ''
    port = 12345

    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to a specific address and port
    server_socket.bind((host, port))
    server_socket.listen(5)
    print("TCP server started on {}:{}".format(host, port))

    # Dictionary to store client names and addresses
    client_names = {}
    client_sockets = set()

    # Lock for the client_sockets set
    lock = threading.Lock()

    while True:
        client_socket, address = server_socket.accept()
        print("Connection established with {}:{}".format(*address))

        # Start a separate thread to handle each client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, address, client_names, client_sockets, lock), daemon=True)
        client_thread.start()

if __name__ == "__main__":
    main()
