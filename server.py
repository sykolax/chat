import socket
import selectors
import types

HOST = "0.0.0.0"
PORT = 65433

sel = selectors.DefaultSelector()
messages = []
clients = dict()

# accept connection and register to selecotrs
def accept(sock):
    conn, addr = sock.accept()
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    sel.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, data)
    clients[conn] = data

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    # ready for reading
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            print(f"data: {recv_data!r}")

            # broadcast to other clients
            for client in clients.keys():
                if client != sock:
                    try:
                        client.send(recv_data)
                    except Exception as e:
                        print(f"Error sending to {client}: {e}")

        else:
            # client has closed their socket
            for client in clients:
                if client != sock:
                    clients[client].inb = data.inb
            data.inb = b""
            sel.unregister(sock)
            sock.close()
            del clients[sock]

    # ready for writing
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lsock.bind((HOST, PORT))
lsock.listen()
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    while True:
        events = sel.select(timeout=None)

        for key, mask in events:
            if key.data is None:
                # listening socket
                accept(key.fileobj)
            else:
                service_connection(key, mask)

except KeyboardInterrupt:
    print("Bye")
finally:
    sel.close()
