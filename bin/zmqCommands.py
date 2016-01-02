# 0MQ Server to receive commands from ground station

import time
import zmq

context = zmq.Context()
socket  = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    message = socket.recv()
    print("Received: %s" % message)
    time.sleep(.5)

    socket.send("Thanks.")
