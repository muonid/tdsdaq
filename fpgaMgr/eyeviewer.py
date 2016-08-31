#!/usr/bin/env python

import ROOT
from termcolor import bcolors
import os
import numpy as np
from rootpy.extern.six.moves import range
from rootpy.plotting import Hist, Hist2D, Hist3D, HistStack, Legend, Canvas
from rootpy.interactive import wait
import random

bkgColor = bcolors

class EyeViewer():

        def __init__(self):

		#define 2D histogram
		self.eyehist = Hist2D(9, -0.5, 0.5, 15, 0.0 , 1.0, name='eyehist', title='EyeDiagram',
                		drawstyle='colz',
                		legendstyle='F',
                		fillstyle='/')


	def dummy(self):
		print "Nothing"
		return True

	def draw_eyediagram(self,csvfile):

		# read eye scan data from csv file
		eye_2d_array =[]
		if (not os.path.isfile(csvfile) ):
			print "ERROR: [EYE-SCAN] Eye Scan data not available!!"
		else:
			print "INFO: [EYE-SCAN] Eye scan data found."	
			with open(csvfile) as dfile:
				for line in dfile:
					eye_2d_array.append(line.strip().split(','))

			#with open ('eye.csv','rb') as csvfile:
			#	dummyreader=csv.reader(csvfile,delimiter=',',quotechar='|')
			#	for row in dummyreader:
			#		print row


		# fill the histogram
		for i in range (15):
			for j in range (9):
				x=(j-9)*0.1111111+0.5
				y=(14-i)*0.0666666667
				ber=float(eye_2d_array[i+18][j+1])
				self.eyehist.Fill(x,y,float(eye_2d_array[i+18][j+1]))
				print ber

		# set visual attributes
		self.eyehist.linecolor = 'blue'
		self.eyehist.fillcolor = 'green'
		self.eyehist.fillstyle = '/'

		# display eye diagram attributes
		print(self.eyehist.name)
		print(self.eyehist.title)
		print(self.eyehist.markersize)

		# make plot
		ROOT.gStyle.SetOptStat(0)
		canvas = Canvas(width=700, height=500)
		canvas.SetLeftMargin(0.15)
		canvas.SetBottomMargin(0.15)
		canvas.SetTopMargin(0.10)
		canvas.SetRightMargin(0.15)
		canvas.SetLogz()
		self.eyehist.GetXaxis().SetTitle("Unit Interval")
		self.eyehist.GetYaxis().SetTitle("Amplitude")
		self.eyehist.GetZaxis().SetRangeUser(1e-9,1e-2)
		self.eyehist.Draw()

		# create the legend
		legend = Legend([self.eyehist], pad=canvas,
               			 header='4.8 Gbps',
               			 leftmargin=0.05,
                		 rightmargin=0.5)
		legend.Draw()


		# wait for actions to close canvases before exiting
		# no effect if ROOT is in batch mode:
		# ROOT.gROOT.SetBatch(True)
		wait()

		return True
