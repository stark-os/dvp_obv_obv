# -------- IMPORTATIONS --------

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< pffffffffffffffffff...
from zctx import *

#obv
from obv.exe import *






# -------- SEMANTIC --------

#value kinds
OBV_VAL__LIT    = 0
OBV_VAL__DATITM = 1
OBV_VAL__REG    = 2
OBV_VAL__PTR    = 3






# -------- Z VAL TO OBV VAL --------

#obv val
class obvVal:
	def __init__(sbj, kind, sz, txt):
		sbj.kind = kind #enm OBV_VAL
		sbj.sz   = sz   #s8, in bits! (not in bytes)
		sbj.txt  = txt  #str
