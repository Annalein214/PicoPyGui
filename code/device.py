from picoscope3000 import picoscope as p3000
from picoscope6000 import picoscope as p6000 # ADDPICO in order to add another type of picoscope, add the library here
import traceback
from helpers import *


drivers = [p3000, p6000] # ADDPICO in order to add another type of picoscope, add the library here

def find_units():
	# Search for, open and return all devices for supported picoscope drivers
	devices = []
	for driver in drivers:
		try: 
			device = driver()
			device.open()
			devices.append(device)
		except:
			continue
	if not devices: 
		raise RuntimeError(red+"Could not find any devices on any drivers."+nc)
	return devices

def getDeviceName(device):
	# get the device type from the device info, see other available info in this example
	'''
	DriverVersion                 : PS3000A MacOSX Driver, 2.1.105.3345
	USBVersion                    : 3.0
	HardwareVersion               : 1
	VariantInfo                   : 3406DMSO
	BatchAndSerial                : JY908/0114
	CalDate                       : 07Sep22
	KernelVersion                 : 0.0
	DigitalHardwareVersion        : 1
	AnalogueHardwareVersion       : 1
	PicoFirmwareVersion1          : 1.7.5.0
	PicoFirmwareVersion2          : 1.0.67.0
	'''
	info=device.getAllUnitInfo()
	vinfo=info
	details=info.split("\n")
	for detail in details:
		if "VariantInfo" in detail:
			vinfo=detail.split(":")[-1].replace(" " ,"")
		if "BatchAndSerial" in detail:
			serial=detail.split(":")[-1].replace(" " ,"")
	return vinfo+" "+serial

def select_unit(devices):
	# give the choice on command line to select one of the devices found by find_units
	# if there is only one unit, automatically choose this unit
	if len(devices)==0:
		raise RuntimeError(red+"Could not find any devices on any drivers."+nc)
	#elif len(devices)==1:
	#	print("Only one device found. Automatically choose this device:")
	#	chosen_device=devices[0]
	#	vinfo=getDeviceName(chosen_device)
	else:
		print(green+"Please select a device: The following devices are available (type, batch, serial)."+nc)
		i=1
		for device in devices:
			vinfo=getDeviceName(device)
			print("%02d: "%i,vinfo)
		text=input(green+"Please enter the number of the device which should be initialized: "+nc)
		try:
			nbr=int(text)
			if nbr < len(devices)+1:
				chosen_device=devices[nbr-1]
			else:
				raise RuntimeError("Number not listed.")
		except:
			for device in devices:
				device.close()
			traceback.print_exc()
			raise RuntimeError("Invalid number")
		# close other devices
		i=1
		for device in devices:
			if i!=nbr:
				print("Close",i)
				device.close()
	print(yellow+"The chosen device is called (type, batch, serial): %s"%vinfo,nc)
	return chosen_device

def select_and_start_device():
	devices=find_units()
	device=select_unit(devices)
	return device


if __name__ == "__main__":
	device=select_and_start_device()
	device.close()
