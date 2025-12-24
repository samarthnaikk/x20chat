#include "net/Socket.h"
#include "net/UdpSocket.h"
#include "protocol/Message.h"

#include <iostream>
#include <thread>
#include <string>
#include <sstream>
#include <atomic>

std::string getArg(int argc, char* argv[], const std::string& key) {
    for (int i = 1; i < argc - 1; i++) {
        if (argv[i] == key)
            return argv[i + 1];
    }
    return "";
}

bool parseIpPort(const std::string& s, std::string& ip, unsigned short& port) {
    auto pos = s.find(':');
    if (pos == std::string::npos) return false;
    ip = s.substr(0, pos);
    port = static_cast<unsigned short>(std::stoi(s.substr(pos + 1)));
    return true;
}

int main(int argc, char* argv[]) {
    std::string name = getArg(argc, argv, "--name");
    std::string room = getArg(argc, argv, "--room");
    std::string rendezvousStr = getArg(argc, argv, "--rendezvous");

    if (name.empty() || room.empty() || rendezvousStr.empty()) {
        std::cerr << "Usage: --name NAME --room ROOM --rendezvous IP:PORT\n";
        return 1;
    }

    // ---------------- UDP socket ----------------
    UdpSocket udp;
    udp.open(0);

    std::string rvIp;
    unsigned short rvPort;
    parseIpPort(rendezvousStr, rvIp, rvPort);

    std::string reg = "REGISTER " + name + " " + room;
    udp.sendTo(rvIp, rvPort, reg);

    std::cout << "[" << name << "] Registered with rendezvous\n";

    std::atomic<bool> peerKnown(false);
    std::string peerIp;
    unsigned short peerPort = 0;

    // ---------------- UDP receive thread ----------------
    std::thread recvThread([&]() {
        while (true) {
            std::string msg, ip;
            unsigned short port;

            if (!udp.recvFrom(msg, ip, port))
                continue;

            if (msg.rfind("PEER ", 0) == 0) {
                std::istringstream iss(msg);
                std::string type, peerName;
                iss >> type >> peerName >> peerIp >> peerPort;

                peerKnown = true;

                std::cout << "\n[" << name << "] Discovered peer "
                          << peerName << " at "
                          << peerIp << ":" << peerPort << "\n";

                // ---- HOLE PUNCH ----
                for (int i = 0; i < 5; i++) {
                    udp.sendTo(peerIp, peerPort, "PING");
                }
            }
            else if (msg == "PING") {
                if (!peerKnown) {
                    peerIp = ip;
                    peerPort = port;
                    peerKnown = true;
                }
                udp.sendTo(ip, port, "PONG");
            }
            else if (msg == "PONG") {
                std::cout << "\n[" << name << "] UDP hole punching successful\n";
            }
            else {
                std::cout << "\n[" << name << "] " << msg << std::endl;
            }
        }
    });

    // ---------------- input loop ----------------
    std::string input;
    while (std::getline(std::cin, input)) {
        if (peerKnown) {
            std::string chat = "[" + name + "] " + input;
            udp.sendTo(peerIp, peerPort, chat);
        } else {
            std::cout << "[waiting for peer...]\n";
        }
    }

    recvThread.join();
    return 0;
}
