# kcRover Control SERVER
# LOC: Rover
# IP: 192.168.1.190
#
# dklib
# DroneKit Library

from dronekit import connect, VehicleMode
import time



class DKLib(object):

    # lat = None
    # rel_lat = None
    # lon = None
    # rel_lon = None
    # altitude = None
    # rel_altitude = None
    # heading = None
    # pitch = None
    # yaw = None
    # roll = None
    # battVoltage = None
    # battCurrent = None
    # battLevel = None
    # system_status = None
    interval = None
    start_time = time.time()


    def __init__(self):
        self.vehicle = self.vehicleConnect()
        self.interval = time.time()
        self.update

    def vehicleConnect(self, vHost='192.168.1.190', vPort='14551'):
        print("Connecting to Vehicle on %s:%s" % (vHost, vPort))
        vehicle = connect(vHost+':'+vPort, wait_ready=True)
        return vehicle

    def update(self):
        self.lat            = self.vehicle.location.global_frame.lat
        self.rel_lat        = self.vehicle.location.global_relative_frame.lat
        self.lon            = self.vehicle.location.global_frame.lon
        self.rel_lon        = self.vehicle.location.global_relative_frame.lon
        self.altitude       = self.vehicle.location.global_frame.alt
        self.rel_altitude   = self.vehicle.location.global_relative_frame.alt
        self.heading        = self.vehicle.heading
        self.pitch          = self.vehicle.attitude.pitch
        self.yaw            = self.vehicle.attitude.yaw
        self.roll           = self.vehicle.attitude.roll
        # self.battVoltage    = self.battery.voltage
        # self.battCurrent    = self.battery.current
        # self.battLevel      = self.battery.level
        self.system_status  = self.vehicle.system_status.state
        self.velocity_x     = self.vehicle.velocity[0]
        self.velocity_y     = self.vehicle.velocity[1]
        self.velocity_z     = self.vehicle.velocity[2]
        self.mode           = self.vehicle.mode

        return {
            'mode': self.mode,
            'lat':  self.lat,
            'lon': self.lon,
            'rel_lat': self.rel_lat,
            'rel_lon': self.rel_lon,
            'altitude': self.altitude,
            'rel_altitude': self.altitude,
            'heading': self.heading,
            'pitch': self.pitch,
            'yaw': self.yaw,
            'roll': self.roll,
            'status': self.system_status,
            'velocity_x': self.velocity_x,
            'velocity_y': self.velocity_y,
            'velocity_z': self.velocity_z
        }


# dk = DKLib()
#
# while True:
#     time.sleep(.5)
#     telem = dk.update()
#     print dk.start_time
    #print(telem)
    # print('Vehicle Location: lat(%s) lon(%s) alt(%s) ' % (dk.lat, dk.lon, dk.altitude))
    # print('Vehicle rel location lat(%s) lon(%s) alt(%s) ' % (dk.rel_lat, dk.rel_lon, dk.rel_altitude))
    # print('Altitude: %s' % dk.altitude)
    # print('Vehicle Heading: %s' % dk.heading)
    # print('Vehicle attitude: %s' % dk.pitch)
    # print('Vehicle Status: %s' % dk.system_status)
