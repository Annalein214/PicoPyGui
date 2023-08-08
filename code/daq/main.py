from PyQt5.QtCore import QThread

from code.picoscope.device import deviceShelf

class daq(QThread):

	def __init__(self, log, opts, settings):
		'''
		initialise and prepare data taking
		- search for available picoscopes
		'''
		QThread.__init__(self)

		self.log=log
		self.opts=opts

		# search picoscope devices and let the user decide which one to use
		# might return a dummy device: bool(self.scope.dummy)
		ds=deviceShelf(log,self.opts.test)
		self.scope=ds.select_and_start_device()


		# --- initialise variables --------------------------------------
		self.progress=0 # otherwise bug sometimes when early access to this variable
		# --- settings -----
		# (stuff which is remembered after re-launch)
		# channel settings
		self.voltagerange=settings.attr["voltagerange"]
		self.coupling=settings.attr["coupling"] # dc or ac
		self.offset=settings.attr["offset"] # voltage for offset of channel
		self.channelEnabled=settings.attr["channelEnabled"]
		# trigger settings
		self.triggerchannel=settings.attr["triggerchannel"]
		self.triggermode=settings.attr["triggermode"]
		self.triggervoltage=settings.attr["triggervoltage"]
		self.triggerdelay=settings.attr["triggerdelay"]
		self.triggertimeout=settings.attr["triggertimeout"]
		# block settings
		self.samplefreq=settings.attr["samplefreq"]
		self.captures=settings.attr["captures"]
		self.nosamples=settings.attr["nosamples"]

