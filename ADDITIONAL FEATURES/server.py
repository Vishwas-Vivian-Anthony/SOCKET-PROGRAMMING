import threading
import socket
import os

# Server configuration
host = '127.0.0.1'
port = 59001

# Create the server socket and bind it to the specified address
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# Lists to keep track of connected clients and their aliases
clients = []
aliases = []

# Function to broadcast a message to all connected clients, excluding the sender
def broadcast(message, sender=None):
    for client in clients:
        if client != sender:
            client.send(message)

# Function to set up a new client connection
def setup_client(client):
    client.send("Enter your alias: ".encode('utf-8'))
    alias = client.recv(1024).decode('utf-8')

    if alias in aliases:
        # If the alias is already in use, block the client and close the connection
        client.send('You were blocked by the server. The alias is already in use.'.encode('utf-8'))
        client.close()
        return None

    # Add the new alias to the list of connected clients
    aliases.append(alias)

    # Send a welcome message to the client
    client.send('You are now connected!'.encode('utf-8'))
    return alias

# Function to handle the communication with a connected client
def handle_client(client):
    alias = setup_client(client)

    if not alias:
        return

    while True:
        try:
            message = client.recv(1024)
            if not message:
                # Client disconnected
                index = clients.index(client)
                alias = aliases[index]
                clients.remove(client)
                aliases.remove(alias)
                broadcast(f'{alias} has left the chat room!'.encode('utf-8'))
                client.close()
                break
            if message.startswith(b'/file'):
                # The client sent a file
                _, filename, filesize = message.split(b'|')
                filename = filename.decode('utf-8')
                filesize = int(filesize)
                # Save the file in the server_files directory
                server_file_directory = './FILES'
                if not os.path.exists(server_file_directory):
                    os.makedirs(server_file_directory)
                file_path = os.path.join(server_file_directory, filename)
                with open(file_path, 'wb') as file:
                    remaining_bytes = filesize
                    while remaining_bytes > 0:
                        data = client.recv(min(4096, remaining_bytes))
                        file.write(data)
                        remaining_bytes -= len(data)
                print(f'{alias} has shared a file: {filename}')
                broadcast(f'{alias} has shared a file: {filename}'.encode('utf-8'), client)
            else:
                # Regular chat message, broadcast it to all clients
                broadcast(message, client)
        except Exception as e:
            print(f'Error: {e}')
            client.close()
            break

# Function to accept incoming client connections
def receive():
    while True:
        print('Server is running and listening ...')
        client, address = server.accept()
        print(f'Connection is established with {str(address)}')
        # Start a new thread to handle the client's communication
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

if __name__ == "__main__":
    receive()
