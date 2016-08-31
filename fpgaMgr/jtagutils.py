#!/usr/bin/env python

# ==========================================================
# jtagutils.py
# ver 1.1
# Liang Guan and Jake Searcy
# 30 August 2016
# 
# 
# A python wrapper to invoke tcl commands in 
# Xilinx tcl shell. Do not confuse with 
# jtagutils.tcl
#
# -- Note:
# 1. several global varivables are defined to monitor 
#    xilinx shell aliveness 
# 2. always connect to hw_server when xilinx shell is
#    open. Always close hw_server when subprcoess is 
#    closed
# 3. AVOID multi-threading this module. 
#
# -- Prerequisites
# pexpect,psutils
#
# ==========================================================
#
# To be improved in this module 
#
# - record vivado,vcse_server,hw_server pids
# 
# To be implemented in main frame:
# - kill vivado,vcse_server,hw_server before any fresh run
# 


from __future__ import absolute_import
from __future__ import unicode_literals
import boardmap
import bitmap
import os.path
import pexpect
import psutil

#default 
pid_jtag_proc = -1 # Default: Not exsit
pid_vivado_proc = -1
pid_vcse_server= -1
pid_hw_server = -1

class JtagUtils():

	def __init__(self,motherboardid,tdsprogramid,runmode="new"):

		global pid_jtag_proc  # pexpect subprocess pid, Not vivado pid 

		# Readin map
		dict_board = boardmap.board.get(motherboardid)
		dict_bit = bitmap.bitstream.get(tdsprogramid)

		self.MBDID = motherboardid
		self.PROGID = tdsprogramid
		self.BITFILE = '' 
		self.PROBFILE = ''
		self.TDSID = ''
		self.FPGAID = ''
		self.JTAGDES = ''

		print "Looking at info associated with board: ",motherboardid
		for bd in dict_board:
			if bd[0] == 'JTAGDES':
				self.JTAGDES = bd[1]
				print "+----JTAGDES:",bd[1]
			elif bd[0] == 'PairedTDSID':
				self.TDSID = bd[1]
				print "+----PairedTDSID:",bd[1]
			elif bd[0] == 'FPGAID':
				self.FPGAID = bd[1]
				print "+----FPGAID:",bd[1]
			elif bd[0] =='MAC':
				print "+----MAC Address:",bd[1]
			else:
				pass

		print "Looking at info associated with test program: ",tdsprogramid
		for pg in dict_bit:
			if pg[0] == 'BITFILE':
				self.BITFILE = pg[1]
				print "+----BITFILE: ",pg[1]
			elif pg[0] == 'PROBFILE':
				self.PROBFILE = pg[1]
				print "+----PROBFILE: ",pg[1]
			else: 
				pass


		# Creat new vivado subprocess or check  
		if (runmode == "new"):
			# -- open xilinx tcl shell
			self.PVIVADO = pexpect.spawn('vivado -mode tcl -nojou -log ./xtcl_backlog/checkhere.log')
			pid_jtag_proc = self.PVIVADO.pid
			print "INFO: [jtagutils.py] new vivado process. Pid: ",pid_jtag_proc

			# -- load jtagutils.tcl 
			self.PVIVADO.sendline('catch {source jtagutils.tcl -notrace}')
			isload_jtagutils = self.PVIVADO.expect('0',timeout=5)
			if isload_jtagutils==0:
				print "INFO: [jtagutils.py] jtagutils.tcl loaded to xtclsh."
			else:
				print "ERROR: [jtagutils.py] can not load jtagutils.tcl"

		elif (runmode == "resume"):
			if (psutil.pid_exists(pid_jtag_proc) == True):
				print "INFO: [jtagutils.py] Vivado shell already openned. Pid: ",pid_jtag_proc
			else:
				print "INFO: [jtagutils.py] No Vivado shell running."
		else:
			print "ERROR: [jtagutils.py] Unrecognized run mode."


	def setup_hardware_server(self):
		if (psutil.pid_exists(pid_jtag_proc) == True):
			print "setup_hardware_server: pid ", pid_jtag_proc, "is still alive..."
			self.PVIVADO.sendline('setup_hardware_server')
			ret_connect_server = self.PVIVADO.expect(['CONNECT_HW_SERVER_OK',
								'Common 17-39',
								pexpect.EOF,
								pexpect.TIMEOUT],
								timeout=30)

			if (ret_connect_server == 0):
				print self.PVIVADO.before,self.PVIVADO.after
				print "INFO: [jtagutils.py] Connect to hardware server - SUCCEEDED!"
				#self.PVIVADO.interact()
				return True
			elif (ret_connect_server == 1):
				print "INFO: [jtagutils.py] Connect to hardware server - FAILED (Common 17-39)!"
				print self.PVIVADO.before,self.PVIVADO.after
				return False
			elif (ret_connect_server == 2):
				print "WARNNING: [jtagutils.py] EOF Found!"
				return False
			elif (ret_connect_server == 3):
				print "ERROR: [jtagutils.py] Time out!!"
				print self.PVIVADO.before,self.PVIVADO.after
				return False
			else:
				print "WARNING: [jtagutils.py] Unable to determine hardware server status"
				return False

		else:
			print "INFO: [jtagutils.py] Vivado process already losed. Do nothing."
			return False

	def deploy_bitstream(self): #automatically open jtag target before deploying bitstream

		# Check bitfile, probefile existence
		if not os.path.isfile(self.BITFILE):
				print "ERROR: [jtagutils.py] Bit file NOT found! Exiting..."
				return False

		if self.PROBFILE!='NA' and (not os.path.isfile(self.PROBFILE)):
				print "ERROR: [jtagutils.py] Probe file NOT found! Exiting..."
				return False

		if (psutil.pid_exists(pid_jtag_proc) == True):
			print "deploy_bitstream: pid ", pid_jtag_proc, "is still alive..."
			cmd = 'deploy_bitstream '+ self.JTAGDES+' '+self.BITFILE+' '+self.PROBFILE
			self.PVIVADO.sendline(cmd)
			ret_deploy_bit = self.PVIVADO.expect(['DEPLOY_BITSTREAM_OK',
								'DEPLOY_BITSTREAM_FAIL',
								'OPEN_HW_TARGET_FAIL',
								pexpect.EOF,
								pexpect.TIMEOUT],
								timeout=120)
			if (ret_deploy_bit == 0):
				print "self.PVIVADO.after:",self.PVIVADO.before
				print "INFO: [jtagutils.py] Deploying bit stream for",self.PROGID,"- SUCCEEDED!"
				return True
			elif (ret_deploy_bit == 1):
				print "ERROR: [jtagutils.py] Deploying bit stream for",self.PROGID,"- FAILED!"
				print self.PVIVADO.before,self.PVIVADO.after
				return False
			elif (ret_deploy_bit == 2):
				print "ERROR: [jtagutils.py] Unable to open hardware. Jtag target ID:",self.JTAGDES
				print self.PVIVADO.before,self.PVIVADO.after
				return False
			elif (ret_deploy_bit == 3):
				print "WARNNING: [jtagutils.py] EOF Found!"
				return False
			elif (ret_deploy_bit == 4):
				print "ERROR: [jtagutils.py] Deploying bit stream - Time out!!"
				print self.PVIVADO.before,self.PVIVADO.after
				return False
			else:
				print "WARNING: [jtagutils.py] Unable to determine bitstream delpoyment status"
				return False

		else:
			print "INFO: [jtagutils.py] Vivado process already losed. Do nothing."
			return True
	

	def eye_scan(self):
		if (psutil.pid_exists(pid_jtag_proc) == True):
			print "eye_scan: pid ", pid_jtag_proc, "is still alive..."
			self.PVIVADO.sendline('eye_scan')
			ret_eyescan = self.PVIVADO.expect(['EYE_SCAN_DONE',
								'No Links Found',
								pexpect.EOF,
								pexpect.TIMEOUT],
								timeout=1000)

			if (ret_eyescan == 0):
				print self.PVIVADO.before,self.PVIVADO.after
				print "INFO: [jtagutils.py] Eye Scan from Board (",self.MBDID,") - SUCCEEDED!"
				return True
			elif (ret_eyescan == 1):
				print "INFO: [jtagutils.py] Eye Scan","- FAILED! (No links found)"
				print self.PVIVADO.before,self.PVIVADO.after
				return False
			elif (ret_eyescan == 2):
				print "INFO: [jtagutils.py] Eye Scan - EOF Found!!"
				return False
			elif (ret_eyescan == 3):
				print "INFO: [jtagutils.py] Eye Scan - Timeout!!"
				print self.PVIVADO.before,self.PVIVADO.after
				return False
			else:
				print "WARNING: [jtagutils.py] Unable to determine eye scan status and results"
				return False

		else:
			print "INFO: [jtagutils.py] Vivado process already losed. Do nothing."
			return False

	def close_jtag_target(self):None

	
	def close_all(self): #  Close hardware_server, vivado shell, pexpect subprocess
		
		if (psutil.pid_exists(pid_jtag_proc) == True):
			print "close_all: pid ", pid_jtag_proc, "is still alive..."
			self.PVIVADO.sendline('close_hardware_server')
			ret_close_hw = self.PVIVADO.expect(['DISCONNECT_HW_SERVER_OK',
							'DISCONNECT_HW_SERVER_FAIL',
							pexpect.EOF,
							pexpect.TIMEOUT])
			if (ret_close_hw == 0):
				print "self.PVIVADO.after:",self.PVIVADO.after
				print "INFO: [jtagutils.py] Disconnect hardware server - SUCCEEDED!"
				return True
			#if (ret_close_hw == 1):
			#	print "INFO: [jtagutils.py] vcse_server crashed. Need to kill vcse_server!"
			#	return True
			elif (ret_close_hw == 1):
				print "ERROR: [jtagutils.py] Disconnect hardware server - FAILED! Will fore close session."
				return False
			elif (ret_close_hw == 2):
				print "WARNNING: [jtagutils.py] EOF Found!"
				return False
			elif (ret_close_hw == 3):
				print "ERROR: [jtagutils.py] Time out!!"
				return False
			else:
				print "WARNING: [jtagutils.py] Unable to determine hardware status. Will force close session."
				return False

		else:
			print "INFO: [jtagutils.py] Vivado process already closed. Do nothing."
			return True

		#self.PVIVADO.interact()
        	#print self.PVIVADO.before,self.PVIVADO.after
	        self.PVIVADO.kill(1)				        
		print ('Vivado TCL Shell is alive? :', self.PVIVADO.isalive())


	#def list_jtag_targets(self):
	
	#	pVivado.sendline('list_jtag_targets')
	#	pVivado.expect('LIST_HW_OK')
	#	#pVivado.sendline('close_hardware_server')
	#	return True



#Poll process for new output until finished
#while pVivado.poll() is None:
#	line = pVivado.stdout.readline()
#	print line

#stdout_data =  pVivado.communicate(input='setup_hardware_server')[0]

#while pVivado.poll() is None:
#	line = pVivado.stdout.readline()
#	print "line:",line

#pVivado.stdout.close()
#print pVivado.stdout.read()
