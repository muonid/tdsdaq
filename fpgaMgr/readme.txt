need to copy the following files to tdstester folder

- jtagutils.tcl  # tcl script to be executed in vivado tcl shell
- jtagutils.py  # python wrapper for jtagutils.tcl
- fpgacall.py   # example code to invoke functions in jtagutils.py (to be implemented)
- termcolor.py # color scheme to visualize error, warning message
- eyeviewer.py #utilize ROOT and rootpy to plot 2d eye scan result for a serial link.
- boardmap.py # test board map file. contains a dict for looking up associated jtag id etc
- bitmap.py # stores bitstream location info for each test program
