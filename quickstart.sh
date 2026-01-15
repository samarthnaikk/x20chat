#!/bin/bash
# Quick start script for P2P Chat MVP

echo "====================================="
echo "P2P Chat MVP - Quick Start"
echo "====================================="
echo ""
echo "This script will help you get started with the P2P Chat MVP"
echo ""

# Check Python version
python3 --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

echo "Step 1: Installing dependencies..."
pip3 install -r requirements.txt --quiet

echo ""
echo "Step 2: Starting signaling server..."
echo "   Opening in new terminal (you may need to do this manually)"
echo ""
echo "   Run this command in a separate terminal:"
echo "   cd server && python3 signaling_server.py"
echo ""

read -p "Press Enter when the signaling server is running..."

echo ""
echo "Step 3: Instructions for running peers"
echo ""
echo "To start a peer, run in separate terminals:"
echo ""
echo "   Terminal 2 (Peer Alice):"
echo "   cd client && python3 peer.py --username Alice --server http://localhost:8000"
echo ""
echo "   Terminal 3 (Peer Bob):"
echo "   cd client && python3 peer.py --username Bob --server http://localhost:8000"
echo ""
echo "When Bob starts, he will see Alice in the peer list."
echo "Copy Alice's peer ID and enter it when prompted to connect."
echo ""
echo "Then start chatting! Type messages and press Enter."
echo "Type '/quit' to exit."
echo ""
echo "====================================="
echo "For testing across networks:"
echo "====================================="
echo ""
echo "1. Deploy signaling server on a public server"
echo "2. Replace 'localhost' with the server's public IP"
echo "3. Ensure port 8000 is open on the server"
echo "4. Run peers on different networks"
echo ""
echo "====================================="
