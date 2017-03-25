#!/usr/bin/env python

import sys

sys.path.append('../../telekinesis')
import telekinesis
import pygame

class Dropship(telekinesis.graphics.ScreenEntity):
	def __init__(self, x=0, y=0, parent=None):
		super(Dropship, self).__init__(x=x, y=y, parent=parent, filepath='dropship.png')

class SimpleGame(telekinesis.gamecore.GameContainer):
	def draw(self, screen):
		screen.fill((0,0,0))
		super(SimpleGame, self).draw(screen)

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

class PlayerShip(telekinesis.graphics.ScreenEntity):
	def __init__(self, x=0, y=0, parent=None):
		super(PlayerShip, self).__init__(x=x, y=y, parent=parent, filepath='dropship.png')
		self.reload = 0
		self.max_reload = 3
	def update(self):
		game = self.parent.getGame()

		if game.keystate[pygame.K_LSHIFT]:
			speed = 2
		else:
			speed = 4

		if game.keystate[pygame.K_a]:
			self.rect.x -= speed
		if game.keystate[pygame.K_d]:
			self.rect.x += speed
		if game.keystate[pygame.K_w]:
			self.rect.y -= speed
		if game.keystate[pygame.K_s]:
			self.rect.y += speed

		if self.reload > 0:
			self.reload -= 1
		elif game.keystate[pygame.K_SPACE]:
			self.parent.addEntity(PlayerBullet(x=self.rect.x + self.rect.w / 2 - 10, y=self.rect.y - 20, sy=-12))
			self.reload = self.max_reload


parser = telekinesis.logic.LayoutReader({
		'Dropship': Dropship,
	})

game = SimpleGame()
for ent in parser.fromFile('simple_game.layout'):
	game.addEntity(ent)
game.addEntity(PlayerShip())
game.run()

