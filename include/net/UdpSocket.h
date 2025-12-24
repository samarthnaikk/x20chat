#pragma once

#include <string>
#include <netinet/in.h>

class UdpSocket {
public:
    UdpSocket();
    ~UdpSocket();

    bool open(unsigned short port = 0);
    bool sendTo(const std::string& ip, unsigned short port,
                const std::string& data);

    bool recvFrom(std::string& data,
                  std::string& senderIp,
                  unsigned short& senderPort);

private:
    int m_fd;
};
