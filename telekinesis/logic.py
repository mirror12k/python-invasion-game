
import re
import gamecore



class Timer(gamecore.Entity):
	def __init__(self, callbacks, timeSeconds=None, timeFrames=0, deleteOnTime=True, parent=None):
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


class DelayedSpawn(Timer):
	def __init__(self, entities, timeSeconds=None, timeFrames=0, parent=None):
		super(DelayedSpawn, self).__init__(callbacks=[self.spawn], timeSeconds=timeSeconds, timeFrames=timeFrames, deleteOnTime=True, parent=parent)
		self.entities = entities
	def spawn(self, timer):
		for ent in self.entities:
			self.parent.addEntity(ent)



class LayoutReader(object):
	def __init__(self, game, classMap, filename=None):
		# self.classMap = classMap
		self.game = game
		self.variables = { 'game': self.game }
		self.filename = filename

		for k, v in classMap.iteritems():
			self.variables[k] = v

	def evalExpressionArgs(self, expression):
		aargs, kwargs = [], {}
		match = re.match(r'\A(?:([a-zA-Z_][a-zA-Z_0-9]*)\s*=\s*|(\s*\)))', expression)
		while True:
			if match is None:
				expression, arg = self.evalExpression(expression)
				aargs.append(arg)
			elif match.group(1) is not None:
				expression = expression[len(match.group()):]
				# print "got kwarg:", match.group(1), expression
				expression, arg = self.evalExpression(expression)
				kwargs[match.group(1)] = arg
			else:
				expression = expression[len(match.group()):]
				return expression, aargs, kwargs

			match = re.match(r'\A(?:(\s*\))|(\s*,\s*))', expression)
			if match is None:
				raise Exception("invalid expression args:", expression)
			elif match.group(1) is not None:
				expression = expression[len(match.group()):]
				return expression, aargs, kwargs
			else:
				expression = expression[len(match.group()):]
			match = re.match(r'\A(?:([a-zA-Z_][a-zA-Z_0-9]*)\s*=\s*)', expression)

	def evalExpressionList(self, expression):
		results = []
		match = re.match(r'\A(?:(\s*(?:,\s*)?\]))', expression)
		while True:
			if match is None:
				expression, arg = self.evalExpression(expression)
				results.append(arg)
			else:
				expression = expression[len(match.group()):]
				return expression, results

			match = re.match(r'\A(?:(\s*(?:,\s*)?\])|(\s*,\s*))', expression)
			if match is None:
				raise Exception("invalid expression list:", expression)
			elif match.group(1) is not None:
				expression = expression[len(match.group()):]
				return expression, results
			else:
				expression = expression[len(match.group()):]
			match = None






	def evalExpression(self, expression):
		match = re.match(r'\A(?:(-?\d+\.\d+)|(-?\d+)|(".*")|([a-zA-Z_][a-zA-Z_0-9]*)|(\[))', expression)
		if match is None:
			raise Exception("invalid expression: " + expression)
		elif match.group(1) is not None:
			expression = expression[len(match.group()):]
			result = float(match.group(1))
			# print "got integer: ", result, expression
		elif match.group(2) is not None:
			expression = expression[len(match.group()):]
			result = int(match.group(2))
			# print "got integer: ", result, expression
		elif match.group(3) is not None:
			expression = expression[len(match.group()):]
			result = match.group(3)[1:-1]
		elif match.group(4) is not None:
			expression = expression[len(match.group()):]
			result = self.variables[match.group(4)]
			# print "got variable: ", result, expression
			expression, result = self.evalExpressionMore(expression, result)
		else:
			expression = expression[len(match.group()):]
			expression, result = self.evalExpressionList(expression)
		return expression, result
	def evalExpressionMore(self, expression, result):
		match = re.match(r'\A(?:(\s*=\s*)|\.([a-zA-Z_][a-zA-Z_0-9]*)|(\())', expression)
		if match is None:
			# print "got no more expression of:", expression
			return expression, result
		elif match.group(1) is not None:
			key = result
			expression = expression[len(match.group()):]
			expression, value = self.evalExpression(expression)
			self.variables[key] = value
			return expression, None
		elif match.group(2) is not None:
			key = match.group(2)
			# print "got attribute access:", result, key
			result = getattr(result, key)
			expression = expression[len(match.group()):]
			return self.evalExpressionMore(expression, result)
		else:
			# print "got variable call:", result
			expression = expression[len(match.group()):]
			expression, args, kwargs = self.evalExpressionArgs(expression)
			result = result(*args, **kwargs)
			return self.evalExpressionMore(expression, result)

	def evalStatement(self, expression):
		expression, value = self.evalExpression(expression)
		if expression != '':
			raise Exception("invalid expression tail: " + expression)


		
	def fromFile(self, filename=None):
		if filename is None:
			filename = self.filename
		else:
			self.filename = filename
		with open(filename, 'r') as f:
			lines = f.readlines()
			lines = map(lambda line: line.strip(), lines)
			lines = filter(lambda line: not line.startswith('#'), lines)
			lines = filter(lambda line: len(line) > 0, lines)

			processed_lines = []
			running_line = ''
			for line in lines:
				if line.endswith('\\'):
					running_line += line[:-1]
				else:
					processed_lines.append(running_line + line)
					running_line = ''
			if running_line != '':
				processed_lines.append(running_line)

			for line in processed_lines:
				self.evalStatement(line)
				# entityClass, args = line.split('(', 1)
				# args = args.rstrip(')')
				# args = args.split(',')

				# aargs = []
				# kwargs = {}
				# for arg in args:
				# 	if arg.find('=') == -1:
				# 		aargs.append(self.evalExpression(arg.strip()))
				# 	else:
				# 		key, val = arg.split('=', 1)
				# 		key = key.strip()
				# 		val = val.strip()
				# 		kwargs[key] = self.evalExpression(val)
				# # print "debug: "+ str(aargs)+ " : "+ str(kwargs)
				# classObject = self.classMap.get(entityClass)
				# if classObject is None:
				# 	die("cannot map class from name '"+entityClass+"' in layout file '"+filename+"'")
				# else:
				# 	entity = classObject(*aargs, **kwargs)
				# yield entity
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


