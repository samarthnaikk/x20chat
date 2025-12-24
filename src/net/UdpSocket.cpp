#include "net/UdpSocket.h"

#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>

UdpSocket::UdpSocket() : m_fd(-1) {}

UdpSocket::~UdpSocket() {
    if (m_fd != -1) {
        close(m_fd);
        m_fd = -1;
    }
}

bool UdpSocket::open(unsigned short port) {
    m_fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (m_fd < 0)
        return false;

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(port);

    if (bind(m_fd, (sockaddr*)&addr, sizeof(addr)) < 0)
        return false;

    return true;
}

bool UdpSocket::sendTo(const std::string& ip,
                       unsigned short port,
                       const std::string& data) {
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);

    if (inet_pton(AF_INET, ip.c_str(), &addr.sin_addr) <= 0)
        return false;

    int sent = sendto(m_fd, data.c_str(), data.size(), 0,
                      (sockaddr*)&addr, sizeof(addr));

    return sent == (int)data.size();
}

bool UdpSocket::recvFrom(std::string& data,
                         std::string& senderIp,
                         unsigned short& senderPort) {
    char buffer[2048];
    sockaddr_in sender{};
    socklen_t len = sizeof(sender);

    int received = recvfrom(m_fd, buffer, sizeof(buffer), 0,
                            (sockaddr*)&sender, &len);

    if (received <= 0)
        return false;

    data.assign(buffer, received);
    senderIp = inet_ntoa(sender.sin_addr);
    senderPort = ntohs(sender.sin_port);

    return true;
}
