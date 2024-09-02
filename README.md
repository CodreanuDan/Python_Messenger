# 📨 Python Messenger App

A real-time chat application built with Python.

## Project Overview

The Python Messenger App consists of the following components:

- **Client Application** with a GUI using Tkinter
- **Concurrent Server** to handle multiple clients
- **User Database** for authentication
- **Message Database** for storing messages

### Client Application

The client-side application is designed with a user-friendly graphical interface using Tkinter. It consists of four frames that form the application's menu:

1. **Main Menu (Page 1)**
   - Buttons for `LOGIN`, `REGISTER`, and `EXIT`.
   - The application connects to the "USERS" database to verify user credentials.

2. **Login Menu (Page 2)**
   - Contains fields for entering login credentials.
   - Utilizes a `login` function to check if the username and password exist in the "USERS" database.
   - Creates a `Client` object that handles communication with the server upon successful authentication.
   - The `Forgot Password?` button redirects to Page 4, where the user can reset their password. This is done through the `change_password` function, which is triggered by a button.

3. **Registration Menu (Page 3)**
   - Fields for new users to enter their details.
   - Checks if the user ID and username already exist in the database; if not, creates a new account.
   - The `terms & conditions` checkbox must be checked to register.
   - Supports the option to hide/show passwords. All input fields are cleared after function calls, and appropriate confirmation or warning messages are displayed.

4. **Password Reset Menu (Page 4)**
   - Allows users to reset their password by entering their username and a new password. The database is updated with the new password via the `change_password` function.

#### Client Communication

- The client is represented by the `Client` class, which handles communication with the server.
- Upon connection, the server sends a generic "NAME" message, and the client responds with the username.
- Once connected, users can send messages in real-time using the `send_message` function, which encodes the message from the `Msg_Box` and sends it to the server. Incoming messages are decoded and displayed in the `Chat_Box` using the `receive_message` function.
- The application also supports sending emojis, which are stored in a list.
- The GUI only becomes active once it is fully initialized to prevent errors.
- The application operates on three threads to handle each critical operation (GUI, Send/Receive Messages).
- Pressing the "Log Out" button disconnects the client from the server and closes the application.

### 🖥️ Concurrent Server

The server component manages client connections and message distribution. It maintains lists of client addresses and names and can save messages to a database.

- The server uses the `handle_client` function to accept connections and spawns a thread with the `manage_client` function as its target.
- The `manage_client` function handles incoming messages, distributes them to all connected participants through the `broadcast_message` function, and saves messages to the database.
- It also manages the removal of clients who encounter connection issues.

### 📊 Application Structure

The application is organized into specific classes:

- **Server Program**: Structured in a class containing functions for initialization and broadcasting.
- **Client Application**: More complex, with separate classes for each frame:
  - Each frame class handles the initialization of widgets and specific functions (such as `register`, `login`, `change_password`, etc.).
  - Commands from the `GUI_Commands` class are used to provide functionality to the buttons.
- **GUI Initialization**: The `GUI_Init` class initializes the application's graphical interface.

### 🌟 Latest Update

The program structure has been improved for better organization:

- The server program is now in a dedicated class, with specific functions for initialization and message broadcasting.
- The client application includes a class for each frame (Main Menu, Login, Register, Password Reset), which includes widget initialization and specific functions for each feature.
- Commands for button functionality have been modularized in a separate `GUI_Commands` class.

## 💻 How to Run

1. **Server**: Start the server by running the server script.
2. **Client**: Run the client script to open the GUI and connect to the server.

## 📚 Technologies Used

- Python
- Tkinter (for GUI)
- SQLite (for databases)
- Socket Programming (for real-time communication)

