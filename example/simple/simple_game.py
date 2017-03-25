#!/usr/bin/env python

import sys

sys.path.append('../../telekinesis')
import telekinesis
import pygame

class SimpleGame(telekinesis.gamecore.GameContainer):
	def draw(self, screen):
		screen.fill((0,0,0))
		super(SimpleGame, self).draw(screen)


class ShipEntity(telekinesis.graphics.ScreenEntity):
	def __init__(self, x=0, y=0, sx=0, sy=0, bounding_box=None, parent=None, filepath=None):
		super(ShipEntity, self).__init__(x=x, y=y, parent=parent, filepath=filepath)
		self.bounding_box = bounding_box
		self.bounding_box.x += x
		self.bounding_box.y += y
		self.sx = sx
		self.sy = sy
	def update(self):
		self.rect.x += self.sx
		self.rect.y += self.sy
		self.bounding_box.x += self.sx
		self.bounding_box.y += self.sy



class Dropship(ShipEntity):
	def __init__(self, x=0, y=0, parent=None):
		super(Dropship, self).__init__(x=x, y=y, parent=parent, bounding_box=pygame.Rect(3, 23, 34, 14), filepath='dropship_down.png')


class PlayerBullet(telekinesis.graphics.ScreenEntity):
	def __init__(self, x=0, y=0, sx=0, sy=0, parent=None):
		super(PlayerBullet, self).__init__(x=x, y=y, parent=parent, filepath='player_bullet.png')
		self.sx = sx
		self.sy = sy
	def update(self):
		self.rect.x += self.sx
		self.rect.y += self.sy
		game = self.parent.getGame()
		if self.rect.x + self.rect.w < 0 or self.rect.x > game.sizeX or self.rect.y + self.rect.h < 0 or self.rect.y > game.sizeY:
			self.removeSelf()

class PlayerShip(ShipEntity):
	def __init__(self, x=0, y=0, parent=None):
		super(PlayerShip, self).__init__(x=x, y=y, parent=parent, bounding_box=pygame.Rect(3, 3, 34, 14), filepath='dropship.png')
		self.reload = 0
		self.max_reload = 3
	def update(self):
		game = self.parent.getGame()

		if game.keystate[pygame.K_LSHIFT]:
			speed = 2
		else:
			speed = 4


		if game.keystate[pygame.K_a]:
			self.sx -= 1
			if self.sx < -speed:
				self.sx = -speed
		elif game.keystate[pygame.K_d]:
			self.sx += 1
			if self.sx > speed:
				self.sx = speed
		else:
			if self.sx < 0:
				self.sx += 2
			elif self.sx > 0:
				self.sx -= 2

		if game.keystate[pygame.K_w]:
			self.sy -= 1
			if self.sy < -speed:
				self.sy = -speed
		elif game.keystate[pygame.K_s]:
			self.sy += 1
			if self.sy > speed:
				self.sy = speed
		else:
			if self.sy < 0:
				self.sy += 2
			elif self.sy > 0:
				self.sy -= 2

		if self.reload > 0:
			self.reload -= 1
		elif game.keystate[pygame.K_SPACE]:
			self.parent.addEntity(PlayerBullet(x=self.rect.x + self.rect.w / 2 - 10, y=self.rect.y - 20, sy=-12))
			self.reload = self.max_reload

		super(PlayerShip, self).update()


parser = telekinesis.logic.LayoutReader({
		'Dropship': Dropship,
	})

game = SimpleGame()
for ent in parser.fromFile('simple_game.layout'):
	game.addEntity(ent)
game.addEntity(PlayerShip())
game.run()

