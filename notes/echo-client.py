import socket

HOST = "0.0.0.0"
PORT = 65432

# Creates socket object, connect to the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    # sends the message in bytes
    s.sendall(b"Hello world!")
    # read server's reply
    data = s.recv(1024)

# !r -> repr(obj) instead of str(obj)
# doesn't render special characters \n or \t
# easy to debug
print(f"Received {data!r}")
