#!/usr/bin/env python
# kcRover Control SERVER
# LOC: Rover
# IP: 192.168.1.190
#
# Control Server
# Recieves info from groundstation and processes.

import sys
#sys.path.append('/opt/rover/lib')
# from dklib import dklib
import ConfigParser
import zmq
import time
import os
import json
import logging
import math
from numpy import interp
from Adafruit_PWM_Servo_Driver import PWM
import curses
import zlib

# Configure Logging
logging.basicConfig(
    filename="/opt/rover/logs/control-server.log",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S %p",
    level=logging.DEBUG
)

class ControlServer(object):

    payload = {}
    #serverIP   = '*'
    #serverPORT = '5550'
    cycles = 0
    debug = False
    telem = False

    def __init__(self, proto, serverIP, serverPORT):
        # Init class
        self.proto = proto
        self.serverIP = serverIP
        self.serverPORT = serverPORT
        self.serverAddr = self.proto+"://"+self.serverIP+":"+self.serverPORT
        self.connect()

        # Init PWM Driver
        self.pwm = PWM(0x40, debug=False)
        self.pwm.setPWMFreq(60)

    def connect(self):
        # Bind socket for listening
        logging.info("Binding to address: %s", self.serverAddr)
        self.context = zmq.Context(1)
        self.socket  = self.context.socket(zmq.REP)
        self.socket.bind(self.serverAddr)

    def process(self):
        log_every = 1000
        # Receive the payload from server
        payload = None
        payload = json.loads(self.socket.recv())
        sequence = payload['seq']
        self.cycles += 1

        # Log Heartbeat
        if(sequence % log_every) == 0:
            logging.info("Heartbeat Alive. Sequence # %s", sequence)

        # Get Telemetry data
        # if(sequence % (log_every / 4)) == 0:
        #     self.telem = dk.update
        #     logging.info(self.telem)

        # Send ack sequence back to server
        self.socket.send(str(sequence))
        payload.pop('seq', None)
        if self.debug:
            logging.info(payload)
        return payload


#class ServoBlaster(object):
#
#    # Class Variables
#    sb = None
#
#    def __init__(self):
#        self.sb = open('/dev/servoblaster', 'w')
#
#    def write(self, servo, percentage):
#        #logging.info(str(servo)+" - "+str(percentage))
#        cmd = str(servo)+"="+str(percentage)+"%\n"
#        self.sb.write(cmd)
#        self.sb.flush()
#
#    def close(self):
#        self.sb.close()

configFile = "/opt/rover/etc/rover.cfg"
cp = ConfigParser.RawConfigParser()
cp.read(configFile)

server = ControlServer(
    cp.get('network', 'zmq_proto').replace('\'', ''),
    cp.get('network', 'ip_rvr').replace('\'', ''),
    cp.get('network', 'control_port')
)

# Instanciate ServoBlaster
#servo = ServoBlaster()

def axis2PWM(value):
    #return int(math.floor(interp(value, [0, 100], [228, 533])))
    return int(math.floor(interp(value, [-1.0, 0.9999], [228, 533])))

def mode2PWM(value):
    return int(math.floor(interp(value, [1, 100], [228, 533])))

#myscreen = curses.initscr()
#myscreen.border(0)

def cursesDebug(pos, name, value):
    myscreen.addstr(pos, 2, str(name)+":")
    myscreen.addstr(pos, 14, str(value))
    myscreen.refresh()
    #myscreen.getch()

def screenDebug():
    # DEBUG
    my = payload['control']['throttle']['axes']['mousey']
    cursesDebug(2, "Mouse_y", my)
    mx = payload['control']['throttle']['axes']['mousex']
    cursesDebug(4, "Mouse_x", mx)

    ts = payload['control']['throttle']['axes']['topspinner']
    cursesDebug(6, "TopSPin", ts)
    bs = payload['control']['throttle']['axes']['botspinner']
    cursesDebug(7, "TopSPin", bs)

    rty3 = payload['control']['throttle']['axes']['rty3']
    cursesDebug(8, 'rty3', rty3)

    #mode = mode2PWM(payload['control']['throttle']['buttons']['fltmode'])
    #cursesDebug(9, 'mode', mode)

while True:
    payload = None
    payload = server.process()

    #screenDebug()

    # Work control code here
    # =========================================================================

    # Interpolate stick axis - Use for STICK control
    #stick_y = axis2PWM(payload['control']['stick']['y']) # Y Axis
    #server.pwm.setPWM(0, 0, stick_y)
    #stick_x = axis2PWM(payload['control']['stick']['x']) # X Axis
    #server.pwm.setPWM(1, 0, stick_x)

    # Interpolate thrust & twist - use for thrust & twist control
    steer = axis2PWM(payload['control']['stick']['z'])
    server.pwm.setPWM(0, 0, steer)
    thrust = axis2PWM(payload['control']['thrust'])
    server.pwm.setPWM(1, 0, thrust)

    # Interpolate Camera Control
    trim_top = axis2PWM(payload['control']['trim']['top']) # X Axis
    server.pwm.setPWM(7, 0, trim_top)
#    trim_bot = axis2PWM(payload['control']['trim']['bot']) # Y Axis
#    server.pwm.setPWM(8, 0, trim_bot)

    # Flight Modes
    fltmode = axis2PWM(payload['control']['fltmode'])
    #fltmode = axis2PWM(payload['control']['throttle']['axes']['rty3'])
    server.pwm.setPWM(8, 0, fltmode)

