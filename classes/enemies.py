"""
Enemy and Boss System for Sky Fury
Includes all enemy types and boss encounters for 3 levels
"""

import pygame
from pygame.math import Vector2
import math
import random
import os

# Enemy projectile class
class EnemyProjectile:
    """Projectile fired by enemies"""
    
    def __init__(self, position, velocity):
        self.position = Vector2(position)
        self.velocity = Vector2(velocity)
        self.damage = 8  # Reduced from 15 for easier gameplay
        self.active = True
        
        # Sprite - larger and brighter for better visibility
        self.sprite = pygame.Surface((14, 14), pygame.SRCALPHA)
        self.sprite.fill((255, 80, 80))  # Brighter red
    
    def update(self, dt):
        self.position += self.velocity * dt * 60
        
        # Deactivate if off screen
        if (self.position.x < -50 or self.position.x > 850 or 
            self.position.y < -50 or self.position.y > 650):
            self.active = False
    
    def draw(self, screen):
        rect = self.sprite.get_rect(center=(int(self.position.x), int(self.position.y)))
        screen.blit(self.sprite, rect)
    
    def get_rect(self):
        return pygame.Rect(self.position.x - 7, self.position.y - 7, 14, 14)


class Enemy:
    """Base enemy class with different types"""
    
    def __init__(self, position, enemy_type="drone"):
        self.position = Vector2(position)
        self.type = enemy_type
        self.active = True
        self.state = "spawn"
        
        # Set stats based on type
        self.health, self.max_health, self.speed, self.damage, self.score_value = self._get_stats()
        
        # Movement
        self.velocity = Vector2(-self.speed, 0)  # Move left
        self.move_timer = 0
        self.attack_cooldown = 0
        
        # Load sprite (increased size for better visibility)
        self.size = 80 if enemy_type != "kamikaze" else 70
        self.sprite = self._load_sprite()
    
    def _get_stats(self):
        """Get stats based on enemy type"""
        stats = {
            "drone": (30, 30, 2.0, 10, 100),
            "bomber": (60, 60, 1.5, 15, 200),
            "gunship": (100, 100, 1.8, 20, 300),
            "elite": (150, 150, 2.2, 25, 400),
            "kamikaze": (20, 20, 4.0, 40, 150)
        }
        return stats.get(self.type, (30, 30, 2.0, 10, 100))
    
    def _load_sprite(self):
        """Load enemy sprite"""
        assets_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'assets'))
        
        # Map enemy types to new sprite files
        sprite_map = {
            "drone": "enemy-1.png",
            "bomber": "enemy-2.png",
            "gunship": "enemy-3.png",
            "elite": "enemy-4.png",
            "kamikaze": "enemy-1.png"
        }
        
        filename = sprite_map.get(self.type, "enemy-1.png")
        path = os.path.join(assets_dir, 'images', filename)
        
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (self.size, self.size))
            except:
                pass
        
        # Fallback
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        colors = {
            "drone": (255, 100, 100),
            "bomber": (100, 100, 255),
            "gunship": (100, 255, 100),
            "elite": (255, 100, 255),
            "kamikaze": (255, 50, 50)
        }
        surf.fill(colors.get(self.type, (200, 200, 200)))
        return surf
    
    def update(self, dt, player_pos):
        """Update enemy behavior"""
        if not self.active:
            return []
        
        self.move_timer += dt
        self.attack_cooldown = max(0, self.attack_cooldown - dt)
        
        # State machine
        if self.state == "spawn":
            self.state = "move"
        
        # Movement patterns
        projectiles = []
        if self.type == "drone":
            projectiles = self._update_drone(dt, player_pos)
        elif self.type == "bomber":
            projectiles = self._update_bomber(dt, player_pos)
        elif self.type == "gunship":
            projectiles = self._update_gunship(dt, player_pos)
        elif self.type == "elite":
            projectiles = self._update_elite(dt, player_pos)
        elif self.type == "kamikaze":
            self._update_kamikaze(dt, player_pos)
        
        # Deactivate if off screen (left side)
        if self.position.x < -100:
            self.active = False
        
        return projectiles
    
    def _update_drone(self, dt, player_pos):
        """Simple straight movement, occasional shots"""
        self.position += self.velocity * dt * 60
        
        # Slight wave pattern
        self.position.y += math.sin(self.move_timer * 2) * 1.5
        
        # Shoot occasionally
        if self.attack_cooldown <= 0 and 50 < self.position.x < 750:
            if random.random() < 0.02:
                self.attack_cooldown = 2.0
                return [EnemyProjectile(self.position, Vector2(-5, 0))]
        return []
    
    def _update_bomber(self, dt, player_pos):
        """Slow movement, drops bombs toward player"""
        self.position += self.velocity * dt * 60
        
        # Gentle sine wave
        self.position.y += math.sin(self.move_timer * 1.5) * 0.8
        
        # Drop bombs when above player
        if self.attack_cooldown <= 0 and 50 < self.position.x < 750:
            if abs(self.position.x - player_pos.x) < 100:
                self.attack_cooldown = 2.5
                # Drop bomb downward
                return [EnemyProjectile(self.position, Vector2(-2, 3))]
        return []
    
    def _update_gunship(self, dt, player_pos):
        """Tries to match player Y, fires aimed shots"""
        self.position.x += self.velocity.x * dt * 60
        
        # Move toward player's Y position
        if abs(self.position.y - player_pos.y) > 5:
            dir_y = 1 if player_pos.y > self.position.y else -1
            self.position.y += dir_y * 1.5
        
        # Aimed shots
        if self.attack_cooldown <= 0 and 100 < self.position.x < 700:
            if random.random() < 0.03:
                self.attack_cooldown = 1.8
                # Aim at player
                direction = (player_pos - self.position).normalize()
                return [EnemyProjectile(self.position, direction * 4)]
        return []
    
    def _update_elite(self, dt, player_pos):
        """Advanced movement, rapid fire"""
        self.position.x += self.velocity.x * dt * 60
        
        # Complex movement pattern
        self.position.y += math.sin(self.move_timer * 3) * 2 + math.cos(self.move_timer * 1.5) * 1
        
        # Rapid fire
        if self.attack_cooldown <= 0 and 100 < self.position.x < 700:
            if random.random() < 0.04:
                self.attack_cooldown = 1.2
                # Triple shot spread
                projectiles = []
                for angle in [-15, 0, 15]:
                    rad = math.radians(angle + 180)  # Shoot left
                    vel = Vector2(math.cos(rad) * 5, math.sin(rad) * 5)
                    projectiles.append(EnemyProjectile(self.position, vel))
                return projectiles
        return []
    
    def _update_kamikaze(self, dt, player_pos):
        """Rushes toward player"""
        # Move toward player
        direction = (player_pos - self.position)
        if direction.length() > 0:
            direction = direction.normalize()
            self.position += direction * self.speed * dt * 60
    
    def take_damage(self, amount):
        """Take damage"""
        self.health -= amount
        if self.health <= 0:
            self.active = False
            return True
        return False
    
    def draw(self, screen):
        """Draw enemy"""
        if not self.active:
            return
        
        # Draw sprite
        rect = self.sprite.get_rect(center=(int(self.position.x), int(self.position.y)))
        screen.blit(self.sprite, rect)
        
        # Draw health bar if damaged
        if self.health < self.max_health:
            bar_width = 30
            bar_height = 3
            bar_x = int(self.position.x - bar_width / 2)
            bar_y = int(self.position.y - self.size / 2 - 8)
            
            pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
            health_width = int(bar_width * (self.health / self.max_health))
            pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, health_width, bar_height))
    
    def get_rect(self):
        """Get collision rect"""
        return pygame.Rect(self.position.x - self.size/2, self.position.y - self.size/2,
                          self.size, self.size)


class Boss:
    """Boss enemy with multiple phases"""
    
    def __init__(self, position, boss_type="hive_queen"):
        self.position = Vector2(position)
        self.type = boss_type
        self.active = True
        self.phase = 1
        
        # Stats based on boss type - much larger for epic feel
        if boss_type == "hive_queen":
            self.max_health = 800
            self.size = 300  # 2x size for screen recording
            self.score_value = 5000
        elif boss_type == "aegis_defender":
            self.max_health = 1200
            self.size = 360  # 2x size for screen recording
            self.score_value = 8000
        else:  # final_destroyer
            self.max_health = 1800
            self.size = 440  # 2x size for screen recording
            self.score_value = 15000
        
        self.health = self.max_health
        
        # Movement
        self.velocity = Vector2(0, 0)
        self.move_timer = 0
        self.attack_timer = 0
        self.phase_transition_timer = 0
        
        # Load sprite
        self.sprite = self._load_sprite()
        
        # Entry animation
        self.entered = False
        self.entry_target_x = 650
    
    def _load_sprite(self):
        """Load boss sprite"""
        assets_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'assets'))
        
        # Map boss types to sprite files
        sprite_map = {
            "hive_queen": "enemy-2.png",      # Boss 1
            "aegis_defender": "enemy-3.png",  # Boss 2
            "final_destroyer": "enemy-4.png"  # Boss 3
        }
        
        filename = sprite_map.get(self.type, "enemy-4.png")
        path = os.path.join(assets_dir, 'images', filename)
        
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (self.size, self.size))
            except:
                pass
        
        # Fallback
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(surf, (200, 50, 200), (self.size//2, self.size//2), self.size//2)
        return surf
    
    def update(self, dt, player_pos):
        """Update boss behavior"""
        if not self.active:
            return []
        
        self.move_timer += dt
        self.attack_timer += dt
        
        projectiles = []
        
        # Entry animation
        if not self.entered:
            if self.position.x > self.entry_target_x:
                self.position.x -= 3
            else:
                self.entered = True
        else:
            # Check phase transitions
            health_percent = self.health / self.max_health
            if health_percent <= 0.66 and self.phase == 1:
                self.phase = 2
                self.phase_transition_timer = 2.0
            elif health_percent <= 0.33 and self.phase == 2:
                self.phase = 3
                self.phase_transition_timer = 2.0
            
            # Phase transition invulnerability
            if self.phase_transition_timer > 0:
                self.phase_transition_timer -= dt
            else:
                # Attack patterns based on boss type and phase
                if self.type == "hive_queen":
                    projectiles = self._hive_queen_attack(dt, player_pos)
                elif self.type == "aegis_defender":
                    projectiles = self._aegis_defender_attack(dt, player_pos)
                else:  # final_destroyer
                    projectiles = self._final_destroyer_attack(dt, player_pos)
                
                # Movement pattern
                self._update_movement(dt, player_pos)
        
        return projectiles
    
    def _update_movement(self, dt, player_pos):
        """Boss movement pattern"""
        # Vertical sine wave
        amplitude = 100
        frequency = 0.5
        center_y = 300
        self.position.y = center_y + math.sin(self.move_timer * frequency) * amplitude
        
        # Keep on screen
        self.position.y = max(100, min(500, self.position.y))
    
    def _hive_queen_attack(self, dt, player_pos):
        """Hive Queen boss attacks"""
        projectiles = []
        
        if self.phase == 1:
            # Spread shot
            if self.attack_timer >= 2.0:
                self.attack_timer = 0
                for i in range(5):
                    angle = 180 + (i - 2) * 20
                    rad = math.radians(angle)
                    vel = Vector2(math.cos(rad) * 4, math.sin(rad) * 4)
                    projectiles.append(EnemyProjectile(self.position, vel))
        
        elif self.phase == 2:
            # Faster spread shot + aimed
            if self.attack_timer >= 1.5:
                self.attack_timer = 0
                for i in range(7):
                    angle = 180 + (i - 3) * 15
                    rad = math.radians(angle)
                    vel = Vector2(math.cos(rad) * 5, math.sin(rad) * 5)
                    projectiles.append(EnemyProjectile(self.position, vel))
                
                # Aimed shot
                direction = (player_pos - self.position).normalize()
                projectiles.append(EnemyProjectile(self.position, direction * 6))
        
        else:  # Phase 3
            # Spiral pattern
            if self.attack_timer >= 0.1:
                self.attack_timer = 0
                angle = (self.move_timer * 200) % 360
                rad = math.radians(angle)
                vel = Vector2(math.cos(rad) * 5, math.sin(rad) * 5)
                projectiles.append(EnemyProjectile(self.position, vel))
        
        return projectiles
    
    def _aegis_defender_attack(self, dt, player_pos):
        """Aegis Defender boss attacks"""
        projectiles = []
        
        if self.phase == 1:
            # Aimed rapid fire
            if self.attack_timer >= 0.5:
                self.attack_timer = 0
                direction = (player_pos - self.position).normalize()
                projectiles.append(EnemyProjectile(self.position, direction * 5))
        
        elif self.phase == 2:
            # Aimed rapid fire + side waves
            if self.attack_timer >= 0.4:
                self.attack_timer = 0
                direction = (player_pos - self.position).normalize()
                projectiles.append(EnemyProjectile(self.position, direction * 6))
                
                # Side waves
                for angle in [90, 270]:
                    rad = math.radians(angle)
                    vel = Vector2(math.cos(rad) * 4, math.sin(rad) * 4)
                    projectiles.append(EnemyProjectile(self.position, vel))
        
        else:  # Phase 3
            # Laser barrage
            if self.attack_timer >= 0.15:
                self.attack_timer = 0
                for i in range(3):
                    angle = 180 + (i - 1) * 10
                    rad = math.radians(angle)
                    vel = Vector2(math.cos(rad) * 7, math.sin(rad) * 7)
                    projectiles.append(EnemyProjectile(self.position, vel))
        
        return projectiles
    
    def _final_destroyer_attack(self, dt, player_pos):
        """Final Destroyer boss attacks - most difficult"""
        projectiles = []
        
        if self.phase == 1:
            # Ring burst
            if self.attack_timer >= 1.5:
                self.attack_timer = 0
                for i in range(12):
                    angle = i * 30
                    rad = math.radians(angle)
                    vel = Vector2(math.cos(rad) * 4, math.sin(rad) * 4)
                    projectiles.append(EnemyProjectile(self.position, vel))
        
        elif self.phase == 2:
            # Double ring burst
            if self.attack_timer >= 1.2:
                self.attack_timer = 0
                for i in range(16):
                    angle = i * 22.5
                    rad = math.radians(angle)
                    vel = Vector2(math.cos(rad) * 5, math.sin(rad) * 5)
                    projectiles.append(EnemyProjectile(self.position, vel))
        
        else:  # Phase 3
            # Continuous spiral + aimed
            if self.attack_timer >= 0.08:
                self.attack_timer = 0
                angle = (self.move_timer * 300) % 360
                rad = math.radians(angle)
                vel = Vector2(math.cos(rad) * 6, math.sin(rad) * 6)
                projectiles.append(EnemyProjectile(self.position, vel))
                
                # Occasional aimed shot
                if random.random() < 0.1:
                    direction = (player_pos - self.position).normalize()
                    projectiles.append(EnemyProjectile(self.position, direction * 8))
        
        return projectiles
    
    def take_damage(self, amount):
        """Take damage (ignores during phase transition)"""
        if self.phase_transition_timer > 0:
            return False
        
        self.health -= amount
        if self.health <= 0:
            self.active = False
            return True
        return False
    
    def draw(self, screen):
        """Draw boss"""
        if not self.active:
            return
        
        # Flash during phase transition
        if self.phase_transition_timer > 0 and int(self.phase_transition_timer * 10) % 2 == 0:
            return
        
        # Draw sprite
        rect = self.sprite.get_rect(center=(int(self.position.x), int(self.position.y)))
        screen.blit(self.sprite, rect)
        
        # Draw health bar
        bar_width = 200
        bar_height = 15
        bar_x = int(screen.get_width() / 2 - bar_width / 2)
        bar_y = 30
        
        # Background
        pygame.draw.rect(screen, (50, 50, 50), (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4))
        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
        
        # Health
        health_width = int(bar_width * (self.health / self.max_health))
        color = (255, 0, 0) if self.phase == 3 else (255, 100, 0) if self.phase == 2 else (255, 200, 0)
        pygame.draw.rect(screen, color, (bar_x, bar_y, health_width, bar_height))
        
        # Phase indicator
        font = pygame.font.SysFont('Arial', 14, bold=True)
        phase_text = font.render(f"PHASE {self.phase}/3", True, (255, 255, 255))
        screen.blit(phase_text, (bar_x + bar_width + 10, bar_y))
    
    def get_rect(self):
        """Get collision rect"""
        return pygame.Rect(self.position.x - self.size/2, self.position.y - self.size/2,
                          self.size, self.size)


class EnemyManager:
    """Manages all enemies and spawning"""
    
    def __init__(self):
        self.enemies = []
        self.boss = None
        self.projectiles = []
        
        self.spawn_timer = 0
        self.spawn_delay = 2.0
        self.spawn_queue = []
    
    def set_spawn_queue(self, queue):
        """Set the queue of enemies to spawn"""
        self.spawn_queue = queue
        self.spawn_timer = 0
    
    def spawn_boss(self, boss_type):
        """Spawn a boss"""
        self.boss = Boss(Vector2(900, 300), boss_type)
        self.enemies.clear()  # Clear regular enemies
    
    def update(self, dt, player_pos, missiles):
        """Update all enemies"""
        # Update spawn timer
        self.spawn_timer += dt
        
        # Spawn from queue
        if self.spawn_queue and self.spawn_timer >= self.spawn_delay:
            self.spawn_timer = 0
            enemy_data = self.spawn_queue.pop(0)
            enemy = Enemy(Vector2(850, enemy_data['y']), enemy_data['type'])
            self.enemies.append(enemy)
        
        # Update enemies
        for enemy in self.enemies[:]:
            new_projectiles = enemy.update(dt, player_pos)
            self.projectiles.extend(new_projectiles)
            if not enemy.active:
                self.enemies.remove(enemy)
        
        # Update boss
        if self.boss:
            new_projectiles = self.boss.update(dt, player_pos)
            self.projectiles.extend(new_projectiles)
            if not self.boss.active:
                self.boss = None
        
        # Update homing missiles' targets
        for missile in missiles:
            if missile.active:
                missile.update(dt, self.enemies + ([self.boss] if self.boss else []))
        
        # Update projectiles
        for proj in self.projectiles[:]:
            proj.update(dt)
            if not proj.active:
                self.projectiles.remove(proj)
    
    def draw(self, screen):
        """Draw all enemies"""
        for enemy in self.enemies:
            enemy.draw(screen)
        
        if self.boss:
            self.boss.draw(screen)
        
        for proj in self.projectiles:
            proj.draw(screen)
    
    def is_wave_complete(self):
        """Check if current wave is complete"""
        return len(self.enemies) == 0 and len(self.spawn_queue) == 0 and not self.boss
