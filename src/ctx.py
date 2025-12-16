# -------- IMPORTATIONS --------

#exes
from obv.exe import *






# -------- CTX --------

#obv ctx
class obvCtx:
	def __init__(sbj):
		sbj.exes = [] #lst[obvExe]
		sbj.dats = [] #lst[tab[s8]], dat seg



	#parsing
	def unparse(sbj):
		res = ""

		#dat seg
		for de in sbj.dats:
			res += "dat" + OBV__SEP + hexOnN(len(de), 2) + OBV__SEP
			for b in de:
				res += hexOnN(b, 2)
			res += '\n'

		#exes
		for x in sbj.exes:
			res += x.unparse() + '\n'
		return res
