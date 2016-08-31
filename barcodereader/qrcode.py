#!/usr/bin/env python

# prototype module to decode QR code
# Note: need to install folllowing packages
# imagemagick zbar, zbar-devel package
# Liang Guan June 2016


import os
import signal
import subprocess


def decode():
	zbarcam=subprocess.Popen("zbarcam --raw /dev/video0", stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
	print "---open zbarcam (success) ..."
	i=0
	while i<1:
		qrcodetext=zbarcam.stdout.readline()
		if qrcodetext !="":
			print "---scan QR code (success) ..."
			i+=1
	os.killpg(zbarcam.pid,signal.SIGTERM)
	print "---close zbarcam (success) BYE BYE!"
	return  qrcodetext
