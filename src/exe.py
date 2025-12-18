# -------- IMPORTATIONS --------

#std
import string
from std.int    import *
from std.string import *






# -------- SEMANTIC --------

#syntax
OBV__SEP            = '\t'
OBV__DATITM_CHARSET = string.ascii_letters + string.digits + '_'

#begBlanks for obvExe in fct scope
OBV__BEGBLANKS_FCT = 2* OBV__SEP

#regs
OBV__PARAMS = ("p1", "p2", "p3", "p4", "p5", "p6")
OBV__REGS   = OBV__PARAMS + ("r",)

#cvt
CVT_PATTERNS = (
	"f32_f64",  "f32_smax", #from f32
	"f64_f32",  "f64_smax", #from f64
	"smax_f32", "smax_f64"  #from smax
)

#tmp <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
TERM__OUTPUT_TAB = '\t'






# -------- PARSING --------

#obv
class obvExe:
	def __init__(sbj, ist, sz, args, begBlanks):
		sbj.ist       = ist  #str
		sbj.sz        = sz   #s8
		sbj.args      = args #lst[str]
		sbj.begBlanks = begBlanks #str

	def toStr(sbj, depth=0):
		d    = TERM__OUTPUT_TAB * depth
		res  = "\n" + d + "_:\"obvExe\"\n"
		res += d + "ist:\"" + sbj.ist + "\"\n"
		res += d + "sz:" + str(sbj.sz) + '\n'
		res += d + "args:["
		for a in sbj.args:
			res += '"' + a + "\","
		res += ']'
		return res

	def unparse(sbj):
		res = sbj.begBlanks + sbj.ist + OBV__SEP + hexOnN(sbj.sz, 4)
		for a in sbj.args:
			res += OBV__SEP + a
		return res



#err
def err(line, msg):
	print("At line \"" + line + '\"')
	print("ERROR: " + msg)
	exit(1)

#wrn
def wrn(line, msg):
	print("At line \"" + line + '\"')
	print("WARNING: " + msg)
	print("[Press ENTER to continue]")
	input()



#extract OBV ist & args from line
def obvParse(rawLine):
	commentIdx = str_findFirstChr(rawLine, '#')
	if commentIdx == 0:
		return None #empty line => no exe
	if commentIdx != -1:
		rawLine = str_sub(rawLine, stop=commentIdx-1)

	#strip
	line        = str_stripBeg(rawLine)
	begBlankLen = len(rawLine) - len(line)
	line        = str_stripEnd(line)
	lineWrds    = line.split(OBV__SEP)

	#empty line => no exe
	if len(line) == 0:
		return None

	#beg blank
	begBlank = rawLine[:begBlankLen]

	#ist
	ist = lineWrds[0]
	if len(ist) != 3:
		err(line, "Got more than 3 characters for instruction \"" + ist + "\".")

	#sz
	sz = str_hex_toS16(lineWrds[1])

	#args
	lineWrds = lineWrds[2:]
	args     = [] #lst[str]
	for w in lineWrds:
		if len(w) == 0: #several sep chr following each other => skip them
			continue
		args.append(w)

	#parse
	ox = obvExe(ist, sz, args, begBlank)
	obvExe_checkIntegrity(ox)
	return ox

def obvExe_isCpy(ist, includeFromV=True):
	res = ist in ("d2d","d2r", "r2d","r2r")
	if includeFromV and not res:
		return ist in ("v2d","v2r")
	return res



#check args: nbr
def mustHaveNArgs(ox, argsNbr):
	if len(ox.args) != argsNbr:
		err(ox.unparse().strip(), "Instruction \"" + ox.ist + "\" must have exactly " + str(argsNbr) + " args, got " + str(len(ox.args)) + ".")



#check args: reg
def argMustBeReg(ox, argIdx):
	arg = ox.args[argIdx]

	#must be a reg
	if arg not in OBV__REGS:
		err(ox.unparse, "Instruction \"" + ox.ist + "\", arg " + str(argIdx+1) + " must be a register name (\"" + arg + "\" given).")



#check args: val
def argMustBeVal(ox, argIdx):
	arg = ox.args[argIdx]

	#check val len
	if len(arg) == 0:
		err(ox.unparse(), "Instruction \"" + ox.ist + "\", arg " + str(argIdx+1) + " has empty value given (only \"" + arg + "\" given).")
	argObvSz = len(arg) << 2

	''' <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< NO PROBLEM WITH THIS, BUT MAYBE WE SHOULD FORBID ANY CASTING AT OBV LVL
	#lit upcasting: OK, complete with 0
	if argObvSz < ox.sz:
		prevLine = ox.unparse()
		ox.args[argIdx] = '0' * ((ox.sz-argObvSz) >> 2) + arg
		wrn(prevLine, "Upcasting literal \"" + arg + "\" into \"" + ox.args[argIdx] + "\".")
	'''

	''' <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TO RESTORE
	#lit downcasting: KO, no way we loose lit dat
	elif argObvSz > ox.sz:
		err(ox.unparse(), "Instruction \"" + ox.ist + "\", arg " + str(argIdx+1) + " is a bigger literal than operation => downcasting, literal data loss, forbidden! (ist mentions a " + str(ox.sz) + "b operation, arg is on " + str(argObvSz) + "b).")
	'''

	#check val charset
	if len(arg) & 1:
		err(ox.unparse(), "Instruction \"" + ox.ist + "\", arg " + str(argIdx+1) + " must have an even number of characters (" + str(len(args)) + " given).")
	for c in arg:
		if c not in HEX_DIGITS_LOWERCASE:
			err(ox.unparse(), "Instruction \"" + ox.ist + "\", arg " + str(argIdx+1) + " must have only hexadecimal characters ('" + c + "' given).")



#check args: datItm
def checkNameInArg(ox, argIdx, name):

	#check name len & charset
	if len(name) == 0:
		err(ox.unparse(), "Instruction \"" + ox.ist + "\", arg " + str(argIdx+1) + " has empty name (only \"" + ox.args[argIdx] + "\" given).")
	for c in name:
		if c not in OBV__DATITM_CHARSET:
			err(ox.unparse(), "Instruction \"" + ox.ist + "\", arg " + str(argIdx+1) + " has invalid character in name ('" + c + "' given).")

def check4HexInArg(ox, argIdx, h4):

	#check 4-hex seq
	if len(h4) != 4:
		err(ox.unparse(), "Instruction \"" + ox.ist + "\", arg " + str(argIdx+1) + " must have a 4 hexadecimal digit sequence (\"" + h4 + "\" given).")
	for c in h4:
		if c not in HEX_DIGITS_LOWERCASE:
			err(ox.unparse(), "Instruction \"" + ox.ist + "\", arg " + str(argIdx+1) + " must have only hexadecimal characters in sequence \"" + h4 + "\" ('" + c + "' given).")


def argMustBeDatItm(ox, argIdx, withOffset=True):
	arg = ox.args[argIdx]

	#check '+' existence
	if '+' not in arg:
		err(ox.unparse(), "Instruction \"" + ox.ist + "\", arg " + str(argIdx+1) + " has no '+' symbol in it (required as a data item).")

	#split by it & then check name & offset separately
	name, offset = arg.split('+')
	checkNameInArg(ox, argIdx, name)
	check4HexInArg(ox, argIdx, offset)



#check args: main
def obvExe_checkIntegrity(ox):

	#MEM

	#dat
	if ox.ist == "dat":
		mustHaveNArgs(ox, 1)
		argMustBeVal(ox, 0)

	#rsv
	elif ox.ist == "rsv":
		mustHaveNArgs(ox, 2)
		checkNameInArg(ox, 0, ox.args[0])
		check4HexInArg(ox, 1, ox.args[1])



	#CPY FROM VAL INTO ...

	#cpy val 2 reg
	elif ox.ist == "v2r":
		mustHaveNArgs(ox, 2)
		argMustBeVal(ox, 0)
		argMustBeReg(ox, 1)

	#cpy val 2 dat
	elif ox.ist == "v2d":
		mustHaveNArgs(ox, 2)
		argMustBeVal(ox, 0)
		argMustBeDatItm(ox, 1)

	#cpy val 2 at-adr
	elif ox.ist == "v2a":
		mustHaveNArgs(ox, 2)
		argMustBeVal(ox, 0)
		argMustBeDatItm(ox, 1)




	#CPY FROM REG INTO ...

	#cpy reg 2 reg
	elif ox.ist == "r2r":
		mustHaveNArgs(ox, 2)
		argMustBeReg(ox, 0)
		argMustBeReg(ox, 1)

	#cpy reg 2 dat
	elif ox.ist == "r2d":
		mustHaveNArgs(ox, 2)
		argMustBeReg(ox, 0)
		argMustBeDatItm(ox, 1)

	#cpy reg 2 at-adr
	elif ox.ist == "r2a":
		mustHaveNArgs(ox, 2)
		argMustBeReg(ox, 0)
		argMustBeDatItm(ox, 1)



	#CPY FROM DAT INTO ...

	#cpy dat 2 reg
	elif ox.ist == "d2r":
		mustHaveNArgs(ox, 2)
		argMustBeDatItm(ox, 0)
		argMustBeReg(ox, 1)

	#cpy dat 2 dat
	elif ox.ist == "d2d":
		mustHaveNArgs(ox, 2)
		argMustBeDatItm(ox, 0)
		argMustBeDatItm(ox, 1)

	#cpy dat 2 at-adr
	elif ox.ist == "d2a":
		mustHaveNArgs(ox, 2)
		argMustBeDatItm(ox, 0)
		argMustBeDatItm(ox, 1)



	#CPY FROM AT-ADR INTO ...

	#cpy at-adr 2 reg
	elif ox.ist == "a2r":
		mustHaveNArgs(ox, 2)
		argMustBeDatItm(ox, 0)
		argMustBeReg(ox, 1)

	#cpy at-adr 2 dat
	elif ox.ist == "a2d":
		mustHaveNArgs(ox, 2)
		argMustBeDatItm(ox, 0)
		argMustBeDatItm(ox, 1)

	#cpy at-adr 2 at-adr
	elif ox.ist == "a2a":
		mustHaveNArgs(ox, 2)
		argMustBeDatItm(ox, 0)
		argMustBeDatItm(ox, 1)



	#CPY FROM PTR INTO ...

	#cpy ptr 2 reg
	elif ox.ist == "p2r":
		mustHaveNArgs(ox, 2)
		argMustBeDatItm(ox, 0)
		argMustBeReg(ox, 1)

	#cpy ptr 2 dat
	elif ox.ist == "p2d":
		mustHaveNArgs(ox, 2)
		argMustBeDatItm(ox, 0)
		argMustBeDatItm(ox, 1)

	#cpy ptr 2 at-adr
	elif ox.ist == "p2a":
		mustHaveNArgs(ox, 2)
		argMustBeDatItm(ox, 0)
		argMustBeDatItm(ox, 1)



	#DECISIONAL

	#dor
	elif ox.ist == "dor":
		pass

	#dan
	elif ox.ist == "dan":
		pass



	#ATH

	#bad
	elif ox.ist == "bad":
		pass

	#bsu
	elif ox.ist == "bsu":
		pass

	#amu
	elif ox.ist == "amu":
		pass

	#adi
	elif ox.ist == "adi":
		pass

	#amo
	elif ox.ist == "amo":
		pass

	#cvt
	elif ox.ist == "cvt":
		mustHaveNArgs(ox, 2)
		checkNameInArg(ox, 0, ox.args[0])
		if ox.args[0] not in CVT_PATTERNS:
			err(ox.unparse(), "Unknown conversion pattern \"" + ox.args[0] + "\".")
		argMustBeDatItm(ox, 1)



	#LOGIC

	#sin
	elif ox.ist == "sin":
		pass

	#lor
	elif ox.ist == "lor":
		pass

	#lan
	elif ox.ist == "lan":
		pass

	#lxo
	elif ox.ist == "lxo":
		pass

	#lls
	elif ox.ist == "lls":
		pass

	#lrs
	elif ox.ist == "lrs":
		pass



	#CMP

	#sno
	elif ox.ist == "sno":
		pass

	#ceq
	elif ox.ist == "ceq":
		pass

	#cne
	elif ox.ist == "cne":
		pass

	#clt
	elif ox.ist == "clt":
		pass

	#cgt
	elif ox.ist == "cgt":
		pass

	#cle
	elif ox.ist == "cle":
		pass

	#cge
	elif ox.ist == "cge":
		pass

	#cmp
	elif ox.ist == "CMP":
		pass

	#TMP <<<<<<<<<<<<<<<<<<<<<
	elif ox.ist == "BRK":
		pass
	elif ox.ist == "CTN":
		pass



	#FCT RELATED

	#bck
	elif ox.ist == "bck":
		mustHaveNArgs(ox, 0)

	#ivq
	elif ox.ist == "ivq":
		mustHaveNArgs(ox, 1)
		checkNameInArg(ox, 0, ox.args[0])

	#fct
	elif ox.ist == "fct":
		mustHaveNArgs(ox, 1)
		checkNameInArg(ox, 0, ox.args[0])



	#SYSTEM

	#syc
	elif ox.ist == "syc":
		mustHaveNArgs(ox, 0)

	#unknown
	else:
		print("ERROR: Unknown instruction \"" + ox.ist + "\".")
		exit(1)
