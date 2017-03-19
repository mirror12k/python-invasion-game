
import pygame
from gamecore import *





class ScreenEntity(Entity):
	''' a generic entity for displaying stuff on the screen '''
	def __init__(self, x=0, y=0, parent=None, filepath=None):
		super(ScreenEntity, self).__init__(parent)
		self.rect = Rect(x,y,0,0)
		if filepath is not None:
			self.loadImage(filepath)
	def loadImage(self, filename):
		self.setImage(pygame.image.load(filename))
	def setImage(self, img):
		self.img = img
		self.rect.w = self.img.get_rect().w
		self.rect.h = self.img.get_rect().h
		# print self.rect
	def setSpriteSheet(self, tilesheet):
		self.img = tilesheet
		self.rect.w = tilesheet.tileSizeX
		self.rect.h = tilesheet.tileSizeY
	def selectSubSprite(self, tile):
		self.img = self.img.tile(tile)
	def drawSubSprite(self, screen, tile):
		screen.blit(self.img.tile(tile), self.rect)
	def draw(self, screen):
		screen.blit(self.img, self.rect)
	def move(self, x=0, y=0):
		self.rect.x += x
		self.rect.y += y
	def toLayout(self):
		return { 'x' : self.rect.x, 'y' : self.rect.y }



class TileSheet(object):
	''' a graphical tilesheet which you can query for individual tiles '''
	def __init__(self, tileX, tileY, img):
		if type(img) == Surface:
			self.img = img
		else:
			self.img = pygame.image.load(img)
		self.tileX = tileX
		self.tileY = tileY
		self.sizeX, self.sizeY = self.img.get_size()
		self.tileSizeX = self.sizeX / self.tileX
		self.tileSizeY = self.sizeY / self.tileY
		self.tiles = [ [ 
			self.img.subsurface(Rect(x * self.tileSizeX, y * self.tileSizeY, self.tileSizeX, self.tileSizeY)) for y in range(tileY)
		] for x in range(tileX) ]
	# def tile(self, x, y):
	# 	return self.tiles[x][y]
	def tile(self, a):
		return self.tiles[a % self.tileX][int(a / self.tileX)]
	def tileXY(self, x, y):
		return self.tiles[x][y]


class TileMap(object):
	''' an object able to build an image from a tilesheet and a map '''
	def __init__(self, tileX, tileY, tilesheet):
		self.tileX = tileX
		self.tileY = tileY
		self.tilesheet = tilesheet
		self.map = [[ 0 for y in range(tileY) ] for x in range(tileX) ]
	def setTile(self, x, y, tile):
		self.map[x][y] = tile
	def getTile(self, x, y):
		return self.map[x][y]
	def draw(self, screen):
		for x in range(self.tileX):
			for y in range(self.tileY):
				screen.blit(self.tilesheet.tile(self.map[x][y]), 
					Rect(x * self.tilesheet.tileSizeX, y * self.tilesheet.tileSizeY, self.tilesheet.tileSizeX, self.tilesheet.tileSizeY))
	def build(self):
		surf = Surface((self.tilesheet.tileSizeX * self.tileX, self.tilesheet.tileSizeY * self.tileY), pygame.SRCALPHA)
		self.draw(surf)
		return surf
	def fromFile(self, filename):
		self.filename = filename
		with open(filename, 'r') as f:
			y = 0
			for line in f:
				x = 0
				for val in line.strip().split():
					if x >= self.tileX:
						die("tilemap too wide at line {}, file '{}'".format(y, filename))
					if y >= self.tileY:
						die("tilemap too long at line {}, file '{}'".format(y, filename))
					self.map[x][y] = int(val)
					x += 1
				y += 1
	def toFile(self, filename):
		with open(filename, 'w') as f:
			for y in range(0, self.tileY):
				f.write(' '.join([ str(self.map[x][y]) for x in range(0, self.tileX) ]) + "\n")
				

class Background(ScreenEntity):
	''' a simple entity which builds a screen image from a tilemap '''
	def __init__(self, tileX, tileY, tilemap, tilesheet, parent=None):
		super(Background, self).__init__(parent=parent)
		self.map = TileMap(tileX, tileY, tilesheet)
		self.map.fromFile(tilemap)
		self.build()
	def build(self):
		self.setImage(self.map.build())
	# def draw(self, screen):
	# 	self.map.draw(screen)








class TypeFace(TileSheet):
	''' a special TileSheet which allows mapping text characters to tiles to draw them'''
	def __init__(self, tileX, tileY, img, numericCharmap):
		super(TypeFace, self).__init__(tileX, tileY, img)
		self.numericCharmap = numericCharmap
		self.mapChars()
	def mapChars(self):
		self.charmap = {}
		for char in self.numericCharmap.keys():
			self.charmap[char] = self.tile(self.numericCharmap[char])
	def buildString(self, s):
		surf = Surface((self.tileSizeX * len(s), self.tileSizeY), pygame.SRCALPHA)
		i = 0
		for c in s:
			if self.charmap.get(c) is not None:
				surf.blit(self.charmap[c], (i * self.tileSizeX, 0))
			i += 1
		return surf


class TextEntity(ScreenEntity):
	''' a screen entity which draws a text image '''
	def __init__(self, typeface, text, x=0, y=0, parent=None):
		super(TextEntity, self).__init__(x, y, parent)
		self.typeface = typeface
		self.text = text
		self.build()
	def build(self):
		self.setImage(self.typeface.buildString(self.text))




class BoxEntity(ScreenEntity):
	''' a very basic box display which uses a 9 tile tilesheet '''
	def __init__(self, x, y, sizeX, sizeY, tilesheet, parent=None):
		super(BoxEntity, self).__init__(x, y, parent)
		if sizeX % tilesheet.tileSizeX != 0 or sizeY % tilesheet.tileSizeY:
			die("textbox size must be a multiple of tile size!")
		self.tilesheet = tilesheet
		self.sizeX = sizeX
		self.sizeY = sizeY
		self.setImage(self.build())
	def build(self):
		surf = Surface((self.sizeX, self.sizeY), pygame.SRCALPHA)
		tx = self.tilesheet.tileSizeX
		ty = self.tilesheet.tileSizeY

		topleft = self.tilesheet.tileXY(0, 0)
		surf.blit(topleft, (0, 0))
		top = self.tilesheet.tileXY(1, 0)
		for x in range(1, self.sizeX / tx - 1):
			surf.blit(top, (x * tx, 0))
		topright = self.tilesheet.tileXY(2, 0)
		surf.blit(topright, (self.sizeX - tx, 0))
		left = self.tilesheet.tileXY(0, 1)
		for y in range(1, self.sizeY / ty - 1):
			surf.blit(left, (0, y * ty))
		middle = self.tilesheet.tileXY(1, 1)
		for x in range(1, self.sizeX / tx - 1):
			for y in range(1, self.sizeY / ty - 1):
				surf.blit(middle, (x * tx, y * ty))
		right = self.tilesheet.tileXY(2, 1)
		for y in range(1, self.sizeY / ty - 1):
			surf.blit(right, (self.sizeX - tx, y * ty))
		botleft = self.tilesheet.tileXY(0, 2)
		surf.blit(botleft, (0, self.sizeY - ty))
		bot = self.tilesheet.tileXY(1, 2)
		for x in range(1, self.sizeX / tx - 1):
			surf.blit(bot, (x * tx, self.sizeY - ty))
		botright = self.tilesheet.tileXY(2, 2)
		surf.blit(botright, (self.sizeX - tx, self.sizeY - ty))

		return surf


class TextBoxEntity(BoxEntity):
	def __init__(self, textent, x, y, sizeX, sizeY, tilesheet, parent=None):
		self.textent = textent
		super(TextBoxEntity, self).__init__(x, y, sizeX, sizeY, tilesheet, parent)
	def build(self):
		surf = super(TextBoxEntity, self).build()
		surf.blit(self.textent.img, (self.sizeX / 2 - self.textent.rect.w / 2, self.sizeY / 2 - self.textent.rect.h / 2))
		return surf




class OffsetCamera(object):
	'''simple wrapper class which offsets every .blit attempted'''

	def __init__(self, surf, offsetX=0, offsetY=0, *args, **kwargs):
		super(OffsetCamera, self).__init__(*args, **kwargs)
		self.surf = surf
		self.offsetX = -offsetX # we need negative values to offset properly
		self.offsetY = -offsetY
		self.fill = surf.fill
	def blit(self, surf, pos):
		if issubclass(type(pos), Rect):
			pos = pos.move(self.offsetX, self.offsetY)
		else:
			pos = (pos[0] + self.offsetX, pos[1] + self.offsetY)
		self.surf.blit(surf, pos)

