#!/bin/bash
(
date
echo $PATH
PATH=$PATH:/bin:/sbin:/usr/bin:/usr/local/bin
export PATH
cd /opt/rover/data
screen -d -m -s /bin/bash mavproxy.py --master=/dev/ttyAMA0 --baudrate 57600 --out 192.168.1.107:14550 --aircraft kcRover
) > /opt/rover/logs/rc.log 2>&1
exit 0
