cmake_minimum_required(VERSION 3.10)

project(p2p_chat LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Include headers
include_directories(include)

# Collect all source files
file(GLOB_RECURSE SOURCES
    src/*.cpp
)

# Create executable
add_executable(p2p_chat ${SOURCES})
