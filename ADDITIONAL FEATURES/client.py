import socket
import threading
import os
import time

# Get a unique identification from the user
alias = input('Enter the unique identification: ')

# Create a socket to connect to the server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 59001))

# Function to receive files and save them to a specific location
def receive_file(file_name):
    try:
        # Define the directory where the client will save the received files
        client_file_directory = './RECEIVED'

        # Create the client_files directory if it doesn't exist
        if not os.path.exists(client_file_directory):
            os.makedirs(client_file_directory)

        file_path = os.path.join(client_file_directory, file_name)
        with open(file_path, 'wb') as file:
            while True:
                data = client.recv(4096)
                if data == b'<END_OF_FILE>':
                    break
                file.write(data)
        print(f'{file_name} received and saved successfully!')
    except Exception as e:
        print(f'Error while receiving file: {e}')

# Function to receive messages from the server
def client_receive():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if not message:
                print('Connection to the server is closed.')
                break
            # Check if the received message is a file sharing notification
            if message.startswith(f'{alias} has shared a file:'):
                _, filename = message.split(': ')
                filename = filename.strip()
                print(f'Receiving file: {filename}')
                receive_file(filename)
            else:
                # Display regular chat messages from the server
                print(message)
        except ConnectionResetError:
            print('Connection to the server was reset.')
            break
        except Exception as e:
            print(f'Error: {e}')
            client.close()
            break

# Function to send messages from the client to the server
def client_send():
    while True:
        message = input("Enter your message: ")
        if not client:
            break  # The loop will exit if the client socket is closed

        if message.lower() == "bye":
            # Send a "bye" message to the server to indicate client's exit
            client.send(message.encode())
            # Close the client socket and break the loop to stop the threads
            client.close()
            print("Goodbye")
            break
        elif message.startswith("/file"):
            # If the message starts with '/file', the client wants to share a file
            _, file_path = message.split(" ")
            file_path = file_path.strip()
            send_file(file_path)
        else:
            # Regular chat message, send it to the server
            if client:
                message = f'{alias}: {message}'
                client.send(message.encode('utf-8'))

# Function to send files to the server
def send_file(file_path):
    try:
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        # Check if the file size exceeds the limit of 10MB
        if file_size > 10 * 1024 * 1024:  # 10 MB in bytes
            print("Error: File size exceeds the limit of 10MB. The file will not be sent.")
            return

        # Send file information (name and size) to the server
        client.send(f'/file|{file_name}|{file_size}'.encode('utf-8'))

        # Read and send the file data in chunks
        with open(file_path, 'rb') as file:
            while True:
                data = file.read(4096)
                if not data:
                    break
                client.send(data)

        # Add a delay of 1 second to ensure the file transmission is complete
        time.sleep(1)
        client.send(b'<END_OF_FILE>')
        print(f'{file_name} sent successfully!')
    except Exception as e:
        print(f'Error while sending file: {e}')
        client.close()  # Close the connection in case of an error

# Start a thread to receive messages from the server
receive_thread = threading.Thread(target=client_receive)
receive_thread.start()

# Start a thread to send messages to the server
send_thread = threading.Thread(target=client_send)
send_thread.start()
