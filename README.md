Virtual Cosmos
Virtual Cosmos is a lightweight, Python-powered multiplayer "metaverse" designed for remote teams or social hangouts. It features a collision-aware map, distinct room zones, and a spatial chat system where you can only communicate with those near you.
🔠 Core Languages
The project is built entirely using a single-language ecosystem to ensure seamless communication between the client and server:
Python: The primary language used for both the Frontend (graphics, input handling, and game logic via Pygame) and the Backend (asynchronous WebSocket handling and API management via FastAPI).
JSON (JavaScript Object Notation): Used as the data interchange format. All player coordinates, names, and chat messages are serialized into JSON strings to be sent across the network.
✨ Features
Real-time Multiplayer: See other players move in real-time with low-latency WebSocket synchronization.
Spatial Chat: A proximity-based communication system. The chat interface activates only when you walk up to another user.
Collision System: Navigable environment with walls and furniture that players cannot pass through.
Room Detection: The system tracks your coordinates to identify if you are in the Meeting Room, Lounge, Breakout Room, or Office Space.
Dynamic UI: Includes a sidebar for chat history and a bottom navigation bar for simulated interactions.
🛠️ Tech Stack
Frontend: pygame (2D Engine)
Backend: FastAPI (Asynchronous Web Framework)
Networking: WebSockets for bi-directional communication.
Concurrency: threading and asyncio to manage network and rendering loops simultaneously.
🚀 Getting Started
1. Prerequisites
Ensure you have Python 3.8+ installed on your machine.
2. Install Dependencies
Install the required libraries using the provided requirements file:
code
Bash
pip install -r requirements.txt
3. Run the Server
The server must be running first to handle the WebSocket connections and broadcast player positions.
code
Bash
python server.py
The server will start at http://localhost:8000.
4. Run the Client
Open a new terminal window and run the client. You can run this command multiple times to simulate multiple players on the same machine.
code
Bash
python client.py
🎮 How to Play / Instructions
Movement: Use the Arrow Keys (Up, Down, Left, Right) to move your avatar around the office.
Navigation: You cannot walk through walls (brown) or out of the game boundaries. Explore the four different quadrants of the map.
Chatting:
Walk towards another player (red avatars).
Once you are close enough, the sidebar will change from "Walk near a user to chat" to a chat input box.
Type your message and press Enter to send.
Identification: Your avatar is Blue, while all other connected players appear as Red.
📂 Project Structure
client.py: The Pygame application. Handles rendering, local movement logic, and the user interface.
server.py: The FastAPI application. Manages a list of active connections and broadcasts movement and chat data to all clients.
requirements.txt: List of necessary Python packages.
