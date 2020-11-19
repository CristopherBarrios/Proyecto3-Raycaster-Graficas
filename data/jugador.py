#Cristopher Jose Rodolfo Barrios Solis
#18207
from data.mapa import WORLD_WALLS
from data.configuracion import *
import pygame
import math

class JUUGADOR:
    def __init__(self, sprites):
        self.x, self.y = PLAYER_POSITION
        self.angle = PLAYER_ANGLE
        self.sensitivity = PLAYER_SENSITIVITY
        self.sprites = sprites
        self.side = 50
        self.rect = pygame.Rect(*PLAYER_POSITION, self.side, self.side)
        self.shot = False
    @property
    def collision_list(self):
        return WORLD_WALLS + [
            pygame.Rect(*obj.position, obj.side, obj.side)
            for obj in self.sprites.list_of_objects
            if obj.blocked
        ]
    def mouse_control(self):
        if pygame.mouse.get_focused():
            difference = pygame.mouse.get_pos()[0] - HALF_WIDTH
            pygame.mouse.set_pos([HALF_WIDTH, HALF_HEIGHT])
            self.angle += difference * self.sensitivity
    def movement(self):
        self.keys_control()
        self.mouse_control()
        self.rect.center = self.x, self.y
        self.angle %= 2 * math.pi
    @property
    def position(self):
        return (self.x, self.y)
    def keys_control(self):
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            exit()
        if keys[pygame.K_w]:
            dx, dy = PLAYER_SPEED * cos_a, PLAYER_SPEED * sin_a
            self.find_collision(dx, dy)
        if keys[pygame.K_s]:
            dx, dy = -PLAYER_SPEED * cos_a, -PLAYER_SPEED * sin_a
            self.find_collision(dx, dy)
        if keys[pygame.K_a]:
            dx, dy = PLAYER_SPEED * sin_a, -PLAYER_SPEED * cos_a
            self.find_collision(dx, dy)
        if keys[pygame.K_d]:
            dx, dy = -PLAYER_SPEED * sin_a, PLAYER_SPEED * cos_a
            self.find_collision(dx, dy)
        if keys[pygame.K_LEFT]:
            self.angle -= PLAYER_ROTATION_SPEED
        if keys[pygame.K_RIGHT]:
            self.angle += PLAYER_ROTATION_SPEED
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not self.shot:
                    self.shot = True
    def find_collision(self, dx, dy):
        next_rect = self.rect.copy()
        next_rect.move_ip(dx, dy)
        hit_indexes = next_rect.collidelistall(self.collision_list)
        if len(hit_indexes):
            delta_x, delta_y = 0, 0
            for hit_index in hit_indexes:
                hit_rect = self.collision_list[hit_index]
                if dx > 0:
                    delta_x += next_rect.right - hit_rect.left
                else:
                    delta_x += hit_rect.right - next_rect.left
                if dy > 0:
                    delta_y += next_rect.bottom - hit_rect.top
                else:
                    delta_y += hit_rect.bottom - next_rect.top
            if abs(delta_x - delta_y) < 20:
                dx, dy = 0, 0
            elif delta_x > delta_y:
                dy = 0
            elif delta_x < delta_y:
                dx = 0
        self.x += dx
        self.y += dy
