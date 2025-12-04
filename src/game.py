import pygame
import time
from entities import Player, Bullet, Enemy

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.clock = pygame.time.Clock()
        self.running = True
        self.player = Player(self.width // 2, self.height - 70, (self.width, self.height))
        self.bullets = []
        self.enemies = []
        self.spawn_timer = 0.0
        self.score = 0

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            keys = pygame.key.get_pressed()

            # update player
            self.player.update(keys, dt)

            # shooting
            if keys[pygame.K_SPACE]:
                b = self.player.shoot()
                if b:
                    self.bullets.append(b)

            # update bullets
            for b in list(self.bullets):
                b.update(dt)
                if b.rect.bottom < 0:
                    self.bullets.remove(b)

            # spawn enemies periodically
            self.spawn_timer += dt
            if self.spawn_timer > 0.8:
                self.spawn_timer = 0.0
                self.enemies.append(Enemy(self.width))

            # update enemies
            for e in list(self.enemies):
                e.update(dt)
                if e.rect.top > self.height:
                    self.enemies.remove(e)

            # collisions: bullets vs enemies
            for b in list(self.bullets):
                for e in list(self.enemies):
                    if b.rect.colliderect(e.rect):
                        try:
                            self.bullets.remove(b)
                        except ValueError:
                            pass
                        try:
                            self.enemies.remove(e)
                        except ValueError:
                            pass
                        self.score += 10
                        break

            # draw
            self.screen.fill((135, 206, 235))  # sky blue

            # draw HUD
            self._draw_hud()

            # draw entities
            for b in self.bullets:
                b.draw(self.screen)
            for e in self.enemies:
                e.draw(self.screen)

            self.player.draw(self.screen)

            pygame.display.flip()

    def _draw_hud(self):
        font = pygame.font.SysFont(None, 24)
        score_surf = font.render(f"Score: {self.score}", True, (20, 20, 20))
        self.screen.blit(score_surf, (8, 8))

        hs_surf = font.render("High: --", True, (20, 20, 20))
        self.screen.blit(hs_surf, (self.width - 100, 8))

        # health
        for i in range(self.player.health):
            pygame.draw.rect(self.screen, (220, 30, 30), pygame.Rect(8 + i * 18, self.height - 22, 14, 14))
