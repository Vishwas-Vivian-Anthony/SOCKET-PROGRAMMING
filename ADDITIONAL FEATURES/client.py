import socket
import threading
import os
import time

alias = input('Enter the unique identification: ')
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 59001))

# New function to save received files to a specific location
def receive_file(file_name):
    try:
        # Define the path where the client will save the received files
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

# Function to receive messages on the client end
def client_receive():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if not message:
                print('Connection to the server is closed.')
                break
            if message.startswith(f'{alias} has shared a file:'):
                _, filename = message.split(': ')
                filename = filename.strip()
                print(f'Receiving file: {filename}')
                receive_file(filename)
            else:
                print(message)
        except ConnectionResetError:
            print('Connection to the server was reset.')
            break
        except Exception as e:
            print(f'Error: {e}')
            client.close()
            break

# Function to send messages from the client to another client
def client_send():
    while True:
        message = input("")
        if not client:
            break  # The loop will exit if the client socket is closed

        if message.lower() == "bye":
            client.send(message.encode())
            # Close the client socket and break the loop to stop the threads
            client.close()
            print("Goodbye")
            break
        elif message.startswith("/file"):
            _, file_path = message.split(" ")
            file_path = file_path.strip()
            send_file(file_path)
        else:
            if client:
                message = f'{alias}: {message}'
                client.send(message.encode('utf-8'))

# Function to send Files
def send_file(file_path):
    try:
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        if file_size > 10 * 1024 * 1024:  # 10 MB in bytes
            print("Error: File size exceeds the limit of 10MB. The file will not be sent.")
            return

        client.send(f'/file|{file_name}|{file_size}'.encode('utf-8'))

        with open(file_path, 'rb') as file:
            while True:
                data = file.read(4096)
                if not data:
                    break
                client.send(data)
        # Increase the delay to 1 second (you can adjust this value if needed)
        time.sleep(1)
        client.send(b'<END_OF_FILE>')
        print(f'{file_name} sent successfully!')
    except Exception as e:
        print(f'Error while sending file: {e}')
        client.close()  # Close the connection in case of an error

receive_thread = threading.Thread(target=client_receive)
receive_thread.start()

send_thread = threading.Thread(target=client_send)
send_thread.start()
