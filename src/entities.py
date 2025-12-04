import pygame
import random

class Bullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 4, y - 10, 8, 10)
        self.speed = -600  # px/s

    def update(self, dt):
        self.rect.y += self.speed * dt

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 220, 60), self.rect)

class Player:
    def __init__(self, x, y, screen_size):
        self.rect = pygame.Rect(x - 20, y - 20, 40, 40)
        self.speed = 300  # px/s
        self.cooldown = 0.12
        self._cd = 0.0
        self.screen_w, self.screen_h = screen_size
        self.health = 3

    def update(self, keys, dt):
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        if dx or dy:
            self.rect.x += int(dx * self.speed * dt)
            self.rect.y += int(dy * self.speed * dt)

        # Clamp to screen
        self.rect.x = max(0, min(self.rect.x, self.screen_w - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, self.screen_h - self.rect.height))

        # cooldown tick
        if self._cd > 0:
            self._cd = max(0.0, self._cd - dt)

    def shoot(self):
        if self._cd <= 0:
            self._cd = self.cooldown
            return Bullet(self.rect.centerx, self.rect.top)
        return None

    def draw(self, surface):
        # simple triangle placeholder ship
        cx, cy = self.rect.center
        points = [(cx, self.rect.top), (self.rect.left, self.rect.bottom), (self.rect.right, self.rect.bottom)]
        pygame.draw.polygon(surface, (40, 160, 220), points)

class Enemy:
    def __init__(self, screen_w):
        w = 36
        h = 28
        x = random.randint(0, max(0, screen_w - w))
        self.rect = pygame.Rect(x, -h, w, h)
        self.speed = random.uniform(60, 160)
        self.health = 1

    def update(self, dt):
        self.rect.y += int(self.speed * dt)

    def draw(self, surface):
        pygame.draw.rect(surface, (200, 60, 60), self.rect)
