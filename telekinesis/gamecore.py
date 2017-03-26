

import sys, time
import pygame
from pygame import Surface
from pygame.rect import Rect
import random



def die(msg=''):
	print "ERROR:", msg
	print "sudden death occured..."
	sys.exit(1)





class Entity(object):
	''' the most basic unit of the engine, receives callbacks to update() and draw() '''
	def __init__(self, parent=None):
		self.parent = None
		self.zIndex = 0
		if parent is not None:
			parent.addEntity(self)
			# self.parent = parent
	def update(self):
		pass
	def draw(self, screen):
		pass
	def removeSelf(self):
		''' removes itself from the game engine '''
		self.parent.removeEntity(self)
	def __str__(self):
		return str(type(self))



class ContainerEntity(Entity):
	''' an entity which stores other entities and update()s and draw()s them '''
	def __init__(self, parent=None):
		super(ContainerEntity, self).__init__(parent)
		self.entities = []
		self.entitiesToAdd = []
		self.entitiesToRemove = []
	def addEntity(self, ent):
		self.entitiesToAdd.append(ent)
		if ent.parent is not None:
			ent.parent.removeEntity(ent)
		# ent.parent = self
	def removeEntity(self, ent):
		self.entitiesToRemove.append(ent)
	def updateContainer(self):
		if len(self.entitiesToRemove) > 0:
			for ent in self.entitiesToRemove:
				ent.parent = None
			self.entities = [ ent for ent in self.entities if ent not in self.entitiesToRemove ]
			# for ent in self.entitiesToRemove:
			# 	ent.parent = None
			self.entitiesToRemove = []
		if len(self.entitiesToAdd) > 0:
			for ent in self.entitiesToAdd:
				ent.parent = self
			self.entities += self.entitiesToAdd
			# for ent in self.entitiesToAdd:
			# 	ent.parent = self
			self.entitiesToAdd = []
	def getGame(self):
		if self.parent is not None:
			return self.parent.getGame()
	def sortEntities(self):
		self.entities = sorted(self.entities, key=lambda ent: ent.zIndex)
	def update(self):
		self.updateContainer()
		for entity in self.entities:
			entity.update()
		self.updateContainer()
	def draw(self, screen):
		for entity in self.entities:
			entity.draw(screen)



# class EventHandler(object):
# 	def processEvents(self, game):
# 		pass
# 	def handleEvent(self, game):
# 		pass

# class DefaultEventHandler(EventHandler):
# 	def handleEvents(self, game):


class GameContainer(ContainerEntity):
	''' the main game container which contains the entire game in it '''
	def __init__(self, sizeX=640, sizeY=400, fps=60):
		super(GameContainer, self).__init__()
		self.sizeX = sizeX
		self.sizeY = sizeY
		self.fps = fps
		self.showFPS = False
		self.keystate = {}
		for key in [
				pygame.K_1,
				pygame.K_2,
				pygame.K_3,
				pygame.K_q,
				pygame.K_w,
				pygame.K_e,
				pygame.K_a,
				pygame.K_s,
				pygame.K_d,
				pygame.K_z,
				pygame.K_x,
				pygame.K_c,
				pygame.K_TAB,
				pygame.K_LSHIFT,
				pygame.K_RETURN,
				pygame.K_SPACE,
			]:
			self.keystate[key] = False
	def getGame(self):
		return self
	# def loadEventHandler(self, handler):
	# 	self.eventHandler = 
	def eventEnd(self):
		pass
	def run(self):		
		total_start = time.time()
		frames = 0
		frame_time = 1.0 / self.fps
		pygame.init()

		self.font = pygame.font.SysFont("monospace", 15)


		size = self.sizeX, self.sizeY

		screen = pygame.display.set_mode(size)

		self.running = True
		while self.running:
			time_start = time.time()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
				elif event.type == pygame.KEYDOWN:
					self.keystate[event.key] = True
					if event.key == pygame.K_ESCAPE:
						self.running = False
				elif event.type == pygame.KEYUP:
					self.keystate[event.key] = False

			self.update()

			self.draw(screen)
			pygame.display.flip()

			time_diff = time.time() - time_start
			# print time_diff
			if time_diff < frame_time:
				time.sleep(frame_time - time_diff)

			if self.showFPS:
				frames += 1
				if frames % self.fps == 0:
					print "fps:", int(frames / (time.time() - total_start))
		self.eventEnd()


