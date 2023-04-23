import socket

SOCKET_FILE = '/tmp/dc_unix_socket'

# Create a Unix datagram socket
s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

# Send a message to the server
message = b'Hello, server!'
s.sendto(message, SOCKET_FILE)

# Close the socket
s.close()