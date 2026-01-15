"""
Message protocol definitions for P2P chat.
Implements a simple JSON-based protocol for peer communication.
"""

import json
import time
from typing import Dict, Any
from enum import Enum


class MessageType(Enum):
    """Message types for P2P communication"""
    HELLO = "hello"
    MESSAGE = "message"
    ACK = "ack"
    DISCONNECT = "disconnect"
    PING = "ping"
    PONG = "pong"


class Message:
    """Message class for protocol handling"""
    
    def __init__(self, msg_type: MessageType, from_peer: str, body: str = "", timestamp: float = None):
        self.type = msg_type
        self.from_peer = from_peer
        self.body = body
        self.timestamp = timestamp if timestamp else time.time()
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps({
            "type": self.type.value,
            "from": self.from_peer,
            "timestamp": self.timestamp,
            "body": self.body
        })
    
    @staticmethod
    def from_json(json_str: str) -> 'Message':
        """Parse message from JSON string"""
        data = json.loads(json_str)
        msg_type = MessageType(data["type"])
        return Message(
            msg_type=msg_type,
            from_peer=data["from"],
            body=data.get("body", ""),
            timestamp=data.get("timestamp", time.time())
        )
    
    def to_bytes(self) -> bytes:
        """Convert message to bytes for transmission"""
        return self.to_json().encode('utf-8')
    
    @staticmethod
    def from_bytes(data: bytes) -> 'Message':
        """Parse message from bytes"""
        return Message.from_json(data.decode('utf-8'))


def create_hello_message(peer_id: str) -> Message:
    """Create a HELLO message"""
    return Message(MessageType.HELLO, peer_id, "Hello!")


def create_text_message(peer_id: str, text: str) -> Message:
    """Create a text MESSAGE"""
    return Message(MessageType.MESSAGE, peer_id, text)


def create_ping_message(peer_id: str) -> Message:
    """Create a PING message for keep-alive"""
    return Message(MessageType.PING, peer_id)


def create_pong_message(peer_id: str) -> Message:
    """Create a PONG message in response to PING"""
    return Message(MessageType.PONG, peer_id)


def create_disconnect_message(peer_id: str) -> Message:
    """Create a DISCONNECT message"""
    return Message(MessageType.DISCONNECT, peer_id, "Goodbye!")
