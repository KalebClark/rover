#!/usr/bin/env python
import sys
import re
import os
from ConfigParser import SafeConfigParser
from subprocess import PIPE, Popen
from termcolor import colored

import socket
import fcntl
import struct

# Read Config File
conf = SafeConfigParser()
conf.read('/opt/rover/etc/rover.cfg')

ip_addr_rvr = conf.get('network', 'ip_rvr')
ip_addr_gs  = conf.get('network', 'ip_gs')
ip_addr_rvr_rtr = conf.get('network', 'ip_rvr_rtr')
ip_addr_gs_rtr = conf.get('network', 'ip_gs_rtr')
rvr = ip_addr_rvr
gs = ip_addr_gs
ip_local = None
ip_remote = None

cmd = sys.argv[1]

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def check_ping(hostname):
    sys.stdout.write(colored('Network:\t', 'white', attrs=['bold']))
    response = os.system("ping -c 1 " + hostname + " > /dev/null 2>&1")
    # and then check the response...
    if response == 0:
        pingstatus = True
    else:
        pingstatus = False

    if(pingstatus):
        print("%s\t(%s)" % (colored('CHECK', 'green'), hostname))
    else:
        print("%s\t(%s)" % (colored('FAIL', 'red'), hostname))

    #return pingstatus

def cmdline(command):
    process = Popen(
        args=command,
        stdout=PIPE,
        stderr=PIPE,
        shell=True
    )
    return process.communicate()[0]

def check_process(host, title, file_name):
    sys.stdout.write(colored(title+":\t", 'white', attrs=['bold']))
    pid = cmdline("ssh root@"+host+" 'cat "+file_name+"'")

    if(not pid):
        print("%s\t(NO PID)" % colored('FAIL', 'red'))
        return

    ps_cmd = cmdline("ssh root@"+host+" 'ps --no-headers -o %p "+pid+"'").rstrip()

    if(ps_cmd):
        print("%s\t(%s)" % (colored('CHECK', 'green'), ps_cmd))
    else:
        print("%s\t(NO PID)" % colored('FAIL', 'red'))

# Returns cpu % and FREE memory
def check_system(host):
    cpu_cmd = "top -b1 -n1 | grep Cpu | awk '{print $2 + $4}'"
    mem_cmd = "free -mh | grep Mem | awk '{print $4}'"
    cpu = cmdline("ssh root@"+host+" "+cpu_cmd).rstrip()
    mem = cmdline("ssh root@"+host+" "+mem_cmd).rstrip().replace('M', '')

    sys.stdout.write(colored("CPU < 20%\t", 'white', attrs=['bold']))

    if(round(float(cpu)) < 20):
        print("%s\t(%s)" % (colored('CHECK', 'green'), cpu))
    else:
        print("%s\t(%s)" % (colored('FAIL', 'red'), cpu))

    # Memory Check
    sys.stdout.write(colored("Memory Free:\t", 'white', attrs=['bold']))
    if(int(mem) > 300):
        print("%s\t(%s)" % (colored('CHECK', 'green'), mem))
    else:
        print("%s\t(%s)" % (colored('FAIL', 'red'), mem))

    return [cpu.rstrip(), mem.rstrip().replace('M', '')]
    



def do_status():

    print "================================================================"
    print "| Network Status"
    print "================================================================"
    check_ping(ip_addr_rvr)
    check_ping(ip_addr_gs)
    check_ping(ip_addr_gs_rtr)
    check_ping(ip_addr_rvr_rtr)

    print
    print "================================================================"
    print "| Ground Station STATUS"
    print "================================================================"
    # Ping Check
    check_ping(ip_addr_gs)

    # Control Check
    check_process(ip_addr_gs, 'Control', "/var/run/control.pid")
    check_process(ip_addr_gs, 'Monit  ', "/var/run/monit.pid")

    check_system(ip_addr_gs)

    print
    print "================================================================"
    print "| Rover STATUS"
    print "================================================================"
    rvr_ping = check_ping(ip_addr_rvr)

    check_process(ip_addr_rvr, 'Control', "/var/run/control.pid")
    check_process(ip_addr_rvr, 'MavProxy', "/var/run/mavproxy.pid")
    check_process(ip_addr_rvr, 'Monit  ', "/var/run/monit.pid")

    check_system(ip_addr_rvr)

def do_stop_control(host):
    output = cmdline("ssh root@"+host+" /opt/rover/etc/init.d/control stop")
    print output

def do_start_control(host):
    output = cmdline("ssh root@"+host+" /opt/rover/etc/init.d/control start")
    print output

# Figure out what host we are on
if get_ip_address('eth0') == ip_addr_rvr.replace('\'', ''):
    ip_local    = ip_addr_rvr
    ip_remote   = ip_addr_gs
elif get_ip_address('eth0') == ip_addr_gs.replace('\'', ''):
    ip_local    = ip_addr_gs
    ip_remote   = ip_addr_rvr 
else:
    print "No matches on IP addresses"


# Aliass
if len(sys.argv) > 2:
    if(sys.argv[2] == 'rvr'):
        cmd_host = ip_addr_rvr
    elif(sys.argv[2] == 'gs'):
        cmd_host = ip_addr_gs

if cmd == 'status':
    do_status()
elif cmd == 'stop-control':
    do_stop_control(cmd_host)
    check_process(cmd_host, 'Control', '/var/run/control.pid')
elif cmd == 'start-control':
    do_stop_control(cmd_host)
    do_start_control(cmd_host)
    check_process(cmd_host, 'Control', '/var/run/control.pid')
elif cmd == 'restart-control':
    print colored("Restarting Groundstation Control", 'white', attrs=['bold'])
    do_stop_control(ip_addr_gs)
    do_start_control(ip_addr_gs)
    check_process(ip_addr_gs, 'Control', '/var/run/control.pid')

    print
    print colored("Restarting Rover Control", 'white', attrs=['bold'])
    do_stop_control(ip_addr_rvr)
    do_start_control(ip_addr_rvr)
    check_process(ip_addr_rvr, 'Control', '/var/run/control.pid')
elif cmd == 'sync-self':
    do_sync_self()
elif cmd == 'sync-conf':
    do_sync_conf()
else:
    print "Usage: %s command" % sys.argv[0]
    print "Commands:"
    print "\tstatus"
    print "\tstop-control"
    print "\tsync-self"
    print "\tsync-conf"
