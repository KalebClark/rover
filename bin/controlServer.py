#
# kcRover Control SERVER
# LOC: Rover
# IP: 192.168.1.190
#
# Control Server
# Recieves info from groundstation and processes.

import zmq
import time
import json

class ControlServer(object):

    payload = {}
    serverIP   = '*'
    serverPORT = '5550'
    cycles = 0

    def __init__(self):
        # Init class
        self.serverAddr = "tcp://"+self.serverIP+":"+self.serverPORT
        self.connect()

    def connect(self):
        # Bind socket for listening
        self.context = zmq.Context(1)
        self.socket  = self.context.socket(zmq.REP)
        self.socket.bind(self.serverAddr)

    def process(self):
        # Receive the payload from server
        payload = json.loads(self.socket.recv())
        sequence = payload['seq']
        print(payload['control'])
        self.cycles += 1

        # Do work

        print("I: Normal request (%s)" % sequence)
        time.sleep(.01)

        # Send ack sequence back to server
        self.socket.send(str(sequence))


control = ControlServer()

while True:
    control.process()
