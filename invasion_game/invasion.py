#!/usr/bin/env python

import sys
import math
import random

sys.path.append('../telekinesis')
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
				ent.take_damage(self.entities[index].damage)
				self.removeEntity(self.entities[index])

class EnemyBulletContainer(telekinesis.gamecore.ContainerEntity):
	def update(self):
		super(EnemyBulletContainer, self).update()
		bullet_boxes = [ bullet.bounding_box for bullet in self.entities ]
		# print "debug bullets", len(self.entities)
		player = self.parent.player
		index = player.bounding_box.collidelist(bullet_boxes)
		if index != -1:
			player.take_damage(self.entities[index].damage)
			self.removeEntity(self.entities[index])



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
		self.move(self.sx, self.sy)
	def move(self, x=0, y=0):
		self.x += float(x)
		self.y += float(y)
		self.bounding_box_x += float(x)
		self.bounding_box_y += float(y)
		self.rect.x = int(self.x)
		self.rect.y = int(self.y)
		self.bounding_box.x = int(self.bounding_box_x)
		self.bounding_box.y = int(self.bounding_box_y)

class BulletEntity(CollidingEntity):
	def __init__(self, damage=5, expires=None, *args, **kwargs):
		super(BulletEntity, self).__init__(*args, **kwargs)
		self.damage = damage
		self.expires = expires
	def update(self):
		super(BulletEntity, self).update()
		game = self.parent.getGame()
		if not self.rect.colliderect(game.screen_bounds):
			self.removeSelf()
		elif self.expires is not None:
			if self.expires == 0:
				self.removeSelf()
			else:
				self.expires -= 1

class PlayerBullet(BulletEntity):
	def __init__(self, *args, **kwargs):
		super(PlayerBullet, self).__init__(bounding_box=pygame.Rect(8, 3, 4, 14), filepath='player_bullet.png', *args, **kwargs)

class EnemyBullet(BulletEntity):
	def __init__(self, *args, **kwargs):
		super(EnemyBullet, self).__init__(bounding_box=pygame.Rect(5, 5, 10, 10), filepath='enemy_bullet_red.png', *args, **kwargs)
class EnemyBulletBlue(BulletEntity):
	def __init__(self, *args, **kwargs):
		super(EnemyBulletBlue, self).__init__(bounding_box=pygame.Rect(13, 13, 14, 14), filepath='enemy_bullet_blue.png', *args, **kwargs)
	def update(self):
		super(EnemyBulletBlue, self).update()
		self.sx *= 0.95
		self.sy *= 0.95




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
	def take_damage(self, damage):
		self.health -= damage
		if self.health <= 0:
			self.onDeath()
			self.removeSelf()
	def onDeath(self):
		pass
	def fire(self):
		self.reload = self.max_reload

class EnemyShipEntity(ShipEntity):
	def __init__(self, *args, **kwargs):
		super(EnemyShipEntity, self).__init__(*args, **kwargs)
		self.active = False

	def update(self):
		super(EnemyShipEntity, self).update()
		game = self.parent.getGame()
		if not self.active and self.bounding_box.colliderect(game.active_bounds):
			self.active = True
		if self.active and self.reload == 0:
			self.fire()
		if not self.rect.colliderect(game.out_of_bounds):
			self.removeSelf()
	def take_damage(self, damage):
		if not self.active:
			# apply armor until ship is fully on screen
			damage /= 4
		super(EnemyShipEntity, self).take_damage(damage)
	def spawn_bullet_at_player(self, speed, angle_delta=0, *aargs, **kwargs):
		player = self.parent.getGame().player
		px, py = player.rect.x + player.rect.w / 2, player.rect.y + player.rect.h / 2
		x, y = self.rect.x + self.rect.w / 2, self.rect.y + self.rect.h / 2
		angle = calculate_angle(px - x, py - y)
		# print "debug angle:", angle
		self.spawn_bullet(speed, angle + angle_delta, *aargs, **kwargs)
	def spawn_bullet(self, speed, angle, expires=None, bullet_type=EnemyBullet):
		sx, sy = angle_to_normal(angle)
		# print "debug sx, sy:", sx, sy
		sx = sx * float(speed)
		sy = sy * float(speed)
		x, y = self.rect.x + self.rect.w / 2, self.rect.y + self.rect.h / 2
		self.parent.getGame().enemy_bullet_container.addEntity(bullet_type(x=x-10, y=y-10, sx=sx, sy=sy, expires=expires))



def calculate_angle(dx, dy):
	return math.atan2(float(dy), float(dx))

def angle_to_normal(angle):
	return math.cos(angle), math.sin(angle)

def distance_point_to_point(p0, p1):
	return ((p1[0] - p0[0]) ** 2 + (p1[1] - p0[1]) ** 2) ** 0.5

def distance_point_to_line(l0, l1, p):
	return abs((l1[1] - l0[1]) * p[0] - (l1[0] - l0[0]) * p[1] + l1[0] * l0[1] - l1[1] * l0[0]) / distance_point_to_point(l0, l1)

class Dropship(EnemyShipEntity):
	def __init__(self, *args, **kwargs):
		super(Dropship, self).__init__(
			bounding_box=pygame.Rect(3, 23, 34, 14),
			filepath='dropship_down.png',
			health=25,
			*args, **kwargs)

class DropshipFiring(Dropship):
	def fire(self):
		super(DropshipFiring, self).fire()
		self.spawn_bullet_at_player(2)
		

class LightFighter(EnemyShipEntity):
	def __init__(self, *args, **kwargs):
		super(LightFighter, self).__init__(
			bounding_box=pygame.Rect(3, 23, 34, 14),
			filepath='light_fighter_down.png',
			health=15,
			max_reload=60,
			*args, **kwargs)

	def fire(self):
		super(LightFighter, self).fire()
		self.spawn_bullet_at_player(4)
		self.spawn_bullet_at_player(4, math.radians(15.0))
		self.spawn_bullet_at_player(4, math.radians(-15.0))

class TroopTransport(EnemyShipEntity):
	def __init__(self, *args, **kwargs):
		super(TroopTransport, self).__init__(
			bounding_box=pygame.Rect(3, 23, 34, 14),
			filepath='troop_transport_down.png',
			health=100,
			max_reload=4,
			*args, **kwargs)

	def fire(self):
		super(TroopTransport, self).fire()
		self.spawn_bullet(random.randint(5, 10), math.radians(random.randint(0, 360)), expires=300+random.randint(0, 120), bullet_type=EnemyBulletBlue)


class LightSuppressionCrystal(EnemyShipEntity):
	def __init__(self, *args, **kwargs):
		super(LightSuppressionCrystal, self).__init__(
			bounding_box=pygame.Rect(9, 18, 42, 26),
			filepath='light_suppression_crystal.png',
			health=500,
			max_reload=240,
			*args, **kwargs)
		self.firing_laser = 0
		self.laser_target = None

		self.charge_duration = 30
		self.laser_duration = 60

		self.charging_laser = 0
		self.firing_laser = 0
	def fire(self):
		super(LightSuppressionCrystal, self).fire()
		self.fire_laser_at_player()

	def fire_laser_at_player(self, angle_delta=0):
		player = self.parent.getGame().player
		px, py = player.rect.x + player.rect.w / 2, player.rect.y + player.rect.h / 2
		x, y = self.rect.x + self.rect.w / 2, self.rect.y + self.rect.h / 2
		angle = calculate_angle(px - x, py - y)
		self.fire_laser(angle + angle_delta)

	def fire_laser(self, angle):
		nx, ny = angle_to_normal(angle)
		x, y = self.rect.x + self.rect.w / 2, self.rect.y + self.rect.h / 2
		self.laser_target = (x + nx * 1000, y + ny * 1000)
		self.charging_laser = self.charge_duration

	def move(self, x=0, y=0):
		super(LightSuppressionCrystal, self).move(x,y)
		if self.laser_target is not None:
			self.laser_target = (self.laser_target[0] + x, self.laser_target[1] + y)

	def update(self):
		super(LightSuppressionCrystal, self).update()
		if self.charging_laser > 0:
			self.charging_laser -= 1
			if self.charging_laser == 0:
				self.firing_laser = self.laser_duration
		if self.firing_laser > 0:
			self.firing_laser -= 1
			x, y = self.rect.x + self.rect.w / 2, self.rect.y + self.rect.h / 2
			player = self.parent.getGame().player
			px, py = player.rect.x + player.rect.w / 2, player.rect.y + player.rect.h / 2
			dist = distance_point_to_line((x,y), self.laser_target, (px, py))
			if dist <= 10:
				player.take_damage(1)


	def draw(self, screen):
		if self.charging_laser:
			x, y = self.rect.x + self.rect.w / 2, self.rect.y + self.rect.h / 2
			pygame.draw.line(screen, (255,0,0), (x, y), self.laser_target, 1)
		if self.firing_laser:
			x, y = self.rect.x + self.rect.w / 2, self.rect.y + self.rect.h / 2
			pygame.draw.line(screen, (255,255,255), (x, y), self.laser_target, 21)
			pygame.draw.line(screen, (255,128,128), (x, y), self.laser_target, 15)
			pygame.draw.line(screen, (255,0,0), (x, y), self.laser_target, 11)
			pygame.draw.line(screen, (255,64,64), (x, y), self.laser_target, 5)
		super(LightSuppressionCrystal, self).draw(screen)



class PlayerShip(ShipEntity):
	def __init__(self, *args, **kwargs):
		super(PlayerShip, self).__init__(
			bounding_box=pygame.Rect(3, 3, 34, 14),
			filepath='dropship.png',
			max_reload = 3,
			*args, **kwargs)

		self.max_speed = 6
		self.invuln = 60
	def update(self):
		game = self.parent.getGame()

		if game.keystate[pygame.K_LSHIFT]:
			speed = self.max_speed / 2
		else:
			speed = self.max_speed


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
			self.fire(concentrated=game.keystate[pygame.K_LSHIFT])

		if self.invuln > 0:
			self.invuln -= 1

		super(PlayerShip, self).update()

		if self.bounding_box.x < 0:
			self.move(0 - self.bounding_box.x, 0)
			self.sx = 0.0
		elif self.bounding_box.x + self.bounding_box.w > game.screen_bounds.w:
			self.move(game.screen_bounds.w - (self.bounding_box.x + self.bounding_box.w), 0)
			self.sx = 0.0

		if self.bounding_box.y < 0:
			self.move(0, 0 - self.bounding_box.y)
			self.sy = 0.0
		elif self.bounding_box.y + self.bounding_box.h > game.screen_bounds.h:
			self.move(0, game.screen_bounds.h - (self.bounding_box.y + self.bounding_box.h))
			self.sy = 0.0


	def take_damage(self, damage):
		if self.parent and self.invuln == 0:
			self.parent.getGame().on_player_death()

	def draw(self, screen):
		if self.invuln % 2 == 0:
			super(PlayerShip, self).draw(screen)

	def fire(self, concentrated):
		super(PlayerShip, self).fire()
		if concentrated:
			game.player_bullet_container.addEntity(PlayerBullet(x=self.rect.x + self.rect.w / 2 - 15, y=self.rect.y - 25, sy=-20))
			game.player_bullet_container.addEntity(PlayerBullet(x=self.rect.x + self.rect.w / 2 - 5, y=self.rect.y - 15, sy=-20))
		else:
			game.player_bullet_container.addEntity(PlayerBullet(x=self.rect.x + self.rect.w / 2 - 25, y=self.rect.y - 10, sy=-20))
			game.player_bullet_container.addEntity(PlayerBullet(x=self.rect.x + self.rect.w / 2 + 5, y=self.rect.y - 10, sy=-20))



class DebugPrinter(telekinesis.gamecore.Entity):
	def __init__(self, *args, **kwargs):
		super(DebugPrinter, self).__init__(*args, **kwargs)
		self.zIndex = 1000000
	def draw(self, screen):
		game = self.parent.getGame()
		entity_count = len(game.entities)
		bullet_count = len(game.enemy_bullet_container.entities) + len(game.player_bullet_container.entities)
		debug_text1 = "fps: {}".format(game.real_fps)
		debug_text2 = "entities: {} ({} bullets)".format(entity_count, bullet_count)
		debug_text1 = game.font.render(debug_text1, 1, (255,255,0))
		debug_text2 = game.font.render(debug_text2, 1, (255,255,0))
		screen.blit(debug_text1, (4,4))
		screen.blit(debug_text2, (4,24))

		for ent in game.entities:
			if isinstance(ent, CollidingEntity):
				pygame.draw.rect(screen, (255, 0, 0), ent.bounding_box, 2)





class InvasionGameContainer(telekinesis.gamecore.GameContainer):
	def __init__(self):
		super(InvasionGameContainer, self).__init__(sizeX=1000, sizeY=640)
		self.screen_bounds = pygame.Rect(0, 0, self.sizeX, self.sizeY)
		self.active_bounds = pygame.Rect(40, 40, self.sizeX - 40, self.sizeY - 40)
		self.out_of_bounds = pygame.Rect(-200, -200, self.sizeX + 200, self.sizeY + 200)
		self.player_bullet_container = PlayerBulletContainer(parent=self)
		self.enemy_bullet_container = EnemyBulletContainer(parent=self)
		self.spawn_player()
		# telekinesis.logic.Timer([], 1, parent=self)
	def draw(self, screen):
		screen.fill((0,0,0))
		super(InvasionGameContainer, self).draw(screen)
	def update(self):
		super(InvasionGameContainer, self).update()
		self.sortEntities()
	def spawn_player(self, *args):
		self.player = PlayerShip(x=480, y=580, parent=self)
	def on_player_death(self):
		self.player.removeSelf()
		telekinesis.logic.Timer([self.spawn_player], 1, parent=self)


game = InvasionGameContainer()
parser = telekinesis.logic.LayoutReader(game, {
		'Dropship': Dropship,
		'DropshipFiring': DropshipFiring,
		'LightFighter': LightFighter,
		'TroopTransport': TroopTransport,
		'LightSuppressionCrystal': LightSuppressionCrystal,
		'DelayedSpawn': telekinesis.logic.DelayedSpawn,
	})
parser.fromFile('level1.layout')
game.addEntity(DebugPrinter())
game.run()

