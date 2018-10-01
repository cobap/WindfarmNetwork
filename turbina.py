#!/usr/bin/python

# Import socket module
import socket

# Create a socket object
s = socket.socket()

# Get local machine name
host = socket.gethostname()

# Reserve a port for your service.
port = 3334

s.connect((host, port))
print (s.recv(1024).decode())
# Close the socket when done
s.close()
