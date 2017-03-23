#!/usr/bin/env python

import sys

sys.path.append('../../telekinesis')
import telekinesis

class Dropship(telekinesis.graphics.ScreenEntity):
	def __init__(self, x=0, y=0, parent=None):
		super(Dropship, self).__init__(x=x, y=y, parent=parent, filepath='dropship.png')

class SimpleGame(telekinesis.gamecore.GameContainer):
	pass


parser = telekinesis.logic.LayoutReader({
		'Dropship': Dropship,
	})

game = SimpleGame()
for ent in parser.fromFile('simple_game.layout'):
	game.addEntity(ent)
game.run()

