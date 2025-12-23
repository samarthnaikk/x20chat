#pragma once

#include <string>

class Socket {
public:
    Socket();
    ~Socket();

    bool create();
    bool bind(unsigned short port);
    bool listen(int backlog = 5);
    Socket* accept();

    bool connect(const std::string& host, unsigned short port);

    int send(const void* data, size_t size);
    int recv(void* buffer, size_t size);

    void close();

private:
    int m_fd;   // socket file descriptor
};
