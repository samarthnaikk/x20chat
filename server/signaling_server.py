"""
Signaling server for P2P chat peer discovery.
FastAPI-based REST server with in-memory peer registry.
"""

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Optional
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="P2P Chat Signaling Server")


class PeerRegistration(BaseModel):
    """Peer registration request"""
    peer_id: str
    username: str
    port: int


class PeerInfo:
    """Peer information stored in registry"""
    def __init__(self, peer_id: str, username: str, ip: str, port: int):
        self.peer_id = peer_id
        self.username = username
        self.ip = ip
        self.port = port
        self.last_seen = time.time()
        self.online = True
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "peer_id": self.peer_id,
            "username": self.username,
            "ip": self.ip,
            "port": self.port,
            "online": self.online,
            "last_seen": self.last_seen
        }


# In-memory peer registry
peer_registry: Dict[str, PeerInfo] = {}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "P2P Chat Signaling Server",
        "status": "running",
        "peers_online": len([p for p in peer_registry.values() if p.online])
    }


@app.post("/register")
async def register_peer(registration: PeerRegistration, request: Request):
    """
    Register a peer with the signaling server.
    
    Args:
        registration: Peer registration data
        request: FastAPI request object
        
    Returns:
        Success message
    """
    # Get client IP from request
    client_ip = request.client.host
    
    # Create or update peer info
    peer_info = PeerInfo(
        peer_id=registration.peer_id,
        username=registration.username,
        ip=client_ip,
        port=registration.port
    )
    
    peer_registry[registration.peer_id] = peer_info
    
    logger.info(f"Peer registered: {registration.username} ({registration.peer_id[:8]}...) at {client_ip}:{registration.port}")
    
    return {
        "status": "success",
        "message": "Peer registered successfully",
        "peer_id": registration.peer_id,
        "public_ip": client_ip
    }


@app.get("/peer/{peer_id}")
async def get_peer(peer_id: str):
    """
    Get peer information by ID.
    
    Args:
        peer_id: Peer ID to look up
        
    Returns:
        Peer information
    """
    if peer_id not in peer_registry:
        raise HTTPException(status_code=404, detail="Peer not found")
    
    peer_info = peer_registry[peer_id]
    
    if not peer_info.online:
        raise HTTPException(status_code=404, detail="Peer is offline")
    
    logger.info(f"Peer lookup: {peer_id[:8]}... -> {peer_info.ip}:{peer_info.port}")
    
    return {
        "peer_id": peer_info.peer_id,
        "username": peer_info.username,
        "ip": peer_info.ip,
        "port": peer_info.port
    }


@app.get("/peers")
async def list_peers():
    """
    List all online peers.
    
    Returns:
        List of online peers
    """
    online_peers = [
        peer.to_dict() 
        for peer in peer_registry.values() 
        if peer.online
    ]
    
    return {
        "peers": online_peers,
        "count": len(online_peers)
    }


@app.delete("/peer/{peer_id}")
async def unregister_peer(peer_id: str):
    """
    Unregister a peer.
    
    Args:
        peer_id: Peer ID to unregister
        
    Returns:
        Success message
    """
    if peer_id in peer_registry:
        peer_info = peer_registry[peer_id]
        peer_info.online = False
        logger.info(f"Peer unregistered: {peer_info.username} ({peer_id[:8]}...)")
        return {"status": "success", "message": "Peer unregistered"}
    else:
        raise HTTPException(status_code=404, detail="Peer not found")


@app.get("/status")
async def status():
    """
    Get server status and statistics.
    
    Returns:
        Server status
    """
    total_peers = len(peer_registry)
    online_peers = len([p for p in peer_registry.values() if p.online])
    
    return {
        "status": "running",
        "total_peers": total_peers,
        "online_peers": online_peers,
        "peer_list": [
            {
                "peer_id": p.peer_id[:16] + "...",
                "username": p.username,
                "online": p.online
            }
            for p in peer_registry.values()
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting P2P Chat Signaling Server...")
    # Bind to all interfaces (0.0.0.0) to allow connections from any network
    # This is intentional for a signaling server that needs to be publicly accessible
    logger.info("Server will listen on http://0.0.0.0:8000")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
