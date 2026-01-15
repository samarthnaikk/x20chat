"""
UDP networking and NAT traversal functionality.
Handles socket operations and UDP hole punching.
"""

import socket
import threading
import time
from typing import Callable, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class UDPSocket:
    """UDP socket wrapper with NAT traversal support"""
    
    def __init__(self, port: int = 0):
        """
        Initialize UDP socket.
        
        Args:
            port: Local port to bind (0 for random available port)
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('0.0.0.0', port))
        self.local_port = self.socket.getsockname()[1]
        self.running = False
        self.recv_thread = None
        self.on_message_callback = None
        
        logger.info(f"UDP socket bound to port {self.local_port}")
    
    def send_to(self, address: Tuple[str, int], data: bytes) -> bool:
        """
        Send data to specified address.
        
        Args:
            address: Tuple of (ip, port)
            data: Bytes to send
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.socket.sendto(data, address)
            return True
        except Exception as e:
            logger.error(f"Error sending to {address}: {e}")
            return False
    
    def start_receiving(self, callback: Callable[[bytes, Tuple[str, int]], None]):
        """
        Start receiving messages in background thread.
        
        Args:
            callback: Function to call with (data, address) when message received
        """
        self.on_message_callback = callback
        self.running = True
        self.recv_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.recv_thread.start()
        logger.info("Started receiving thread")
    
    def _receive_loop(self):
        """Background thread for receiving messages"""
        self.socket.settimeout(1.0)
        
        while self.running:
            try:
                data, address = self.socket.recvfrom(4096)
                if self.on_message_callback:
                    self.on_message_callback(data, address)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    logger.error(f"Error receiving: {e}")
    
    def stop(self):
        """Stop receiving and close socket"""
        self.running = False
        if self.recv_thread:
            self.recv_thread.join(timeout=2.0)
        self.socket.close()
        logger.info("UDP socket closed")
    
    def get_local_port(self) -> int:
        """Get the local port number"""
        return self.local_port


class NATTraversal:
    """NAT traversal using UDP hole punching"""
    
    @staticmethod
    def perform_hole_punch(udp_socket: UDPSocket, peer_address: Tuple[str, int], attempts: int = 5):
        """
        Perform UDP hole punching to peer.
        
        Args:
            udp_socket: UDP socket to use
            peer_address: Peer's (ip, port) tuple
            attempts: Number of ping attempts
        """
        logger.info(f"Performing hole punch to {peer_address}")
        
        for i in range(attempts):
            udp_socket.send_to(peer_address, b"PUNCH")
            time.sleep(0.2)
        
        logger.info(f"Hole punch complete to {peer_address}")


class Heartbeat:
    """Keep-alive heartbeat to maintain NAT mapping"""
    
    def __init__(self, udp_socket: UDPSocket, peer_address: Tuple[str, int], interval: int = 15):
        """
        Initialize heartbeat.
        
        Args:
            udp_socket: UDP socket to use
            peer_address: Peer's (ip, port) tuple
            interval: Heartbeat interval in seconds
        """
        self.udp_socket = udp_socket
        self.peer_address = peer_address
        self.interval = interval
        self.running = False
        self.thread = None
    
    def start(self):
        """Start sending heartbeat pings"""
        self.running = True
        self.thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.thread.start()
        logger.info(f"Heartbeat started with {self.interval}s interval")
    
    def _heartbeat_loop(self):
        """Background thread for heartbeat"""
        while self.running:
            self.udp_socket.send_to(self.peer_address, b"HEARTBEAT")
            time.sleep(self.interval)
    
    def stop(self):
        """Stop heartbeat"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        logger.info("Heartbeat stopped")


def get_public_ip_port(stun_server: Tuple[str, int] = ("stun.l.google.com", 19302)) -> Optional[Tuple[str, int]]:
    """
    Get public IP and port using STUN.
    
    Args:
        stun_server: STUN server address
        
    Returns:
        Tuple of (public_ip, public_port) or None if failed
    """
    try:
        import stun
        nat_type, external_ip, external_port = stun.get_ip_info(stun_host=stun_server[0], stun_port=stun_server[1])
        
        if external_ip and external_port:
            logger.info(f"Public address: {external_ip}:{external_port} (NAT type: {nat_type})")
            return (external_ip, external_port)
        else:
            logger.warning("Failed to get public address via STUN")
            return None
    except ImportError:
        logger.warning("pystun3 not installed, skipping STUN discovery")
        return None
    except Exception as e:
        logger.error(f"STUN error: {e}")
        return None
