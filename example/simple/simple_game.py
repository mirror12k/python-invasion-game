#!/usr/bin/env python

import sys

sys.path.append('../../telekinesis')
import telekinesis
import pygame


class PlayerBulletContainer(telekinesis.gamecore.ContainerEntity):
	def update(self):
		super(PlayerBulletContainer, self).update()
		bullet_boxes = [ bullet.bounding_box for bullet in self.entities ]
		# print "debug bullets", len(self.entities)
		for ent in [ ent for ent in self.parent.entities if isinstance(ent, CollidingEntity) ]:
			index = ent.bounding_box.collidelist(bullet_boxes)
			if index != -1:
				ent.takeDamage(self.entities[index].damage)
				self.removeEntity(self.entities[index])

class EnemyBulletContainer(telekinesis.gamecore.ContainerEntity):
	def update(self):
		super(EnemyBulletContainer, self).update()
		bullet_boxes = [ bullet.bounding_box for bullet in self.entities ]
		# print "debug bullets", len(self.entities)
		player = self.parent.player
		index = player.bounding_box.collidelist(bullet_boxes)
		if index != -1:
			player.takeDamage(self.entities[index].damage)
			self.removeEntity(self.entities[index])



class SimpleGame(telekinesis.gamecore.GameContainer):
	def __init__(self):
		super(SimpleGame, self).__init__(sizeX=1000, sizeY=640)
		self.player_bullet_container = PlayerBulletContainer(parent=self)
		self.enemy_bullet_container = EnemyBulletContainer(parent=self)
		self.player = PlayerShip(x=480, y=580, parent=self)
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
		self.sx = float(sx)
		self.sy = float(sy)
		self.x = float(x)
		self.y = float(y)
		self.bounding_box_x = float(self.bounding_box.x)
		self.bounding_box_y = float(self.bounding_box.y)
	def update(self):
		self.x += float(self.sx)
		self.y += float(self.sy)
		self.bounding_box_x += float(self.sx)
		self.bounding_box_y += float(self.sy)
		self.rect.x = int(self.x)
		self.rect.y = int(self.y)
		self.bounding_box.x = int(self.bounding_box_x)
		self.bounding_box.y = int(self.bounding_box_y)

class ShipEntity(CollidingEntity):
	def __init__(self, health=1, max_reload=60, *args, **kwargs):
		super(ShipEntity, self).__init__(*args, **kwargs)
		self.health = health
		self.reload = 0
		self.max_reload = max_reload
	def update(self):
		super(ShipEntity, self).update()
		if self.reload > 0:
			self.reload -= 1
	def takeDamage(self, damage):
		self.health -= damage
		if self.health <= 0:
			self.onDeath()
			self.removeSelf()
	def onDeath(self):
		pass
	def fire(self):
		self.reload = self.max_reload

def calculate_adjusted_speed(x, y, speed):
	c = (float(x) ** 2 + float(y) ** 2) ** 0.5
	multiplier = float(speed) / c
	return x * multiplier, y * multiplier

class Dropship(ShipEntity):
	def __init__(self, *args, **kwargs):
		super(Dropship, self).__init__(bounding_box=pygame.Rect(3, 23, 34, 14), filepath='dropship_down.png', *args, **kwargs)

class DropshipFiring(Dropship):
	def update(self):
		super(DropshipFiring, self).update()
		if self.reload == 0:
			self.fire()
	def fire(self):
		super(DropshipFiring, self).fire()
		player = self.parent.getGame().player
		px, py = player.rect.x + player.rect.w / 2, player.rect.y + player.rect.h / 2
		x, y = self.rect.x + self.rect.w / 2, self.rect.y + self.rect.h / 2
		sx, sy = calculate_adjusted_speed(px - x, py - y, 3)
		self.parent.getGame().enemy_bullet_container.addEntity(EnemyBullet(x=x - 10, y=y - 10, sx=sx, sy=sy))
		

class BulletEntity(CollidingEntity):
	def __init__(self, damage=5, *args, **kwargs):
		super(BulletEntity, self).__init__(*args, **kwargs)
		self.damage = damage
	def update(self):
		super(BulletEntity, self).update()
		game = self.parent.getGame()
		if self.rect.x + self.rect.w < 0 or self.rect.x > game.sizeX or self.rect.y + self.rect.h < 0 or self.rect.y > game.sizeY:
			self.removeSelf()

class PlayerBullet(BulletEntity):
	def __init__(self, *args, **kwargs):
		super(PlayerBullet, self).__init__(bounding_box=pygame.Rect(8, 3, 4, 14), filepath='player_bullet.png', *args, **kwargs)

class EnemyBullet(BulletEntity):
	def __init__(self, *args, **kwargs):
		super(EnemyBullet, self).__init__(bounding_box=pygame.Rect(5, 5, 10, 10), filepath='enemy_bullet_red.png', *args, **kwargs)



class PlayerShip(ShipEntity):
	def __init__(self, *args, **kwargs):
		super(PlayerShip, self).__init__(bounding_box=pygame.Rect(3, 3, 34, 14), filepath='dropship.png', max_reload = 3, *args, **kwargs)
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

		if game.keystate[pygame.K_SPACE] and self.reload == 0:
			self.fire()

		super(PlayerShip, self).update()

	def fire(self):
		super(PlayerShip, self).fire()
		game.player_bullet_container.addEntity(PlayerBullet(x=self.rect.x + self.rect.w / 2 - 10, y=self.rect.y - 20, sy=-12))




game = SimpleGame()
parser = telekinesis.logic.LayoutReader(game, {
		'Dropship': Dropship,
		'DropshipFiring': DropshipFiring,
		'DelayedSpawn': telekinesis.logic.DelayedSpawn,
	})
parser.fromFile('simple_game.layout')
game.run()

