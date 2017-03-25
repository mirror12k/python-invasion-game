#!/usr/bin/env python

import sys

sys.path.append('../../telekinesis')
import telekinesis
import pygame


class BulletContainer(telekinesis.gamecore.ContainerEntity):
	def update(self):
		super(BulletContainer, self).update()
		bullet_boxes = [ bullet.bounding_box for bullet in self.entities ]
		# print "debug bullets", len(self.entities)
		for ent in [ ent for ent in self.parent.entities if isinstance(ent, CollidingEntity) ]:
			index = ent.bounding_box.collidelist(bullet_boxes)
			if index != -1:
				ent.takeDamage(self.entities[index].damage)
				self.removeEntity(self.entities[index])



class SimpleGame(telekinesis.gamecore.GameContainer):
	def __init__(self):
		super(SimpleGame, self).__init__()
		self.bullet_container = BulletContainer(parent=self)
	def draw(self, screen):
		screen.fill((0,0,0))
		super(SimpleGame, self).draw(screen)
	def update(self):
		super(SimpleGame, self).update()
		# print "debug", len(self.entities)


class CollidingEntity(telekinesis.graphics.ScreenEntity):
	def __init__(self, x=0, y=0, sx=0, sy=0, bounding_box=None, parent=None, filepath=None):
		super(CollidingEntity, self).__init__(x=x, y=y, parent=parent, filepath=filepath)
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



class Dropship(CollidingEntity):
	def __init__(self, x=0, y=0, parent=None):
		super(Dropship, self).__init__(x=x, y=y, parent=parent, bounding_box=pygame.Rect(3, 23, 34, 14), filepath='dropship_down.png')
		self.health = 25
	def takeDamage(self, damage):
		self.health -= damage
		if self.health <= 0:
			self.removeSelf()


class PlayerBullet(CollidingEntity):
	def __init__(self, damage=5, *args, **kwargs):
		super(PlayerBullet, self).__init__(bounding_box=pygame.Rect(8, 3, 4, 14), filepath='player_bullet.png', *args, **kwargs)
		self.damage = damage
	def update(self):
		super(PlayerBullet, self).update()
		game = self.parent.getGame()
		if self.rect.x + self.rect.w < 0 or self.rect.x > game.sizeX or self.rect.y + self.rect.h < 0 or self.rect.y > game.sizeY:
			self.removeSelf()

class PlayerShip(CollidingEntity):
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
			game.bullet_container.addEntity(PlayerBullet(x=self.rect.x + self.rect.w / 2 - 10, y=self.rect.y - 20, sy=-12))
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

