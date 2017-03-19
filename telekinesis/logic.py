
import gamecore



class Timer(gamecore.Entity):
	def __init__(self, timeFrames=0, timeSeconds=None, callbacks=[], deleteOnTime=True, parent=None):
		super(Timer, self).__init__(parent)
		if timeSeconds is not None:
			self.timeFrames = int(parent.getGame().fps * timeSeconds)
		else:
			self.timeFrames = timeFrames
		self.timer = self.timeFrames
		self.callbacks = callbacks
		self.deleteOnTime = deleteOnTime
	def update(self):
		if self.timer > 0:
			self.timer -= 1
		else:
			for cb in self.callbacks:
				cb(self)
			if self.deleteOnTime:
				self.removeSelf()
			else:
				self.timer = self.timeFrames



class LayoutReader(object):
	def __init__(self, classMap, filename=None):
		self.classMap = classMap
		self.filename = filename
	def evalExpression(self, expression):
		if expression[0] == '"' or expression[0] == "'":
			expression = expression[1:-1]
		else:
			expression = int(expression)
		return expression
	def fromFile(self, filename=None):
		if filename is None:
			filename = self.filename
		else:
			self.filename = filename
		with open(filename, 'r') as f:
			for line in f:
				line = line.strip()
				if not line.startswith('#') and line.find('(') != -1:
					entityClass, args = line.split('(', 1)
					args = args.rstrip(')')
					args = args.split(',')

					aargs = []
					kwargs = {}
					for arg in args:
						if arg.find('=') == -1:
							aargs.append(self.evalExpression(arg.strip()))
						else:
							key, val = arg.split('=', 1)
							key = key.strip()
							val = val.strip()
							kwargs[key] = self.evalExpression(val)
					# print "debug: "+ str(aargs)+ " : "+ str(kwargs)
					classObject = self.classMap.get(entityClass)
					if classObject is None:
						die("cannot map class from name '"+entityClass+"' in layout file '"+filename+"'")
					else:
						entity = classObject(*aargs, **kwargs)
					yield entity
	def toFile(self, entities, filename=None):
		if filename is None:
			filename = self.filename
		else:
			self.filename = filename
		with open(filename, 'w') as f:
			for ent in entities:
				layoutargs = ent.toLayout()
				for key in layoutargs.keys():
					if type(layoutargs[key]) is str:
						layoutargs[key] = '"' + layoutargs[key] + '"'
					elif type(layoutargs[key]) is int:
						layoutargs[key] = str(layoutargs[key])
					else:
						die('unknown type: '+str(type(layoutargs[key])))
				f.write(type(ent).__name__+ '(' + ', '.join([ key+'='+str(layoutargs[key]) for key in layoutargs.keys() ])+")\n")


