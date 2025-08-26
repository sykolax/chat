import sys
import socket
import selectors
import types

HOST = "0.0.0.0"
PORT = 65432

def accept(sock):
    # accept the connection
    conn, addr = sock.accept() # new client socket to read/write data from
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    sel.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    # mask can be 1(0001, only readable), 2(wr), 3(both)
    # EVENT_READ is 1(0001)
    # since mask describes what happened to this socket,
    # this means did a READ event happen here at the moment of the select()
    # if it's ready for reading
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            data.outb += recv_data # write it to another client
        else:
            # client has closed their socket
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]

# selectors see which sockets are ready to r/w
# it keeps track of all the sockets
# each socket can be registered for r/w or both
sel = selectors.DefaultSelector()

# listening socket
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((HOST, PORT))
lsock.listen()
print(f"Listening on {(HOST, PORT)}")
# instead of waiting for the data to come(blocking),
# it handles other tasks to serve multiple clients
lsock.setblocking(False)
# register the socket to monitor - listening socket
# EVENT_READ : tell me when this socket is readable,
# for listening socket, it means a new client is trying to connect
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    while True:
        # blocks until at least one socket is ready / timeout
        # returns a list of tuples one for each socket
        # key containes fileobj(socket object)
        # mask: integer bitmask describing what happened on that file object
        # during the iteration of the event loop
        # it tells you what kind of event happened(readable, writable or both)
        events = sel.select(timeout=None)

        for key, mask in events:
            if key.data is None:
                # socket is listening socket
                accept(key.fileobj) # connect to the socket
            else:
                # accepted socket that needs to be serviced
                service_connection(key, mask)
except KeyboardInterrupt:
    print("Bye")
finally:
    sel.close()
