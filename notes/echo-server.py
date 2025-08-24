import socket

# accept connections on any of my machine's IP address
# if using 127.0.0.1 loopback interface, the data doesn't leave the host or touches the external network
# if not, it's bound to an Ethernet interface
HOST = "0.0.0.0"
PORT = 65432

# specify address family and socket type
# AF_INET for Ipv4, SOCK_STREAM for TCP connection
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # associate the socket with specific network interface and port num
    # to be known so that clients can reach
    s.bind((HOST, PORT))
    # listens to incoming connections
    # listen(backlog) => can specify the number of unaccepted connections
    # befroe refusing new connections
    s.listen()
    # when a client connects, it creates a new socket for that connection
    # returns the socket object and address tuple of the client(host, port for ipv4connections)
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        # loop over blocking calls to conn.recv()
        # blocking call: socket function or method that temporarily suspends application
        # they have to wait on system calls(I/O) to complete before they can return a value
        while True:
            # conn.recv(buffer_size, max number of bytes to read from the socket at once)
            data = conn.recv(1024)
            # if client sends b'' empty bytes object, connection is closed
            if not data:
                break
            # echos back the data sent
            conn.sendall(data)

# Chceck the network stat by netstat -an
