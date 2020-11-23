# Class that adds opendrive signal elements
# <Signals> class is a container for <signal>. <signals> is a subelement of the <road> element. 
# Current subelements include:
# <validity> to restrict validity to specific lanes

import xml.etree.ElementTree as ET

class Signals:
	def __init__(self):
		self.signals = []

	def get_element(self):
		element = ET.Element('signals')
		for signal in self.signals:
			element.append(signal.get_element())
		return element



class Signal:
	def __init__(self, s, t, dynamic="no", orientation="+"):
		self.s = s
		self.t = t
		self.dynamic=dynamic
		self.orientation=orientation

	#def __init__(self, s, t, id, name, dynamic, valDirection, heightOffset, height, hOffset, pitch, roll):
		#self.s = s  #s co-ordinate of the signal
		#self.t = t  #t co-oordinate of the signal
		#self.id = id #Signal id 
		#self.name = name #Name of the signal
		#self.dynamic = dynamic 
		#self.orientation = valDirection
		#self.zOffset = heightOffset
		#self.height = height
		#self.

	def get_attributes(self):
		retdict = {}
		retdict["s"] = str(self.s)
		retdict["t"] = str(self.t)
		retdict["dynamic"] = self.dynamic
		retdict["orientation"] = self.orientation
		return retdict

	def get_element(self):
		element = ET.Element('signal',attrib=self.get_attributes())
		return element



