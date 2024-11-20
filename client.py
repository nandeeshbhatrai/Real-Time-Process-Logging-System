import win32gui
import time
import socket
import threading
from datetime import datetime
import argparse
import re

# Function to get the current active window title
def get_active_window():
    # Get the handle of the current active window
    window = win32gui.GetForegroundWindow()
    # Get the window title of the active window
    window_title = win32gui.GetWindowText(window)
    
    # Check for Microsoft Edge's special behavior (Edge may return empty window title)
    if "Microsoft Edge" in window_title:
        return "Microsoft Edge"  # Use a fixed name for Edge window, avoiding infinite loop
    
    window_title = re.sub(r'[^\x20-\x7E]', '', window_title)

    return window_title

# Function to log active window titles and send them to the server
def log_active_window(client_socket, interval):
    last_window = None
    while True:
        try:
            current_window = get_active_window()
            if current_window != last_window and current_window:  # Send only if the window changes
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                message = f"{timestamp}, {current_window}"
                client_socket.send(message.encode('utf-8'))
                print(f"Sent active window: {message}")
                last_window = current_window
            time.sleep(interval)  # Check at the specified interval
        except (socket.error, BrokenPipeError) as e:
            print("Connection lost. Attempting to reconnect...")
            reconnect(client_socket)
        except Exception as e:
            print(f"Unexpected error: {e}")
            break

# Function to attempt reconnection
MAX_RECONNECTION = 5 # terminate if can't connect after attempting this many times
def reconnect(client_socket):
    global MAX_RECONNECTION
    while True:
        try:
            MAX_RECONNECTION -= 1
            if(MAX_RECONNECTION <= 0):
                print("\n\nCan't connect at this time.\n\n")
                exit()
            client_socket.close()
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((SERVER_IP, SERVER_PORT))
            print("Reconnected to server.")
            return
        except socket.error:
            MAX_RECONNECTION -= 1
            if(MAX_RECONNECTION <= 0):
                print("Exiting ...")
                exit()
            print("Reconnection failed. Retrying in 5 seconds...")
            time.sleep(5)

# Function to start the client
def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((SERVER_IP, SERVER_PORT))
        print("Connected to server.")
        log_active_window(client_socket, INTERVAL)
    except Exception as e:
        print(f"Failed to connect to the server: {e}")
    finally:
        client_socket.close()

# Main function
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Client for active window logging.")
    parser.add_argument('--ip', type=str, required=True, help="Server IP address")
    parser.add_argument('--port', type=int, default=9999, help="Server port number")
    parser.add_argument('--interval', type=int, default=1, help="Interval for checking window changes in seconds")
    args = parser.parse_args()

    SERVER_IP = args.ip
    SERVER_PORT = args.port
    INTERVAL = args.interval

    try:
        client_thread = threading.Thread(target=start_client, daemon=True)
        client_thread.start()
        client_thread.join()
    except KeyboardInterrupt:
        print("\nClient shutting down ...")
