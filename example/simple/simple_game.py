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

class PlayerShip(telekinesis.graphics.ScreenEntity):
	def __init__(self, x=0, y=0, parent=None):
		super(PlayerShip, self).__init__(x=x, y=y, parent=parent, filepath='dropship.png')
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


parser = telekinesis.logic.LayoutReader({
		'Dropship': Dropship,
	})

game = SimpleGame()
for ent in parser.fromFile('simple_game.layout'):
	game.addEntity(ent)
game.addEntity(PlayerShip())
game.run()

