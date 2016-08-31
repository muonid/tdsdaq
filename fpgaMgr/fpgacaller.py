
import time
from jtagutils import JtagUtils
from eyeviewer import EyeViewer
ev = EyeViewer()


motherboardid = 'TDSV1-TBD-01'
tdsprogramid = 'TDS-TESTPROG-002'

#motherboardid = 'TDSV2-WIREBOND-TBD-01'
#tdsprogramid = 'TDS-TESTPROG-001'

# ***************** Program the first FPGA Board********************#


#== create vivado subprocess handler

jtagcontrol = JtagUtils(motherboardid,tdsprogramid,runmode="new")


#== connect to vivado hardware_server
for i in range (2):
	print i
	time.sleep(0.7)

isConnected_hw_server =jtagcontrol.setup_hardware_server()
if not isConnected_hw_server:
	exit()
else:
	print "isConnected_hw_server:",isConnected_hw_server


#== deploy bit stream
for i in range (3):
	print i
	time.sleep(1)

isDeployed_bitstream = jtagcontrol.deploy_bitstream()
if not isDeployed_bitstream:
	exit()
else:
	print "isDeployed_bitstream:",isDeployed_bitstream

#== do statistical eye diagram scan
#for i in range (3):
#	print i
#	time.sleep(1)

#isDone_eyescan = jtagcontrol.eye_scan()
#if not isDone_eyescan:
	exit()
#else:
#	print "isDone_eyescan:",isDone_eyescan

#== plot scanned eye diagram
#ev.draw_eyediagram("eye.csv")


#== disconnect hardware_server and close vivado
#for i in range (3):
#	print i
#	time.sleep(1)
#jtagcontrol.close_all()



# ***************** Program the second FPGA Board********************#
