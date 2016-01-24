from dronekit import connect, VehicleMode
import time

vehicle = connect('192.168.1.190:14551', wait_ready=True)

print("GPS %s" % vehicle.gps_0)
print("Attitude: %s" % vehicle.attitude)
print("heading: %s" % vehicle.heading)

