#!/usr/bin/env python
# kcRover Control SERVER
# LOC: Rover
# IP: 192.168.1.190
#
# Control Server
# Recieves info from groundstation and processes.

#sys.path.append('/opt/rover/lib')
# from dklib import dklib
import ConfigParser
import json
import logging
import math
import zmq
from numpy import interp
from Adafruit_PWM_Servo_Driver import PWM


#from lib.Adafruit_PWM_Servo_Driver.Adafruit_PWM_Servo_Driver import PWM


# Configure Config File
###############################################################################
configFile = "/opt/rover/etc/rover.cfg"
config = ConfigParser.RawConfigParser()
config.read(configFile)

# Configure Logging
###############################################################################
logging.basicConfig(
    #filename="/opt/rover/logs/control-server.log",
    filename=config.get('control', 'logfile'),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S %p",
    level=logging.DEBUG
)

class ControlServer(object):

    payload = {}
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
        self.pwm = PWM(0x40, debug=config.get('control', 'pwm_debug'))
        self.pwm.setPWMFreq(config.get('control', 'pwm_freq'))

    def connect(self):
        # Bind socket for listening
        logging.info("Binding to address: %s", self.serverAddr)
        self.context = zmq.Context(1)
        self.socket  = self.context.socket(zmq.REP)
        self.socket.bind(self.serverAddr)

    def process(self):
        log_every = config.get('control', 'logevery')

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

# Setup ZMQ Server
###############################################################################
server = ControlServer(
    config.get('zeromq', 'protocol').replace('\'', ''),
    config.get('rover', 'ip_address').replace('\'', ''),
    config.get('zeromq', 'port')
)

# TODO: probably should move these to a class of their own, or integrate with ControlServer
def axis2PWM(value):
    return int(math.floor(interp(value, [0, 100], [228, 533])))
    #return int(math.floor(interp(value, [-1.0, 0.9999], [228, 533])))

def fltmode2PWM(value):
    return int(math.floor(interp(value, [-1.0, 0.9999], [228, 533])))

def mode2PWM(value):
    return int(math.floor(interp(value, [1, 100], [228, 533])))

while True:
    payload = None
    payload = server.process()
    print payload


    # Process STEERING
    steer = axis2PWM(payload['control']['steer'])
    server.pwm.setPWM(0, 0, steer)

    # Process THRUST
    thrust = axis2PWM(payload['control']['thrust'])
    server.pwm.setPWM(1, 0, thrust)

    # Process CAMERA CONTROL AXIS
    camera_x = axis2PWM(payload['control']['camera']['x'])
    #camera_y = axis2PWM(payload['control']['camera']['y'])
    server.pwm.setPWM(7, 0, camera_x)

    # Process CAMERA SWITCHING

    # Process FLIGHT MODES
    fltmode = fltmode2PWM(payload['control']['fltmode'])
    server.pwm.setPWM(8, 0, fltmode)

