import pygame
import random
import sys
import time
import numpy as np

FPS = 60
window_width = 800
window_height = 600

size = 5

nest_size = 30

ant_sum = 50
food_sum = 50


nest_list = pygame.sprite.Group()
ant_list = pygame.sprite.Group()
food_list = pygame.sprite.Group()
all_list = pygame.sprite.Group()
phero_list = pygame.sprite.Group()

phero_map = [[0 for x in range(window_height)] for y in range(window_width)]
food_map = [[0 for x in range(window_height)] for y in range(window_width)]

BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,0xE6)
WHITE = (255,255,255)
PURPLE = (0xE8,0,0xE8)
		
class Nest(pygame.sprite.Sprite):
	def __init__(self,nest_position_x,nest_position_y,color,antcolor):
		super().__init__()
		self.position_x = nest_position_x
		self.position_y = nest_position_y
		self.color = color
		self.image = pygame.Surface([nest_size,nest_size])
		self.image.fill(color)
		self.rect = self.image.get_rect()
		self.rect.topleft = (self.position_x, self.position_y)
		
		for i in range(ant_sum):
			ant = Ant(self.position_x,self.position_y,antcolor)
			ant_list.add(ant)
			all_list.add(ant)

class Ant(pygame.sprite.Sprite):
	def __init__(self,nest_position_x,nest_position_y,color):
		super().__init__()
		
		#init position (in nest)
		self.position_x = random.randint(nest_position_x,nest_position_x + nest_size - size)
		self.position_y = random.randint(nest_position_y,nest_position_y + nest_size - size)
		
		self.nest_position_x = nest_position_x
		self.nest_position_y = nest_position_y
		
		self.color = color
		self.search_color = color
		self.image = pygame.Surface([size,size])
		self.image.fill(color)
		self.rect = self.image.get_rect()
		self.rect.topleft = (self.position_x, self.position_y)
		# health
		self.health = random.randint(1000,1200)
		#state
		self.state = "search"	
		
		self.type = random.randint(0,1)
		
		if self.type == 1:
			self.computeQuad()
	
	def computeQuad(self):
		if self.position_x > self.nest_position_x + 15:
			if self.position_y > self.nest_position_y +15:
				self.quad = (-1,-1)
			else:
				self.quad = (-1,1)
		else:
			if self.position_y > self.nest_position_y +15:
				self.quad = (1,-1)
			else:
				self.quad = (1, 1)
			
	def update(self):
		if self.state == "search":
			if self.health == 0:
				self.color = BLACK
				self.image.fill(self.color)
				self.health = 20
				self.state = "dead"
			elif pygame.sprite.spritecollide(self,food_list,False):
				self.color = (255,0,255)
				self.image.fill(self.color)
				self.health +=100 #先吃一點補體力
				self.state = "backhome"
			else:
				x = random.randint(-5,5)
				while (self.position_x + x <= 0 or self.position_x + x >= window_width - size):
					self.type = 0
					x = random.randint(-5,5)
				
				y = random.randint(-5,5)
				while(self.position_y + y<=0 or self.position_y + y >= window_height - size):
					self.type = 0
					y = random.randint(-5,5)
				
				if self.type == 1:
					while(x*self.quad[0] > 0 and y*self.quad[1] > 0):
						x = random.randint(-5,5)
						while(self.position_x + x<=0 or self.position_x + x >= window_width - size):
							x = random.randint(-5,5)
					
						y = random.randint(-5,5)
						while(self.position_y + y<=0 or self.position_y + y >= window_height - size):
							y = random.randint(-5,5)
				
				
				
				self.position_x += x
				self.position_y += y
			
				self.rect.topleft = (self.position_x, self.position_y)
				
			self.health -= 1		
		
		
		
		elif self.state == "backhome":
			if self.health == 0:
				self.color = BLACK
				self.image.fill(self.color)
				self.health = 20
				self.state = "dead"
			elif pygame.sprite.spritecollide(self,nest_list,False):
				self.color = self.search_color
				self.image.fill(self.color)
				self.health = random.randint(1000,1200)
				
				for i in range(1):
					ant = Ant(self.nest_position_x,self.nest_position_y,self.search_color)
					ant_list.add(ant)
					all_list.add(ant)
				
				self.state = "search"
				self.type = random.randint(0, 1)
				if self.type == 1:
					self.computeQuad()
				# 補充食物到 window
				if random.randint(1,10) >= 6:
					food = Food(RED)
					food_list.add(food)
					all_list.add(food)
				
			elif abs(self.nest_position_x + 15 - self.position_x) <= abs(self.nest_position_y + 15 - self.position_y):
				if self.nest_position_y >= self.position_y:
					self.position_y += 5
				else:
					self.position_y -= 5
			else:
				if self.nest_position_x >= self.position_x:
					self.position_x += 5
				else:
					self.position_x -= 5
			self.rect.topleft = (self.position_x, self.position_y)
			self.health -= 1
			
			
			
		elif self.state == "dead":
			if self.health == 0:
				pygame.sprite.Sprite.kill(self)
			else:
				self.health -=1
	

class Food(pygame.sprite.Sprite):
	def __init__(self,color):		
		super().__init__()
		x = random.randint(0,159)
		y = random.randint(0,119)
		
		#food position	
		self.position_x = x
		self.position_y = y
		
		self.health = random.randint(1,10)
		
		
		food_map[x][y] += 1
		
		self.color = color
		self.image = pygame.Surface([size,size])
		self.image.fill(color)
		self.rect = self.image.get_rect()
		self.rect.topleft = (self.position_x*size,self.position_y*size)
	def update(self):
		if pygame.sprite.spritecollide(self,ant_list,False):
			self.health -=1
		if self.health == 0:
			pygame.sprite.Sprite.kill(self)
			
		

	
def main():
	pygame.init()
    # load window surface
	window = pygame.display.set_mode((window_width,window_height))
	pygame.display.set_caption('bug nest')
	window.fill(WHITE)
	
	for i in range(food_sum):
		food = Food(RED)
		food_list.add(food)
		all_list.add(food)
	
	nest_position_x = 300 #random.randint(300,400)
	nest_position_y = 200 #random.randint(200,300)
	nest = Nest(nest_position_x,nest_position_y,BLACK,BLUE)
	nest_list.add(nest)
	all_list.add(nest)
	
	nest_position_x = 600 #random.randint(500,600)
	nest_position_y = 400 #random.randint(300,400)
	nest = Nest(nest_position_x,nest_position_y,BLACK,GREEN)
	nest_list.add(nest)
	all_list.add(nest)
	
	
	clock = pygame.time.Clock()

	while(True):
		clock.tick(FPS)
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()
		
		
		ant_list.update()
		phero_list.update()
		food_list.update()
		#reflesh
		window.fill(WHITE)

		all_list.draw(window)
		
		pygame.display.update()
		
		
if __name__ == '__main__':
	main()
		
		
		
