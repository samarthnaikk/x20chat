#pragma once
#include <string>
#include "net/Socket.h"

bool sendMessage(Socket* sock, const std::string& msg);
bool recvMessage(Socket* sock, std::string& msg);
