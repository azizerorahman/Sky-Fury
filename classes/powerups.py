"""
Power-Up System for Sky Fury
Collectible power-ups that drop from enemies
"""

import pygame
from pygame.math import Vector2
import random
import os

class PowerUp:
    """Collectible power-up"""
    
    def __init__(self, position, powerup_type):
        self.position = Vector2(position)
        self.type = powerup_type
        self.active = True
        self.lifetime = 8.0  # Disappears after 8 seconds
        
        # Movement
        self.velocity = Vector2(-1, 0)  # Drifts left slowly
        self.float_offset = 0
        self.float_speed = 3.0
        
        # Visual
        self.size = 25
        self.sprite = self._load_sprite()
        self.glow_alpha = 0
    
    def _load_sprite(self):
        """Load power-up sprite"""
        assets_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'assets'))
        
        # Try to load appropriate sprite
        sprite_files = {
            "health": "shield.png",
            "weapon_upgrade": "laserGreen.png",
            "missiles": "laserRed.png",
            "shield": "shield2.png",
            "score": "destruction.png"
        }
        
        filename = sprite_files.get(self.type, "shield.png")
        path = os.path.join(assets_dir, 'images', filename)
        
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (self.size, self.size))
            except:
                pass
        
        # Fallback - colored squares
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        colors = {
            "health": (0, 255, 0),
            "weapon_upgrade": (255, 255, 0),
            "missiles": (255, 100, 0),
            "shield": (100, 150, 255),
            "score": (255, 215, 0)
        }
        color = colors.get(self.type, (255, 255, 255))
        pygame.draw.circle(surf, color, (self.size//2, self.size//2), self.size//2)
        return surf
    
    def update(self, dt):
        """Update power-up"""
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.active = False
            return
        
        # Drift movement
        self.position += self.velocity * dt * 60
        
        # Floating animation
        self.float_offset += self.float_speed * dt
        
        # Pulsing glow
        self.glow_alpha = int(100 + 100 * abs(pygame.math.Vector2(1, 0).rotate(self.float_offset * 50).x))
        
        # Deactivate if off screen
        if self.position.x < -50:
            self.active = False
    
    def draw(self, screen):
        """Draw power-up"""
        if not self.active:
            return
        
        # Calculate float position
        float_y = self.position.y + pygame.math.Vector2(0, 10).rotate(self.float_offset * 50).y
        
        # Draw glow
        glow_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (255, 255, 255, min(self.glow_alpha, 100)), 
                          (self.size, self.size), self.size)
        screen.blit(glow_surface, (int(self.position.x - self.size), int(float_y - self.size)))
        
        # Draw sprite
        rect = self.sprite.get_rect(center=(int(self.position.x), int(float_y)))
        screen.blit(self.sprite, rect)
        
        # Draw type indicator
        font = pygame.font.SysFont('Arial', 10, bold=True)
        labels = {
            "health": "HP",
            "weapon_upgrade": "PWR",
            "missiles": "MSL",
            "shield": "SHD",
            "score": "PTS"
        }
        text = font.render(labels.get(self.type, "?"), True, (255, 255, 255))
        text_rect = text.get_rect(center=(int(self.position.x), int(float_y + self.size/2 + 10)))
        screen.blit(text, text_rect)
    
    def get_rect(self):
        """Get collision rect"""
        return pygame.Rect(self.position.x - self.size/2, self.position.y - self.size/2,
                          self.size, self.size)
    
    def apply_effect(self, aircraft):
        """Apply power-up effect to aircraft"""
        if self.type == "health":
            aircraft.heal(30)
            return "+30 Health!"
        
        elif self.type == "weapon_upgrade":
            if aircraft.weapon_system.upgrade_primary():
                return "Weapon Upgraded!"
            else:
                aircraft.add_score(500)
                return "+500 Points!"
        
        elif self.type == "missiles":
            aircraft.weapon_system.add_missiles(3)
            return "+3 Missiles!"
        
        elif self.type == "shield":
            aircraft.weapon_system.shield_energy = aircraft.weapon_system.max_shield_energy
            aircraft.activate_shield(5.0)
            return "Shield Activated!"
        
        elif self.type == "score":
            points = random.choice([500, 1000, 2000])
            aircraft.add_score(points)
            return f"+{points} Points!"
        
        return "Power-Up!"


class PowerUpManager:
    """Manages all power-ups"""
    
    def __init__(self):
        self.powerups = []
    
    def spawn_powerup(self, position, powerup_type=None):
        """Spawn a power-up at position"""
        if powerup_type is None:
            # Random power-up
            types = ["health", "weapon_upgrade", "missiles", "shield", "score"]
            weights = [30, 20, 25, 15, 10]  # Health and missiles more common
            powerup_type = random.choices(types, weights=weights)[0]
        
        powerup = PowerUp(position, powerup_type)
        self.powerups.append(powerup)
    
    def maybe_spawn_from_enemy(self, enemy_position):
        """Maybe spawn a power-up when enemy is destroyed"""
        if random.random() < 0.3:  # 30% chance
            self.spawn_powerup(enemy_position)
    
    def maybe_spawn_from_boss(self, boss_position):
        """Spawn multiple power-ups from boss"""
        # Guaranteed spawns from boss
        for _ in range(random.randint(3, 5)):
            offset = Vector2(random.uniform(-50, 50), random.uniform(-50, 50))
            self.spawn_powerup(boss_position + offset)
    
    def update(self, dt):
        """Update all power-ups"""
        for powerup in self.powerups[:]:
            powerup.update(dt)
            if not powerup.active:
                self.powerups.remove(powerup)
    
    def draw(self, screen):
        """Draw all power-ups"""
        for powerup in self.powerups:
            powerup.draw(screen)
    
    def check_collection(self, aircraft):
        """Check if aircraft collected any power-ups"""
        messages = []
        aircraft_rect = aircraft.get_rect()
        
        for powerup in self.powerups[:]:
            if powerup.active and aircraft_rect.colliderect(powerup.get_rect()):
                message = powerup.apply_effect(aircraft)
                messages.append(message)
                powerup.active = False
                self.powerups.remove(powerup)
        
        return messages
