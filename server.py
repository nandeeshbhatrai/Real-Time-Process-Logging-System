import socket
import os
import threading

clients = 0
lock = threading.Lock()


def handle_client(client_socket, client_address, master_log_folder):
    global clients

    client_ip = client_address[0]
    print(f"Connection from {client_ip} has been established.")

    client_log_folder = os.path.join(master_log_folder, client_ip)
    os.makedirs(client_log_folder, exist_ok=True)

    log_file_path = os.path.join(client_log_folder, 'log.txt')

    try:
        with open(log_file_path, 'a') as log_file:
            while True:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:  # If no data, the client has disconnected
                    break

                # Log the data to the file
                log_file.write(data + '\n')
                log_file.flush()  # Ensure immediate write to disk
                # print(f"Received from {client_ip}: {data}")

    except Exception as e:
        print(f"Error with client {client_ip}: {e}")
    finally:
        with lock:
            clients -= 1
        client_socket.close()
        print(f"Connection from {client_ip} closed. Active clients: {clients}")

# Function to start the server
def start_server():
    global clients

    host = '0.0.0.0'  # Listen on all available network interfaces
    port = 9999       # Use any open port you like

    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(500) #default number of clients
    print(f"Server listening on port {port}")

    # Define the master folder for logs
    master_log_folder = 'LOGS'
    os.makedirs(master_log_folder, exist_ok=True)

    try:
        while True:
            # Accept a new client connection
            client_socket, client_address = server_socket.accept()
            with lock:
                clients += 1
            print(f"New connection from {client_address[0]}. Total active clients: {clients}")

            # Handle the client in a separate thread
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address, master_log_folder), daemon=True)
            client_thread.start()

    except KeyboardInterrupt:
        print("\nServer shutting down ...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
