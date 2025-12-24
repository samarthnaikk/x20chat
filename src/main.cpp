#include "net/Socket.h"
#include "protocol/Message.h"

#include <iostream>
#include <thread>
#include <string>
#include <cstring>

void receiveLoop(Socket* sock) {
    std::string msg;
    while (recvMessage(sock, msg)) {
        std::cout << "\n" << msg << std::endl;
    }
    std::cout << "Peer disconnected\n";
}

std::string getArg(int argc, char* argv[], const std::string& key) {
    for (int i = 1; i < argc - 1; i++) {
        if (argv[i] == key)
            return argv[i + 1];
    }
    return "";
}

int main(int argc, char* argv[]) {
    std::string name = getArg(argc, argv, "--name");
    std::string portStr = getArg(argc, argv, "--port");
    std::string connectStr = getArg(argc, argv, "--connect");

    if (name.empty() || portStr.empty()) {
        std::cerr << "Usage: ./p2p_chat --name NAME --port PORT [--connect IP:PORT]\n";
        return 1;
    }

    int port = std::stoi(portStr);

    Socket server;
    server.create();
    server.bind(port);
    server.listen();

    std::cout << "[" << name << "] Listening on port " << port << "...\n";

    std::thread acceptThread([&]() {
        while (true) {
            Socket* peer = server.accept();
            if (!peer) continue;

            std::cout << "\n[" << name << "] Incoming connection\n";
            std::thread(receiveLoop, peer).detach();
        }
    });

    Socket* outbound = nullptr;

    if (!connectStr.empty()) {
        auto pos = connectStr.find(':');
        std::string ip = connectStr.substr(0, pos);
        int peerPort = std::stoi(connectStr.substr(pos + 1));

        outbound = new Socket();
        outbound->create();

        if (outbound->connect(ip, peerPort)) {
            std::cout << "[" << name << "] Connected to " << connectStr << "\n";
            std::thread(receiveLoop, outbound).detach();
        } else {
            std::cerr << "Connection failed\n";
            delete outbound;
            outbound = nullptr;
        }
    }

    std::string input;
    while (std::getline(std::cin, input)) {
        std::string fullMsg = "[" + name + "] " + input;
        if (outbound)
            sendMessage(outbound, fullMsg);
    }

    acceptThread.join();
    return 0;
}
