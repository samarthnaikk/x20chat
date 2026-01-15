"""
Main peer client for P2P chat.
Handles peer identity, signaling, and P2P communication.
"""

import uuid
import threading
import time
import sys
import logging
from typing import Optional, Tuple
import requests

from protocol import Message, MessageType, create_hello_message, create_text_message, create_ping_message, create_pong_message, create_disconnect_message
from networking import UDPSocket, NATTraversal, Heartbeat

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Peer:
    """P2P Chat Peer"""
    
    def __init__(self, username: str = None, signaling_server: str = "http://localhost:8000"):
        """
        Initialize peer.
        
        Args:
            username: Optional username (generated if not provided)
            signaling_server: Signaling server URL
        """
        self.peer_id = str(uuid.uuid4())
        self.username = username if username else f"user_{self.peer_id[:8]}"
        self.signaling_server = signaling_server
        self.udp_socket = UDPSocket()
        self.peer_address = None
        self.peer_id_remote = None
        self.connected = False
        self.heartbeat = None
        self.retry_count = 3
        
        logger.info(f"Peer initialized: {self.username} (ID: {self.peer_id[:8]}...)")
    
    def register_with_server(self) -> bool:
        """
        Register with signaling server.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Registering with signaling server: {self.signaling_server}")
        
        for attempt in range(self.retry_count):
            try:
                response = requests.post(
                    f"{self.signaling_server}/register",
                    json={
                        "peer_id": self.peer_id,
                        "username": self.username,
                        "port": self.udp_socket.get_local_port()
                    },
                    timeout=5
                )
                
                if response.status_code == 200:
                    logger.info("Successfully registered with signaling server")
                    return True
                else:
                    logger.warning(f"Registration failed: {response.status_code}")
            except Exception as e:
                logger.error(f"Registration attempt {attempt + 1} failed: {e}")
                if attempt < self.retry_count - 1:
                    time.sleep(1)
        
        logger.error("Failed to register with signaling server")
        return False
    
    def discover_peer(self, target_peer_id: str) -> Optional[Tuple[str, int]]:
        """
        Discover peer from signaling server.
        
        Args:
            target_peer_id: ID of peer to discover
            
        Returns:
            Tuple of (ip, port) or None if not found
        """
        logger.info(f"Discovering peer: {target_peer_id[:8]}...")
        
        for attempt in range(self.retry_count):
            try:
                response = requests.get(
                    f"{self.signaling_server}/peer/{target_peer_id}",
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    peer_ip = data["ip"]
                    peer_port = data["port"]
                    self.peer_id_remote = target_peer_id
                    logger.info(f"Peer discovered at {peer_ip}:{peer_port}")
                    return (peer_ip, peer_port)
                elif response.status_code == 404:
                    logger.warning(f"Peer not found: {target_peer_id[:8]}...")
                    return None
                else:
                    logger.warning(f"Discovery failed: {response.status_code}")
            except Exception as e:
                logger.error(f"Discovery attempt {attempt + 1} failed: {e}")
                if attempt < self.retry_count - 1:
                    time.sleep(1)
        
        return None
    
    def list_peers(self) -> list:
        """
        Get list of online peers from signaling server.
        
        Returns:
            List of peer dictionaries
        """
        try:
            response = requests.get(f"{self.signaling_server}/peers", timeout=5)
            if response.status_code == 200:
                peers = response.json()["peers"]
                # Filter out self
                peers = [p for p in peers if p["peer_id"] != self.peer_id]
                return peers
            else:
                logger.error(f"Failed to list peers: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error listing peers: {e}")
            return []
    
    def connect_to_peer(self, peer_address: Tuple[str, int]):
        """
        Establish P2P connection with peer.
        
        Args:
            peer_address: Tuple of (ip, port)
        """
        self.peer_address = peer_address
        
        # Perform UDP hole punching
        NATTraversal.perform_hole_punch(self.udp_socket, peer_address)
        
        # Start receiving messages
        self.udp_socket.start_receiving(self._handle_incoming_message)
        
        # Send HELLO message
        hello_msg = create_hello_message(self.peer_id)
        self.send_message(hello_msg)
        
        # Start heartbeat
        self.heartbeat = Heartbeat(self.udp_socket, peer_address)
        self.heartbeat.start()
        
        self.connected = True
        logger.info(f"Connected to peer at {peer_address}")
    
    def _handle_incoming_message(self, data: bytes, address: Tuple[str, int]):
        """
        Handle incoming UDP message.
        
        Args:
            data: Message data
            address: Sender address
        """
        # Handle simple protocol messages
        if data == b"PUNCH":
            # Respond to hole punch
            self.udp_socket.send_to(address, b"PUNCH_ACK")
            return
        elif data == b"PUNCH_ACK":
            return
        elif data == b"HEARTBEAT":
            return
        
        # Handle protocol messages
        try:
            message = Message.from_bytes(data)
            
            if message.type == MessageType.HELLO:
                logger.info(f"Received HELLO from peer")
                # Send PONG response
                pong = create_pong_message(self.peer_id)
                self.send_message(pong)
                
            elif message.type == MessageType.MESSAGE:
                print(f"\n[{message.from_peer[:8]}...]: {message.body}")
                print("> ", end="", flush=True)
                
            elif message.type == MessageType.PING:
                # Respond with PONG
                pong = create_pong_message(self.peer_id)
                self.send_message(pong)
                
            elif message.type == MessageType.PONG:
                pass  # Heartbeat response
                
            elif message.type == MessageType.DISCONNECT:
                logger.info("Peer disconnected")
                self.disconnect()
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    def send_message(self, message: Message) -> bool:
        """
        Send message to connected peer.
        
        Args:
            message: Message to send
            
        Returns:
            True if successful, False otherwise
        """
        if not self.peer_address:
            logger.error("No peer connected")
            return False
        
        return self.udp_socket.send_to(self.peer_address, message.to_bytes())
    
    def send_text(self, text: str) -> bool:
        """
        Send text message to peer.
        
        Args:
            text: Text message to send
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected:
            logger.warning("Not connected to any peer")
            return False
        
        message = create_text_message(self.peer_id, text)
        return self.send_message(message)
    
    def disconnect(self):
        """Disconnect from peer"""
        if self.connected:
            # Send disconnect message
            disconnect_msg = create_disconnect_message(self.peer_id)
            self.send_message(disconnect_msg)
            
            # Stop heartbeat
            if self.heartbeat:
                self.heartbeat.stop()
            
            self.connected = False
            logger.info("Disconnected from peer")
    
    def shutdown(self):
        """Shutdown peer"""
        self.disconnect()
        self.udp_socket.stop()
        logger.info("Peer shutdown complete")


def main():
    """Main entry point for peer client"""
    import argparse
    
    parser = argparse.ArgumentParser(description='P2P Chat Peer Client')
    parser.add_argument('--username', type=str, help='Username for this peer')
    parser.add_argument('--server', type=str, default='http://localhost:8000',
                       help='Signaling server URL (default: http://localhost:8000)')
    parser.add_argument('--connect', type=str, help='Peer ID to connect to')
    
    args = parser.parse_args()
    
    # Create peer
    peer = Peer(username=args.username, signaling_server=args.server)
    
    # Register with server
    if not peer.register_with_server():
        logger.error("Failed to register. Exiting.")
        sys.exit(1)
    
    print(f"\n=== P2P Chat Client ===")
    print(f"Username: {peer.username}")
    print(f"Peer ID: {peer.peer_id}")
    print(f"Listening on port: {peer.udp_socket.get_local_port()}")
    print()
    
    # Connect to peer if specified
    if args.connect:
        peer_address = peer.discover_peer(args.connect)
        if peer_address:
            peer.connect_to_peer(peer_address)
        else:
            logger.error(f"Could not discover peer: {args.connect}")
    else:
        # List available peers
        print("Available peers:")
        peers = peer.list_peers()
        if peers:
            for i, p in enumerate(peers):
                print(f"  {i+1}. {p['username']} (ID: {p['peer_id'][:16]}...)")
            
            print("\nEnter peer ID to connect (or 'q' to quit): ", end="")
            choice = input().strip()
            
            if choice.lower() == 'q':
                peer.shutdown()
                sys.exit(0)
            
            # Try to connect
            peer_address = peer.discover_peer(choice)
            if peer_address:
                peer.connect_to_peer(peer_address)
            else:
                logger.error(f"Could not discover peer: {choice}")
                peer.shutdown()
                sys.exit(1)
        else:
            print("No peers available. Waiting for connection...")
            peer.udp_socket.start_receiving(peer._handle_incoming_message)
    
    # Message loop
    print("\n--- Chat started. Type messages and press Enter. Type '/quit' to exit ---")
    print("> ", end="", flush=True)
    
    try:
        while True:
            text = input()
            
            if text.strip() == '/quit':
                break
            
            if text.strip():
                if peer.connected:
                    peer.send_text(text)
                else:
                    print("Not connected to any peer. Waiting for connection...")
            
            print("> ", end="", flush=True)
    except KeyboardInterrupt:
        print("\nShutting down...")
    except EOFError:
        pass
    
    peer.shutdown()


if __name__ == "__main__":
    main()
