#!/bin/bash


vlc -vvv v4l:/dev/video:norm=secam:frequency=543250:size=640x480:channel=0 --sout '#transcode{vcodec=mp4v,acodec=mpga,vb=3000,ab=256,vt=800000,keyint=80,deinterlace}:std{access=udp,mux=ts,url=192.168.1.107}' --ttl 12
