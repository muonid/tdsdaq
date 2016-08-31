#!/usr/bin/env python

import time
import collections
import numpy as np
from pscontrol import PsControl
from psviewer import PsViewer


# initialization

#-- deque for current monitor
nFRAME=1200
nPTS=600
in_queue = collections.deque(maxlen=nPTS)
for i in range (0,nPTS):
	in_queue.append(0.0)

#-- array for plotting current
idata = np.zeros(nPTS,dtype='f')

#-- classes for ps control and plotting
ps_caller = PsControl("ASRL/dev/ttyS0::INSTR")
ps_plot = PsViewer(idata)


# Example PS control code starts here
print "dummy caller to check the power supply"
ps_caller.setup_ps()

print "turnning on power in 3 seconds"
for i in range (0,3):
	print 3-i 
	time.sleep(1)
ps_caller.power_on()

for i in range (0,nFRAME):
	in_queue.append(ps_caller.read_current()) 
	idata = np.array(in_queue)
	print idata
	ps_plot.draw_current(idata)
	time.sleep (0.5)

print "turnning off power in 3 seconds"
for i in range (0,3):
        print 3-i
        time.sleep(1)
ps_caller.power_off()



