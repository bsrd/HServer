from HServer import *

# Start HTTP Server in port 8451 with 5 workers (threads in pool).
myServer = HServer(8451,5)
myServer.start()