#!/usr/bin/env python

#======================================================================================
# ver. 1.0
# Liang Guan (guanl@umich.edu)
# June 2016
# Instructions: 
#
# 1. Prerequisite
# Need to install pip "sudo yum install python-pip" and get following python packages:
# (cmd inside "" should be typed without quot. marks)
# - PyVISA "sudo pip install pyvisa" 
# - PyVISA-py "sudo pip install -U https://github.com/hgrecco/pyvisa-py/zipball/master"
# - PySerial "sudo pip install PySerial==2.7"
# 
# 2. One needs sudo privilege to contorl COM ports  
# 3. If program crashes, most likely there is no valid COM port available for use 
#=======================================================================================

# UPDATE NOTICE: 12 Aug 2016
# must install PySerial 2.7 instead of 2.6!
# a bug is found in pySerial 2.6 where follow error could occur when listing serial ports 
#	NameError: global name 'base' is not defined




import time
import visa
rm = visa.ResourceManager("@py") # use pyVISA-py instead of NI-VISA installed earlier 

cmdlist=[
	"*IDN?",
	"*TST?",
	"*RST",
	"SYSTem:REMote",
	"SYSTem:BEEPer",
	"SYSTem:ERRor?",
	"APPLy?",
	"VOLTage?",
	"VOLT 3.0",
	"CURRent",
	"APPLy 6.0,5.0",
	"OUTPut ON",
	"OUTPut OFF",
	"INSTrument:NSELect?",
	"INSTrument:NSELect 1",
	"INSTrument:NSELect 2",
	"MEASure:CURRent?",
	"MEASure:VOLTage?"
]


print "==============================="
print "Welcome to use serial commander"
serlist=rm.list_resources()
print ">> Serial Ports Found:"
for i,a in enumerate(serlist):
	print ">> ",i,serlist[i]

i=0
psel=0
portid="" #port descriptor

while True:
	psel=raw_input(">> Please select one port to communicate (Type numbers):")
	if i<5:
		print psel
		if str(psel)=="":
			print ">> Please type something"
		elif int(psel)>len(serlist)-1:
			print ">> Error:Port not present!"
		else:
			portid=str(serlist[int(psel)])
			#Need to improve the code 
			#- check if port open success or failed
			# -reset control register
			#- set into remote control mode
			#- do self test
			instr=rm.open_resource(portid)
			print portid," selected!"
			break
	else:
		print ">> Too many error trails. Terminating program..."
		exit()
	i+=1


sercmd=""  # user input
payload="" # pay load to be send
optcmd=""  # write/read/query option
imoni=False

while True:
	sercmd=raw_input(">> Please type cmd (type --help for help)")
	if sercmd=="--help":
		print ">> Exit --> Quit program"
		print ">> Imonitor -->Current monitoring"
		print ">> W CMD --> Write command"
		print ">> R CMD --> Read command"
		print ">> Q CMD --> Write and Read (Query)"
	elif sercmd=="exit":
		rm.close()
		exit()
	elif sercmd=="Imonitor":
		imoni=True
		break
	else:
		payload=sercmd[2:]
		optcmd=sercmd[:1]
		print sercmd, " Option:",optcmd," payload:",payload,len(payload)
		if payload not in cmdlist:
			print ">> Command not recognized! Type it again ... "
		else:
			if optcmd=="W" or optcmd=="w":
				instr.write(payload)
				time.sleep(0.5)
				instr.write("SYSTEM:BEEPer")
				continue
			elif optcmd=="R" or optcmd=="r":
				print instr.read(payload)
                                time.sleep(0.5)
                                instr.write("SYSTEM:BEEPer")
				continue
			elif optcmd=="Q" or optcmd=="q":
				print instr.query(payload)
				time.sleep(0.5)
                                instr.write("SYSTEM:BEEPer")
				continue
			else:
				print "payload invalid!!"



print "Start Monitoring Current..."
while True:
	time.sleep(2)
	if imoni==True:
		print float(instr.query("MEASure:CURRent?")),"A"
		instr.write("SYSTEM:BEEPer")


	
