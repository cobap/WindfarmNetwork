#!/usr/bin/python

# Import socket module
import socket

# Create a socket object
s = socket.socket()
# Get local machine name
host = socket.gethostname()
# Reserve a port for your service.
port = 3334
# Bind to the port
s.bind((host, port))

# Now wait for client connection.
s.listen(5)

while True:
    # Establish connection with client.
    c, addr = s.accept()
    print ('Got connection from' + str(addr))
    c.send('Thank you for connecting'.encode())
    # Close the connection
    c.close()
