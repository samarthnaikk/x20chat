#include <iostream>
#include <unordered_map>
#include <string>
#include <sstream>

#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>

struct Peer {
    sockaddr_in addr;
};

int main() {
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        perror("socket");
        return 1;
    }

    sockaddr_in serverAddr{};
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = INADDR_ANY;
    serverAddr.sin_port = htons(3478);

    if (bind(sock, (sockaddr*)&serverAddr, sizeof(serverAddr)) < 0) {
        perror("bind");
        return 1;
    }

    std::unordered_map<std::string,
        std::unordered_map<std::string, Peer>> rooms;

    std::cout << "Rendezvous server listening on UDP 3478\n";

    while (true) {
        char buffer[1024];
        sockaddr_in clientAddr{};
        socklen_t len = sizeof(clientAddr);

        int n = recvfrom(sock, buffer, sizeof(buffer) - 1, 0,
                         (sockaddr*)&clientAddr, &len);
        if (n <= 0) continue;

        buffer[n] = '\0';
        std::istringstream iss(buffer);

        std::string cmd, name, room;
        iss >> cmd >> name >> room;

        if (cmd != "REGISTER") continue;

        rooms[room][name] = {clientAddr};

        std::cout << "REGISTER " << name << " in room " << room
                  << " at "
                  << inet_ntoa(clientAddr.sin_addr) << ":"
                  << ntohs(clientAddr.sin_port) << "\n";

        for (auto& [otherName, peer] : rooms[room]) {
            if (otherName == name) continue;

            std::string toNew =
                "PEER " + otherName + " " +
                inet_ntoa(peer.addr.sin_addr) + " " +
                std::to_string(ntohs(peer.addr.sin_port));

            sendto(sock, toNew.c_str(), toNew.size(), 0,
                   (sockaddr*)&clientAddr, sizeof(clientAddr));

            std::string toOld =
                "PEER " + name + " " +
                inet_ntoa(clientAddr.sin_addr) + " " +
                std::to_string(ntohs(clientAddr.sin_port));

            sendto(sock, toOld.c_str(), toOld.size(), 0,
                   (sockaddr*)&peer.addr, sizeof(peer.addr));
        }
    }

    close(sock);
    return 0;
}
