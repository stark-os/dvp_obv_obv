# -------- SEGS --------

#segs
class seg:
	def __init__(sbj, name, firstGblAdr, sz):

		#gnc
		sbj.name = name
		sbj.sz   = sz

		#gbl adr
		sbj.firstGblAdr = firstGblAdr
		sbj.lastGblAdr  = firstGblAdr + sz - 1

		#lcl adr
		sbj.lclAdr     = 0
		sbj.lastLclAdr = sz-1

		#dat
		sbj.dat = [0] * sz
