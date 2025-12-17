# x20chat

A high-performance peer-to-peer chat application built in C++.

## Overview

x20chat is a decentralized messaging platform that enables direct communication between users without requiring a central server. The application leverages modern C++ features and networking protocols to provide secure, efficient, and real-time messaging capabilities.

## Features

- Peer-to-peer messaging architecture
- Real-time message delivery
- Secure communication protocols
- Cross-platform compatibility
- Lightweight and efficient implementation
- No central server dependency

## Requirements

- C++17 compatible compiler (GCC 7.0+, Clang 5.0+, MSVC 19.14+)
- CMake 3.10 or higher
- Network connectivity

## Building from Source

### Linux/macOS

```bash
git clone https://github.com/samarthnaikk/x20chat.git
cd x20chat
mkdir build
cd build
cmake ..
make
```

### Windows

```bash
git clone https://github.com/samarthnaikk/x20chat.git
cd x20chat
mkdir build
cd build
cmake ..
cmake --build .
```

## Usage

### Starting the Application

```bash
./x20chat [options]
```

### Command Line Options

- `-p, --port <port>`: Set the listening port (default: 8080)
- `-h, --help`: Display help information
- `-v, --version`: Show version information

### Basic Operations

1. Start the application
2. Connect to peers using their IP address and port
3. Begin messaging in real-time

## Architecture

The application follows a decentralized P2P model where each client acts as both a client and server. Key components include:

- **Network Layer**: Handles TCP/UDP socket communication
- **Protocol Layer**: Manages message formatting and routing
- **Security Layer**: Implements encryption and authentication
- **User Interface**: Command-line interface for interaction

## Contributing

Contributions are welcome. Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions, issues, or contributions, please open an issue on the GitHub repository.

## Changelog

### Version 1.0.0
- Initial release
- Basic P2P messaging functionality
- Command-line interface