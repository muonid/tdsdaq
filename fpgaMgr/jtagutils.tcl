# !-vivado--#
# #!!!DO NOT MODIFY!!!##
# ===============================================================
# jtagutils.tcl
# 
# tcl commands to be executed in vivado for downloading
# bitstream and monitoring  
#
# August 2016
# Liang Guan
#
# Note:
# 1. only run ONE hadware_server to centrally manage FPGA jtag 
#    tranffic. No list_hw_server function provided here 
# 2. eval tcl expressions returns 1(TCL_ERROR) when errors occur
#    All functions below return -1 when error occurs.
#
#
# Quick run command
# vivado -mode tcl -source jtagutils.tcl
#
# Steps to download bitstream
# 1. open hardware server
# 2. open hardware target
# 3. deploy bit stream
# 4. take measurements
# 5. close hardware target
# 6. disconnect hardware server
# 7. close vivado tcl shell
# ================================================================

set hw_server_port 3121
set vcse_server_port 60001
#set jtag_freq 30000000
set jtag_freq 6000000

proc setup_hardware_server {} {

	global hw_server_port
	global vcse_server_port

	#open vivado hardware manager
	if { [ catch {open_hw} errorInfo ] } {
		puts "$errorInfo"
		return -1
	}

	#connect hardware server
	if { [ catch {connect_hw_server -host localhost -port $vcse_server_port -url localhost:$hw_server_port} errorInfo ] } {
		puts ": $errorInfo"
		puts "\[jtagutils.tcl\] CONNECT_HW_SERVER_FAIL"
		return -1
	}
	puts "CONNECT_HW_SERVER_OK"
	return 0
}

proc list_jtag_targets {} {
	set hw_list [get_hw_targets]
	puts "FOUND_JTAG_TARGETS: $hw_list"
	puts "LIST_JTAG_TARGET_OK"
	return 0
}

proc deploy_bitstream {jtag_descriptor bitfile probefile} {

	# check existance of provided bitfile and probe file
	# probefile=="NA" indicates no probe file needed 
	
	set bit_fexist [file exist $bitfile]
	if {$bit_fexist} {
		puts "INFO: \[jtagutils.tcl\] Found Bitstream file: $bitfile"
	} else {
		puts "ERROR: \[jtagutils.tcl\] Bitstream not found! Do nothing"
		return -1
	}

	set require_probefile [expr {$probefile ne "NA"}]
	if {$require_probefile} {

		set probe_fexist [file exist $probefile]
		if {$probe_fexist} {
		puts "INFO: \[jtagutils.tcl\] Found Probe file: $probefile"
		} else {
			puts "ERROR: \[jtagutils.tcl\] Probe file not found! Do nothing"
			return -1
		}
	}


	global jtag_freq
	# open hardware target 
	if { [ catch {current_hw_target [get_hw_targets $jtag_descriptor]} errorInfo ] } {
		puts "$errorInfo"
		return -1
	} else {
		set_property PARAM.FREQUENCY $jtag_freq [get_hw_targets $jtag_descriptor]
		set open_failed [ catch {open_hw_target} errorInfo ]
	}
	
	# 
	if {$open_failed} {
		puts "OPEN_HW_TARGET_FAIL"
		return -code error $errorInfo
	} else {
		# Only one device (FPGA) on each jtag chain. Just talk with the device with index 0
		set_property PROGRAM.FILE $bitfile [lindex [get_hw_devices] 0]
		if {$require_probefile == 1} {
			set_property PROBES.FILE $probefile [lindex [get_hw_devices] 0]
		}
		current_hw_device [lindex [get_hw_devices] 0]
		refresh_hw_device -update_hw_probes false [lindex [get_hw_devices] 0]
		set deploy_failed [ catch {program_hw_device [lindex [get_hw_devices] 0]} errorInfo ]
		if {$deploy_failed} {
			puts "DEPLOY_BITSTREAM_FAIL"
			return -code error $errorInfo
		} else {
			refresh_hw_device [lindex [get_hw_devices] 0]
			puts "DEPLOY_BITSTREAM_OK"
			return 0
		}
	}
}


proc eye_scan {} {
	set ber_target 1e-8
	set ber_pattern {PRBS 31-bit}
	set eye_result_file {eye.csv}
	set tx_link {localhost/xilinx_tcf/Digilent/210203A0237EA/0_1/IBERT/Quad_113/MGT_X1Y0/TX} 
	set rx_link {localhost/xilinx_tcf/Digilent/210203A0237EA/0_1/IBERT/Quad_113/MGT_X1Y0/RX}
	detect_hw_sio_links

	#set RPBS pattern and reset link
	set_property TX_PATTERN $ber_pattern [get_hw_sio_links $tx_link->$rx_link]
	commit_hw_sio [get_hw_sio_links $tx_link->$rx_link]
	set_property RX_PATTERN $ber_pattern [get_hw_sio_links $tx_link->$rx_link]
	commit_hw_sio [get_hw_sio_links $tx_link->$rx_link]
	set_property LOGIC.MGT_ERRCNT_RESET_CTRL 1 [get_hw_sio_links $tx_link->$rx_link]
	commit_hw_sio [get_hw_sio_links $tx_link->$rx_link]
	set_property LOGIC.MGT_ERRCNT_RESET_CTRL 0 [get_hw_sio_links $tx_link->$rx_link]
	commit_hw_sio [get_hw_sio_links $tx_link->$rx_link]

	set xil_newScan [create_hw_sio_scan -description {Scan_0} 2d_full_eye [lindex [get_hw_sio_links $tx_link->$rx_link] 0 ]]
	set_property HORIZONTAL_INCREMENT {8} [get_hw_sio_scans $xil_newScan]
	set_property VERTICAL_INCREMENT {16} [get_hw_sio_scans $xil_newScan]
	set_property DWELL_BER $ber_target [get_hw_sio_scans $xil_newScan]
	run_hw_sio_scan [get_hw_sio_scans $xil_newScan]
	# timeout in unit of minute
	wait_on_hw_sio_scan -timeout 10000 [get_hw_sio_scans $xil_newScan]
	write_hw_sio_scan -force $eye_result_file [get_hw_sio_scans $xil_newScan]
	#display_hw_sio_scan $xil_newScan
	puts "EYE_SCAN_DONE" 
	return 0
}


proc close_jtag_targets {jtag_descriptor} {

	set hw_target $jtag_descriptor  
	if { [ catch {close_hw_target $hw_target} errorInfo ] } {
		puts "$errorInfo"
		puts "CLOSE_JTAG_TARGET_FAIL"
		return -1
	} else {
		puts "CLOSE_JTAG_TARGET_OK"
		return 0
	}
}


proc close_hardware_server {} {
	# Execute this before closing vivado !!  
        if { [ catch {disconnect_hw_server} errorInfo ] } {
		puts "$errorInfo"
		puts "DISCONNECT_HW_SERVER_FAIL"
		return -1
	} else {
		puts "DISCONNECT_HW_SERVER_OK"
		return 0
	}
}

# end_of_jtagutils.tcl
