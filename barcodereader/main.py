#!/usr/bin/env python

import qrcode

f=open('TDS_TestReport.txt','w')

print "Welcome to use QR code scanner!"
while True:
	action=raw_input("Please type options. (Type --help for help info) ")
	if action=="--help":
		print "===================="
		print "= 1: start new scan"
		print "= 2: quit scan"
		print "===================="	
	elif action== str(1):
		tdsid=qrcode.decode().strip()
		print "TDSID:",tdsid
		f.write(tdsid)
	elif action== str(2):
		print "Terminating program ..."
		break;
	else:
		print "You must be kidding ... Type --help for availabe options"

f.close()
