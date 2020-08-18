cmake_minimum_required(VERSION 2.8)
project( SocketClient )
find_package( OpenCV REQUIRED core highgui imgcodecs)

include_directories( ${OpenCV_INCLUDE_DIRS} )
include_directories( . )

ADD_DEFINITIONS ( -march=native -std=c++11 )

add_executable( socket_client socket_client.cpp )
target_link_libraries( socket_client ${OpenCV_LIBS} )

