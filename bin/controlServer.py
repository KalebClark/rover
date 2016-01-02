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
        payload = self.socket.recv()
        self.cycles += 1

        # Do work

        print("I: Normal request (%s)" % payload)
        time.sleep(.1)

        # Send payload back to server
        self.socket.send(payload)


    def ack(self):
        self.socket.send('ack')


control = ControlServer()

while True:
    control.process()
