import sys
import time
sys.path.append('/opt/rover/lib')
from control_server import control_server

server = control_server.ControlServer(
    '*',
    '5550'
)

while True:
    data = server.process()
    print(data)
    time.sleep(.0025)
