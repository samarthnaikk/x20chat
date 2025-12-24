#include "protocol/Message.h"
#include <arpa/inet.h>

bool sendMessage(Socket* sock, const std::string& msg) {
    uint32_t len = htonl(msg.size());

    if (sock->send(&len, sizeof(len)) != sizeof(len))
        return false;

    if (sock->send(msg.data(), msg.size()) != (int)msg.size())
        return false;

    return true;
}

bool recvMessage(Socket* sock, std::string& msg) {
    uint32_t lenNet;
    int received = sock->recv(&lenNet, sizeof(lenNet));
    if (received <= 0) return false;

    uint32_t len = ntohl(lenNet);
    msg.resize(len);

    size_t total = 0;
    while (total < len) {
        int bytes = sock->recv(&msg[total], len - total);
        if (bytes <= 0) return false;
        total += bytes;
    }

    return true;
}
