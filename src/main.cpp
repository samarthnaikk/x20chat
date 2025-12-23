#include <iostream>
#include <cstring>
#include "net/Socket.h"

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: ./p2p_chat server|client\n";
        return 1;
    }

    std::string mode = argv[1];

    if (mode == "server") {
        Socket server;
        server.create();
        server.bind(5555);
        server.listen();

        std::cout << "Server waiting...\n";
        Socket* client = server.accept();

        char buffer[128] = {};
        client->recv(buffer, sizeof(buffer));
        std::cout << "Server received: " << buffer << std::endl;

        delete client;
    }
    else if (mode == "client") {
        Socket client;
        client.create();
        client.connect("127.0.0.1", 5555);

        const char* msg = "Hello from client";
        client.send(msg, strlen(msg));
    }
    else {
        std::cerr << "Invalid mode\n";
    }

    return 0;
}
