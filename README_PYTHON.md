# P2P Chat - Python MVP

A Minimal Viable Product (MVP) for a Python-based peer-to-peer (P2P) chat application that allows two peers to exchange text messages across different networks (NAT/Internet).

## Overview

This MVP enables direct peer-to-peer communication using UDP hole punching for NAT traversal and a central signaling server for peer discovery. The implementation focuses on functionality over completeness, providing console-based text messaging without advanced features like encryption, persistence, or GUIs.

## Architecture

```
Peer A  <------UDP------> Peer B
   \                         /
    \------ Signaling ------/
            Server
```

### Components

1. **Signaling Server** (`server/signaling_server.py`)
   - FastAPI-based REST server
   - In-memory peer registry
   - Peer registration and discovery
   - Tracks online status

2. **Peer Client** (`client/`)
   - `peer.py` - Main peer client with identity management
   - `networking.py` - UDP socket handling and NAT traversal
   - `protocol.py` - JSON-based message protocol

## Features

✅ **Peer Identity**
- Unique UUID-based peer_id
- Optional username
- In-memory only (no persistence)

✅ **Signaling & Discovery**
- Central server for peer registration
- Query peers by ID
- List online peers

✅ **NAT Traversal**
- UDP hole punching
- Optional STUN support (via pystun3)
- Maintains NAT mappings

✅ **Transport Layer**
- UDP-based communication
- Direct peer-to-peer after discovery
- Low latency, accepts packet loss

✅ **Message Protocol**
- JSON-based protocol
- Message types: hello, message, ping, pong, disconnect
- Timestamps included

✅ **Connection Establishment**
- Automatic peer discovery
- UDP hole punching
- One-to-one sessions

✅ **Messaging**
- Send/receive text messages
- Console-based interface
- Real-time message display

✅ **Keep-Alive**
- Heartbeat mechanism
- Prevents NAT mapping expiration
- 15-second intervals

✅ **Error Handling**
- Connection timeouts
- Peer offline detection
- Server unreachable handling
- Retry logic (up to 3 attempts)

## Requirements

- Python 3.10 or higher
- Network connectivity
- Open UDP port (automatically assigned)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/samarthnaikk/x20chat.git
cd x20chat
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Step 1: Start the Signaling Server

In one terminal:

```bash
cd server
python signaling_server.py
```

The server will start on `http://0.0.0.0:8000`

### Step 2: Start Peer A

In a second terminal:

```bash
cd client
python peer.py --username Alice --server http://localhost:8000
```

The peer will:
1. Register with the signaling server
2. Display its peer ID
3. Show available peers or wait for connections

### Step 3: Start Peer B

In a third terminal (or on another machine):

```bash
cd client
python peer.py --username Bob --server http://localhost:8000
```

If connecting to a remote signaling server, use its public IP:

```bash
python peer.py --username Bob --server http://SERVER_IP:8000
```

### Step 4: Connect Peers

When Peer B starts, it will show available peers. Select Peer A by entering its peer ID.

Alternatively, you can directly connect by specifying the peer ID:

```bash
python peer.py --username Bob --server http://localhost:8000 --connect PEER_A_ID
```

### Step 5: Chat!

Once connected, type messages and press Enter to send. Messages appear in real-time on both peers.

Commands:
- Type `/quit` to exit
- `Ctrl+C` to shutdown

## Example Session

**Terminal 1 - Signaling Server:**
```
$ python server/signaling_server.py
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 - Peer Alice:**
```
$ python client/peer.py --username Alice
2026-01-15 12:00:00 - INFO - Peer initialized: Alice (ID: a1b2c3d4...)
2026-01-15 12:00:00 - INFO - Successfully registered with signaling server

=== P2P Chat Client ===
Username: Alice
Peer ID: a1b2c3d4-5678-90ab-cdef-1234567890ab
Listening on port: 54321

No peers available. Waiting for connection...

--- Chat started. Type messages and press Enter. Type '/quit' to exit ---
> 2026-01-15 12:00:15 - INFO - Received HELLO from peer
2026-01-15 12:00:15 - INFO - Connected to peer at ('192.168.1.100', 54322)
> Hello Bob!
> [b9c8d7e6...]: Hi Alice! How are you?
> I'm good, thanks!
```

**Terminal 3 - Peer Bob:**
```
$ python client/peer.py --username Bob
2026-01-15 12:00:10 - INFO - Peer initialized: Bob (ID: b9c8d7e6...)
2026-01-15 12:00:10 - INFO - Successfully registered with signaling server

=== P2P Chat Client ===
Username: Bob
Peer ID: b9c8d7e6-f5e4-d3c2-b1a0-9876543210ab
Listening on port: 54322

Available peers:
  1. Alice (ID: a1b2c3d4-5678-90...)

Enter peer ID to connect (or 'q' to quit): a1b2c3d4-5678-90ab-cdef-1234567890ab
2026-01-15 12:00:15 - INFO - Peer discovered at 192.168.1.50:54321
2026-01-15 12:00:15 - INFO - Connected to peer at ('192.168.1.50', 54321)

--- Chat started. Type messages and press Enter. Type '/quit' to exit ---
> [a1b2c3d4...]: Hello Bob!
> Hi Alice! How are you?
> [a1b2c3d4...]: I'm good, thanks!
```

## Testing Across Networks

To test across different networks (e.g., from home to work):

1. Deploy the signaling server on a public server (VPS, cloud instance, etc.)
2. Ensure port 8000 is open for the signaling server
3. Start peers on different networks, pointing to the public server:
   ```bash
   python client/peer.py --username Alice --server http://PUBLIC_IP:8000
   ```
4. UDP hole punching will establish direct P2P connection

## Protocol Details

### Message Format

Messages use JSON format:

```json
{
  "type": "message",
  "from": "peer_id",
  "timestamp": 1234567890.123,
  "body": "Hello!"
}
```

### Message Types

- `hello` - Initial handshake
- `message` - Text message
- `ping` - Keep-alive ping
- `pong` - Keep-alive response
- `disconnect` - Graceful disconnect

### API Endpoints

**Signaling Server REST API:**

- `GET /` - Server status
- `POST /register` - Register peer
- `GET /peer/{peer_id}` - Get peer info
- `GET /peers` - List all online peers
- `DELETE /peer/{peer_id}` - Unregister peer
- `GET /status` - Detailed server status

## Limitations (By Design)

This is an MVP with intentional limitations:

❌ No end-to-end encryption
❌ No message persistence/history
❌ No file transfer
❌ No group chats
❌ No offline messaging
❌ No GUI
❌ No message ordering guarantees
❌ No full reliability (UDP packet loss accepted)

## Tech Stack

**Server:**
- FastAPI - Web framework
- Uvicorn - ASGI server
- Pydantic - Data validation

**Client:**
- socket - UDP networking
- threading - Concurrent message handling
- requests - HTTP client for signaling
- uuid - Peer identification
- pystun3 - Optional STUN support

## File Structure

```
x20chat/
├── server/
│   └── signaling_server.py    # Signaling/discovery server
├── client/
│   ├── peer.py                # Main peer client
│   ├── networking.py          # UDP and NAT traversal
│   └── protocol.py            # Message protocol
├── requirements.txt           # Python dependencies
└── README_PYTHON.md          # This file
```

## Troubleshooting

**Peer registration fails:**
- Ensure signaling server is running
- Check server URL is correct
- Verify network connectivity

**Cannot discover peer:**
- Ensure peer has registered with server
- Check peer ID is correct
- Verify server is reachable

**UDP hole punching fails:**
- Some NAT types (symmetric NAT) may block hole punching
- Try using a public server for signaling
- Check firewall settings

**Messages not received:**
- Verify peers are connected (check logs)
- UDP may lose packets - this is expected
- Heartbeat should maintain connection

## Development

The codebase follows Python best practices:

- Type hints for better code clarity
- Logging for debugging
- Modular design (protocol, networking, peer logic separated)
- Error handling with retries
- Clean shutdown handling

## Future Enhancements (Out of Scope for MVP)

- End-to-end encryption (E2EE)
- Message persistence and history
- Group chat support
- File transfer
- GUI (desktop/web)
- TURN server fallback for strict NATs
- Message ordering and reliability
- Presence indicators
- Typing indicators

## License

MIT License - See LICENSE file for details

## Contributing

This is an MVP implementation. Contributions for core functionality improvements are welcome!

## Contact

For issues or questions, please open an issue on the GitHub repository.
