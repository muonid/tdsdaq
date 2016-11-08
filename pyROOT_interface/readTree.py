from ROOT import *
f=TFile('tdsid.root')
f.tdstree.GetEntry(0)
print list(tdstree.localchipid)
