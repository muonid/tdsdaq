
from termcolor import bcolors
import numpy as np
from math import *
import calendar, datetime
from ROOT import TFile,TNtuple,TCanvas,TH2F,TGraph
from ROOT import gROOT,gRandom

bkgColor = bcolors

class PsViewer():

	def __init__(self,inData):

		gROOT.Reset()
		#Create a canvas to display something
		self.C1 = TCanvas("c1","c1",800,600) 
		self.C1.SetFillColor(10)
		self.C1.GetFrame().SetFillColor(21)
		self.C1.SetLeftMargin(0.15)
		self.C1.SetRightMargin(0.1)
		self.C1.SetTopMargin(0.12)
		self.C1.SetBottomMargin(0.15)
		self.C1.Draw()
		self.INDEX = 0
		self.NPTS = 600
		self.IDATA = np.zeros(self.NPTS, dtype = 'f')

	def draw_current(self,inData):
		self.IDATA = inData
		self.C1.cd()
		gr_iMoni = TGraph(self.NPTS)
		gr_iMoni.SetTitle("Power Supply PS001 Current Monitoring")
		gr_iMoni.Draw("ALP")
		gr_iMoni.SetMarkerStyle(20)
		gr_iMoni.SetMarkerSize(1)
		gr_iMoni.SetMarkerColor(2)

		utcnow = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
		utcnow -= 600  # time offset due to points updating from rightmost side  
		for self.INDEX in range (0,self.NPTS):
			time = self.INDEX
			if self.IDATA[self.INDEX] >= 0.0:
				gr_iMoni.SetPoint(self.INDEX, time, self.IDATA[self.INDEX])
			else:
				print bkgColor.FAIL + "[ERROR-xxx]: Negative Current Data!" + bkgColor.ENDC
				break

		gr_iMoni.GetXaxis().SetTitle("Time (EDT)")
		gr_iMoni.GetXaxis().SetTitleOffset(2.0)
		gr_iMoni.GetXaxis().SetLabelOffset(0.03)
		gr_iMoni.GetXaxis().SetTimeDisplay(1)
        	gr_iMoni.GetXaxis().SetTimeFormat("#splitline{%Y-%m-%d}{%H:%M:%S}")
        	gr_iMoni.GetXaxis().SetTimeOffset(utcnow,"local");
        	gr_iMoni.GetXaxis().SetNdivisions(503)
		gr_iMoni.GetYaxis().SetTitle("Current (A)")
		gr_iMoni.GetYaxis().SetTitleOffset(1.6)
		gr_iMoni.SetMinimum(0.3)
		gr_iMoni.SetMaximum(1.5)
		gr_iMoni.Draw("ALP")
		self.C1.Modified()
		self.C1.Update()
		return True

	def close_plot(self):
		# close canvas and release memory ...
		self.C1.Close()
		return True

