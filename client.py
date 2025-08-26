import selectors
import socket
import types
import sys

sel = selectors.DefaultSelector()

HOST = "0.0.0.0"
PORT = 65433

sel = selectors.DefaultSelector()

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    # data ready to read
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            print(f"anonymous meow: {recv_data.decode()}")
            data.inb += recv_data
        else:
            data.inb = b""

    if mask & selectors.EVENT_WRITE:
        if data.outb:
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]
        else:
            sel.modify(sock, selectors.EVENT_READ, data=data)

server_addr = (HOST, PORT)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setblocking(False)
sock.connect_ex(server_addr)
events = selectors.EVENT_READ
data = types.SimpleNamespace(
    inb=b"",
    outb=b"",
)
sel.register(sock, events, data=data)
sel.register(sys.stdin, selectors.EVENT_READ, data=None)

print("To quit, enter /quit.")

try:
    connect = True
    while connect:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.fileobj is sock:
                service_connection(key, mask)
            elif key.fileobj is sys.stdin:
                line = sys.stdin.readline().rstrip("\n")
                if line == "/quit":
                    connect = False
                    break
                data.outb = line.encode()
                sel.modify(sock, selectors.EVENT_READ | selectors.EVENT_WRITE, data=data)

except KeyboardInterrupt:
    print("Bye")

finally:
    sel.close()
