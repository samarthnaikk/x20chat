#include "net/Socket.h"

#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>

Socket::Socket() : m_fd(-1) {}

Socket::~Socket() {
    close();
}

bool Socket::create() {
    m_fd = socket(AF_INET, SOCK_STREAM, 0);
    return m_fd != -1;
}

bool Socket::bind(unsigned short port) {
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    addr.sin_addr.s_addr = INADDR_ANY;

    return ::bind(m_fd, (sockaddr*)&addr, sizeof(addr)) == 0;
}

bool Socket::listen(int backlog) {
    return ::listen(m_fd, backlog) == 0;
}

Socket* Socket::accept() {
    int client_fd = ::accept(m_fd, nullptr, nullptr);
    if (client_fd == -1) return nullptr;

    Socket* client = new Socket();
    client->m_fd = client_fd;
    return client;
}

bool Socket::connect(const std::string& host, unsigned short port) {
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);

    if (inet_pton(AF_INET, host.c_str(), &addr.sin_addr) <= 0)
        return false;

    return ::connect(m_fd, (sockaddr*)&addr, sizeof(addr)) == 0;
}

int Socket::send(const void* data, size_t size) {
    return ::send(m_fd, data, size, 0);
}

int Socket::recv(void* buffer, size_t size) {
    return ::recv(m_fd, buffer, size, 0);
}

void Socket::close() {
    if (m_fd != -1) {
        ::close(m_fd);
        m_fd = -1;
    }
}
