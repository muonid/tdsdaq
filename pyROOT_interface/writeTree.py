from ROOT import *
import numpy as np

print "writing a tree"

#create Tfile
tds_file = TFile('tdsid.root','recreate')
tdstree = TTree('tdstree','tds test results')

#define tds result variables
localchipid=std.vector(std.string)()
#atlaschipid
routerframe_pass=np.zeros(1,dtype=bool)
globtest_pass=np.zeros(1,dtype=bool)

c='TDSv2-0001'

#define branch
tdstree.Branch('localchipid',localchipid)
tdstree.Branch('globtest_pass','globtest_pass','globtest_pass/B')
tdstree.Branch('rounterframe_pass','rounterframe_pass','rounterframe_pass/B')

for i in range (1):
	localchipid.reserve(20)
	localchipid.push_back(c)
	routerframe_pass=True
	globaltest_pass=True
	tdstree.Fill()

tds_file.Write()
tds_file.Close()
