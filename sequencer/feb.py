"""
rewritten version of FEBgpib

sets/gets sensor parameters
"""

import pyvisa as visa

gpib='GPIB0::18::INSTR' #maybe move gpib address to separate config file

header="c4d"
footer="00zx"
readCommand="c2x"

rm=visa.ResourceManager()
inst=rm.open_resource(gpib)

class SETTINGS:
	SENSORBIAS  = 1
	SQUIDBIAS   = 2
	SQUIDLOCK   = 3
	SQUIDGAIN   = 4
	SQUIDDRIVER = 5
	
class CHANNEL:
	A = 10
	B = 11
	C = 12
	D = 13
	
def fourdigit(string): #helper function to ensure data is formatted properly. Makes numbers four digits long if they are too short by padding with zeros. (Unsure if this is the proper format)
	while len(string) < 4:
		string = "0" + string
	return string

def write(subrack, address, data):
	subrackWithAddressBit = subrack | 8 #why do we need to do this?
	addressString = header + fourdigit(format(address, "x")) + "0" + format(subRackWithAddressBit, "x") + footer
	dataString = header + format(data, "x") + "0" + format(subrack, "x") + footer
	
	inst.write(addressString)
	inst.write(dataString)


def read(subrack, address):
	subrackWithAddressBit = subRack | 8
	addressString = header + fourdigit(format(address, "x")) + "0" + format(subrackWithAddressBit, "x") + footer
	
	inst.write(addressString)
	inst.write(readCommand)
	data=inst.read()
	return data[:4]

sensorDict = {
	SETTINGS.SENSORBIAS: [4096.0, 2000.0, 4000],
	SETTINGS.SQUIDBIAS: [4095.0,200.0,400.0],
	SETTINGS.SQUIDLOCK: [4095.0, 8.0, 16.0],
	SETTINGS.SQUIDGAIN: [409.5, 5.0, 200.0],
	SETTINGS.SQUIDDRIVER: [4095.0, 5.0, 10.0]
}

def setSensorSquid(subrack, slot, setting, channel, value)
	address= (slot<<8) + (setting << 4) + channel
	a,b,c=sensorDict[setting]
	data=int(round(a*(b+value)/c))
	write(subrack, address, data)
	
def getSensorSquid(subrack, slot, setting, channel)
	address= (slot<<8) + (setting << 4) + channel
	a,b,c=sensorDict[setting]
	
	dataHexStr=read(subrack, address)
	dataDec=int(dataHexStr, 16) & 4095
	
	value=c*float(dataDec)/a-b
	return value


