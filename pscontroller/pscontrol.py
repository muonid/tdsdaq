#!/usr/bin/env python

#======================================================================================
# ver. 1.1
# Liang Guan and Jake Searcy 
# August 2016
# Instructions: 
#
# 1. Prerequisites
# Need to install pip "sudo yum install python-pip" and get following python packages:
# (cmd inside "" should be typed without quot. marks)
# - PyVISA "sudo pip install pyvisa" 
# - PyVISA-py "sudo pip install -U https://github.com/hgrecco/pyvisa-py/zipball/master"
# - PySerial "sudo pip install PySerial==2.7"
# 
# 2. One needs sudo privilege to contorl COM ports  
# 3. Insure 0.1s wait time between sending commands
# 4. If program crashes, most likely no valid COM port is available for use 
#=======================================================================================

# UPDATE: using PySerial 2.6 could through out an error "global name 'base' is not defined"
# Try to install PySerial2.7 instead
# Changed the module name from psutils to powersupplyutils to avoid confusion with psutil library 


import sys
import time
import visa
from termcolor import bcolors

bkgColor = bcolors 

class PsControl():
	def __init__(self,port):

		#place holder: derive PS ID, Serial port ID, PS channel to be controlled

		self.RM = visa.ResourceManager("@py") # use pyVISA-py instead of NI-VISA
		self.SERLIST = self.RM.list_resources()
		self.INSTR = self.RM.open_resource(port)
		self.VOLT = 6.00000  # need to keep five bit after decimail point
		self.ILIMIT = 5.00000 # need to keep five bit after decimail point
		
		self.CMDLIST = [
			"*IDN?",
			"*TST?",
			"*RST",
			"*CLS",
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
	
	def dummy_beeper(self):
		self.INSTR.write("SYSTem:BEEPer")
		return True

	def setup_ps(self):  
		#find PS ID
		psid = self.INSTR.query("*IDN?")			
		print "PowerSupply ID: ",psid
		time.sleep(0.5)
		# power-up self test
		health_status = int (self.INSTR.query("*TST?"))
		if health_status==0:
			print bkgColor.OKGREEN + "INFO: [" + "PS01" + "] " + "SELF TEST PASSED!" + bkgColor.ENDC	
			#--clear ps register errors
			self.INSTR.write("*CLS")
			time.sleep(0.1)
			#--switch to remote control mode
			self.INSTR.write("SYSTEM:REMote")
			time.sleep(0.1)	
			return True
		elif health_status == 1:
			print bkgColor.FAIL + "ERROR: [" + "PS01" + "] " + "SELF TEST FAILED!" + bkgColor.ENDC
			return False
		else:
			print bkgColor.FAIL + "CRITICAL_ERROR: [" + "PS01" + "] " + "UNKNOWN STATUS CODE! PS NEEDS INSPECTION." + bkgColor.ENDC
			return False
	
	def power_on(self):
		self.INSTR.write("INSTrument:NSELect 1")
		time.sleep(0.1)
		self.INSTR.write("APPLy "+str(self.VOLT)+","+str(self.ILIMIT))
		time.sleep(0.1)
		#checking if  configuration is applied
		readback = self.INSTR.query("APPLy?")
		readback = readback.replace("\"","")
		if float(readback.split(',')[0])== self.VOLT and float(readback.split(',')[1])== self.ILIMIT:
			print bkgColor.OKGREEN + "INFO: [" + "PS01" + "] " + "VOLTAGE CONFIGURATION APPLIED!" + bkgColor.ENDC
		else:
			print bkgColor.FAIL + "ERROR: [" + "PS01" + "] " + "VOLTAGE CONFIGURATION FAILED!" + bkgColor.ENDC 
			return False
		time.sleep(0.1)
		self.INSTR.write("OUTPut ON")
		for iBeep in range (0,3): 
			time.sleep(0.5)
			self.INSTR.write("SYSTem:BEEPer")
		return True

	def power_off(self):
       	       	self.INSTR.write("INSTrument:NSELect 1")
       	       	time.sleep(0.1)
               	self.INSTR.write("OUTPut OFF")
               	for iBeep in range (0,4):
                       	time.sleep(0.1)
                       	self.INSTR.write("SYSTem:BEEPer")
		return True
	
	def send_command(self,command): #ONLY FOR DEBUG USE
		payload=command[2:]
		optcmd=command[:1]
		if payload not in self.cmdlist:
			print ">> Command not recognized! Type it again ... "
			return False
		else:
			if optcmd=="W" or optcmd=="w":
				INSTR.write(payload)
				time.sleep(0.5)
				self.INSTR.write("SYSTEM:BEEPer")
				return
			elif optcmd=="R" or optcmd=="r":
				print INSTR.read(payload)
				time.sleep(0.5)
				self.INSTR.write("SYSTEM:BEEPer")
				return
			elif optcmd=="Q" or optcmd=="q":
				print INSTR.query(payload)
				time.sleep(0.5)
				self.INSTR.write("SYSTEM:BEEPer")
				return
			else:
				print "payload invalid!!"
				time.sleep(2)


	#This needs to be implmented in upper thread
	def read_current(self):
			CURR=0.0
			self.monitor=True
			if self.monitor==True:
				CURR = float(self.INSTR.query("MEASure:CURRent?"))
			return CURR


	
