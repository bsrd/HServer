import threading, queue
import socket
from HttpMessageParser import *


# Class HServer is the HTTP Server.
class HServer:
    # Constructor to initiate several HTTP Server variables.
    def __init__(self, port, workers):
        # The port where the HTTP Server will listen for client.
        self.port = port
        # Number of workers to handle the client connection (number of thread).
        self.workers = workers
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Create queue to store the client request/connection.
        self.client_queue = queue.Queue()

    # Get socket client from queue if queue is not empty.
    # This will run in different thread from the main thread.
    def get_client(self):
        while True:
            if not self.client_queue.empty():
                print('Queue is not empty, getting client from queue.')
                client_socket = self.client_queue.get(block=True)

                print('Worker', threading.currentThread(), end=' ')
                print('Processing client: ', client_socket)
                data = client_socket.recv(4096)

                # Embedded object.
                embedded_object = 0

                # Data ready.
                data_ready = True

                # As long data is received.
                while data_ready:
                    request = repr(data)

                    # Display the request from client (requirement #2).
                    print('Received data: ', request)

                    if str(request) != "b''":
                        # Display the request from client (requirement #2).
                        print('Parsing data: ', request)
                        # Parse data.
                        http_parser = HttpMessageParser(request)
                        ret_message, file_content, keep_alive = http_parser.parse_data()
                        client_socket.send(bytes(ret_message, 'utf-8'))
                        client_socket.send(file_content)

                        # Get more data if keep alive and embedded object is less than 2
                        if keep_alive or embedded_object < 2:
                            print('Get more data', keep_alive, embedded_object)
                            print('Worker', threading.currentThread(), end=' ')
                            print('Processing client: ', client_socket)
                            data = client_socket.recv(4096)
                            data_ready = True
                            embedded_object = embedded_object + 1

                        else:
                            # Close connection if not keep alive.
                            if not keep_alive or embedded_object >= 2:
                                print('Closing due ', keep_alive, embedded_object)
                                client_socket.shutdown(socket.SHUT_WR)
                                client_socket.close()
                                embedded_object = 0
                                data_ready = False

                    else:
                        data_ready = False

    def start(self):
        # Start socket to bind in localhost with port supplied from outside.
        self.socket.bind(('localhost', self.port))

        # Server socket is listening in specified port.
        self.socket.listen(5)
        print('HServer is listening in localhost port ', self.port)

        # Start a pool of number of workers specified from the host.
        for worker_index in range(self.workers):
            worker_thread = threading.Thread(target=self.get_client, name='worker %i' % (worker_index + 1))
            worker_thread.start()

        # Keep accepting client.
        print('HServer is accepting client...')
        while True:
            # When accepting client, create thread (non-persistent connection).
            (client_socket, address) = self.socket.accept()
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Put the client in queue.
            print('Putting new client from address ', address)
            self.client_queue.put(client_socket)
