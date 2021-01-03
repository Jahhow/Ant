import pygame
import random
import sys
import time
import numpy as np
import math

FPS = 30
window_width = 800
window_height = 600

size = 5

nest_size = 30

ant_sum = 50
food_sum = 50

food_odor = 20
backhome_speed = 5
momentum = 0.5

nest_list = pygame.sprite.Group()
ant_list = pygame.sprite.Group()
food_list = pygame.sprite.Group()
all_list = pygame.sprite.Group()

foodmap = [[0 for y in range(window_height)] for x in range(window_width)]
pheromap = [[0 for y in range(window_height)] for x in range(window_width)]

BLACK = (0, 0, 0)
NEST_COLOR = (150, 150, 100)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 0xE6)
WHITE = (255, 255, 255)
PURPLE = (0xE8, 0, 0xE8)


class Nest(pygame.sprite.Sprite):
    def __init__(self, nest_position_x, nest_position_y, color, antcolor):
        super().__init__()
        self.position_x = nest_position_x
        self.position_y = nest_position_y
        self.color = color
        self.image = pygame.Surface([nest_size, nest_size])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (
            self.position_x - nest_size // 2,
            self.position_y - nest_size // 2,
        )

        for i in range(ant_sum):
            ant = Ant(self.position_x, self.position_y, antcolor)
            ant_list.add(ant)
            all_list.add(ant)


class Ant(pygame.sprite.Sprite):
    def __init__(self, nest_position_x, nest_position_y, color):
        super().__init__()

        # init position (in nest)
        self.position_x = random.randint(
            nest_position_x - nest_size // 2, nest_position_x + nest_size // 2 - size
        )
        self.position_y = random.randint(
            nest_position_y - nest_size // 2, nest_position_y + nest_size // 2 - size
        )

        self.nest_position_x = nest_position_x
        self.nest_position_y = nest_position_y

        self.color = color
        self.search_color = color
        self.image = pygame.Surface([size, size])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.position_x, self.position_y)
        self.dx, self.dy = (0, 0)
        self.atan2 = 0
        self.clearPheromone = False
        self.maxPheroXY = None

        # health
        self.health = random.randint(1000, 1200)
        # state
        self.state = "search"

        self.type = random.randint(0, 1)

        if self.type == 1:
            if self.position_x > self.nest_position_x:
                if self.position_y > self.nest_position_y:
                    self.quad = (-1, -1)
                else:
                    self.quad = (-1, 1)
            else:
                if self.position_y > self.nest_position_y:
                    self.quad = (1, -1)
                else:
                    self.quad = (1, 1)

    def update(self):
        if self.health == 0 and self.state != "dead":
            self.color = BLACK
            self.image.fill(self.color)
            self.health = 20
            self.state = "dead"

        elif self.state == "search":

            if pygame.sprite.spritecollide(self, food_list, False):
                self.color = (255, 0, 255)
                self.image.fill(self.color)
                self.health += 100  # 先吃一點補體力
                self.state = "backhome"
                pheromap[self.position_x][self.position_y] += 50
                self.clearPheromone = False
            else:
                max_phero = (0, 0, 0)  # dx  # dy
                minRadian = 2 * math.pi
                for y in range(
                    max(0, self.position_y - 5),
                    min(window_height - 1, self.position_y + 6),
                ):
                    for x in range(
                        max(0, self.position_x - 5),
                        min(window_width - 1, self.position_x + 6),
                    ):
                        if (self.position_x, self.position_y) == (x, y):
                            continue
                        if pheromap[x][y] > max_phero[0]:
                            dx, dy = x - self.position_x, y - self.position_y
                            radian = math.atan2(dy, dx)
                            radian = abs(self.atan2 - radian) % (2 * math.pi)
                            if radian > math.pi:
                                radian = 2 * math.pi - radian
                            if radian < minRadian:
                                minRadian = radian
                                max_phero = (pheromap[x][y], dx, dy)
                if max_phero[0] > 0:
                    pheroXY = (
                        self.position_x + max_phero[1],
                        self.position_y + max_phero[2]
                    )
                    if self.maxPheroXY == pheroXY:
                        self.clearPheromone = not pygame.sprite.spritecollide(
                            self, nest_list, False
                        )
                        # if not self.clearPheromone:
                        #     self.atan2+=math.pi
                    if self.clearPheromone:
                        pheromap[pheroXY[0]][pheroXY[1]] = 0
                    self.move(
                        max_phero[1], max_phero[2], smooth=self.maxPheroXY!=pheroXY
                    )
                    self.maxPheroXY=pheroXY

                else:
                    self.clearPheromone = False
                    x = random.randint(-5, 5)
                    y = random.randint(-5, 5)

                    a = 4
                    if self.type == 1:
                        if self.quad[0] > 0:
                            x = random.randint(-5, a)
                        else:
                            x = random.randint(-a, 5)
                        if self.quad[1] > 0:
                            y = random.randint(-5, a)
                        else:
                            y = random.randint(-a, 5)

                    self.move(x, y)

                self.rect.topleft = (self.position_x, self.position_y)

            self.health -= 1

        elif self.state == "backhome":

            if pygame.sprite.spritecollide(self, nest_list, False):
                self.color = self.search_color
                self.image.fill(self.color)
                self.health = random.randint(1000, 1200)

                for i in range(1):
                    ant = Ant(
                        self.nest_position_x, self.nest_position_y, self.search_color
                    )
                    ant_list.add(ant)
                    all_list.add(ant)

                self.state = "search"
                # 補充食物到 window
                if random.randint(1, 10) >= 6:
                    food = Food(RED)
                    food_list.add(food)
                    all_list.add(food)

            x = self.nest_position_x - self.position_x
            y = self.nest_position_y - self.position_y
            nestDistance = math.sqrt(x * x + y * y)
            if nestDistance != 0:
                scale = backhome_speed / nestDistance
                self.move(x * scale, y * scale)
                self.rect.topleft = (self.position_x, self.position_y)
                self.health -= 1
                pheromap[self.position_x][self.position_y] += 50

        elif self.state == "dead":
            if self.health == 0:
                pygame.sprite.Sprite.kill(self)
            else:
                self.health -= 1

    def move(self, dx, dy, smooth=True):
        if smooth:
            self.dx = momentum * self.dx + (1 - momentum) * dx
            self.dy = momentum * self.dy + (1 - momentum) * dy
        else:
            self.dx = dx
            self.dy = dy
        self.position_x += round(self.dx)
        self.position_y += round(self.dy)
        self.position_x = min(max(0, self.position_x), window_width - size)
        self.position_y = min(max(0, self.position_y), window_height - size)
        self.atan2 = math.atan2(self.dy, self.dx)


class Food(pygame.sprite.Sprite):
    def __init__(self, color):
        super().__init__()
        x = random.randint(0, 159)
        y = random.randint(0, 119)

        # food position
        self.position_x = x
        self.position_y = y

        self.health = random.randint(1, 10)

        foodmap[x][y] += self.health

        self.color = color
        self.image = pygame.Surface([size, size])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.position_x * size, self.position_y * size)

    def update(self):
        if pygame.sprite.spritecollide(self, ant_list, False):
            self.health -= 1
            foodmap[self.position_x][self.position_y] -= 1
        if self.health == 0:
            pygame.sprite.Sprite.kill(self)
        else:
            self.image = pygame.Surface([self.health, self.health])
            self.image.fill(self.color)


def main():
    pygame.init()
    # load window surface
    window = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("bug nest")
    window.fill(WHITE)

    for i in range(food_sum):
        food = Food(RED)
        food_list.add(food)
        all_list.add(food)

    nest_position_x = 300  # random.randint(300,400)
    nest_position_y = 200  # random.randint(200,300)
    nest = Nest(nest_position_x, nest_position_y, NEST_COLOR, BLUE)
    nest_list.add(nest)
    #all_list.add(nest)

    nest_position_x = 600  # random.randint(500,600)
    nest_position_y = 400  # random.randint(300,400)
    nest = Nest(nest_position_x, nest_position_y, NEST_COLOR, GREEN)
    nest_list.add(nest)
    #all_list.add(nest)

    clock = pygame.time.Clock()

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        for i in range(window_width):
            for j in range(window_height):
                if pheromap[i][j] > 0:
                    pheromap[i][j] -= 1

        ant_list.update()
        food_list.update()
        # reflesh
        window.fill(WHITE)

        nest_list.draw(window)
        all_list.draw(window)

        pygame.display.update()


if __name__ == "__main__":
    main()
