"""
Weapon System for Sky Fury
Includes all weapon types: primary guns, homing missiles, plasma laser, and shield
"""

import pygame
from pygame.math import Vector2
import math
import random
import os

class Bullet:
    """Standard bullet projectile"""
    
    def __init__(self, position, direction_angle, speed=15):
        self.position = Vector2(position)
        self.angle = direction_angle
        self.speed = speed
        self.damage = 15
        self.active = True
        
        # Calculate velocity from angle (0° = right, positive = counterclockwise)
        rad = math.radians(direction_angle)
        self.velocity = Vector2(math.cos(rad) * speed, -math.sin(rad) * speed)
        
        # Load sprite
        self.sprite = self._load_sprite()
    
    def _load_sprite(self):
        """Load bullet sprite with fallback"""
        assets_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'assets'))
        path = os.path.join(assets_dir, 'images', 'laserGreen.png')
        
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (35, 12))  # Larger bullets
            except:
                pass
        
        # Fallback - brighter and larger
        surf = pygame.Surface((35, 12), pygame.SRCALPHA)
        surf.fill((0, 255, 100))  # Bright green
        return surf
    
    def update(self, dt):
        """Update bullet position"""
        self.position += self.velocity * dt * 60
        
        # Deactivate if off screen
        if (self.position.x < -50 or self.position.x > 850 or 
            self.position.y < -50 or self.position.y > 650):
            self.active = False
    
    def draw(self, screen):
        """Draw the bullet"""
        rotated = pygame.transform.rotate(self.sprite, -self.angle)
        rect = rotated.get_rect(center=(int(self.position.x), int(self.position.y)))
        screen.blit(rotated, rect)
    
    def get_rect(self):
        """Get collision rect"""
        return pygame.Rect(self.position.x - 4, self.position.y - 4, 8, 8)


class HomingMissile:
    """Homing missile that tracks enemies"""
    
    def __init__(self, position):
        self.position = Vector2(position)
        self.velocity = Vector2(10, 0)  # Initial velocity to the right
        self.angle = 0
        self.target = None
        self.damage = 40
        self.active = True
        self.lifetime = 6.0
        self.turn_rate = 3.0  # Degrees per frame
        
        # Load sprite
        self.sprite = self._load_sprite()
    
    def _load_sprite(self):
        """Load missile sprite with fallback"""
        assets_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'assets'))
        path = os.path.join(assets_dir, 'images', 'laserRed.png')
        
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (50, 18))  # Larger missiles
            except:
                pass
        
        # Fallback - brighter and larger
        surf = pygame.Surface((50, 18), pygame.SRCALPHA)
        surf.fill((255, 50, 50))  # Bright red
        return surf
    
    def update(self, dt, enemies):
        """Update missile with homing behavior"""
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.active = False
            return
        
        # Find or update target
        if not self.target or not self.target.active:
            self.target = self._find_nearest_enemy(enemies)
        
        # Home in on target
        if self.target and self.target.active:
            # Calculate direction to target
            target_dir = self.target.position - self.position
            if target_dir.length() > 0:
                target_angle = math.degrees(math.atan2(-target_dir.y, target_dir.x))
                
                # Turn toward target
                angle_diff = target_angle - self.angle
                # Normalize to -180 to 180
                while angle_diff > 180:
                    angle_diff -= 360
                while angle_diff < -180:
                    angle_diff += 360
                
                # Apply turn rate
                if abs(angle_diff) < self.turn_rate:
                    self.angle = target_angle
                else:
                    self.angle += self.turn_rate if angle_diff > 0 else -self.turn_rate
        
        # Update velocity from angle
        rad = math.radians(self.angle)
        speed = 12
        self.velocity = Vector2(math.cos(rad) * speed, -math.sin(rad) * speed)
        
        # Update position
        self.position += self.velocity * dt * 60
        
        # Deactivate if off screen
        if (self.position.x < -50 or self.position.x > 850 or 
            self.position.y < -50 or self.position.y > 650):
            self.active = False
    
    def _find_nearest_enemy(self, enemies):
        """Find the nearest enemy"""
        nearest = None
        min_dist = float('inf')
        
        for enemy in enemies:
            if enemy.active:
                dist = (enemy.position - self.position).length()
                if dist < min_dist:
                    min_dist = dist
                    nearest = enemy
        
        return nearest
    
    def draw(self, screen):
        """Draw the missile"""
        rotated = pygame.transform.rotate(self.sprite, -self.angle)
        rect = rotated.get_rect(center=(int(self.position.x), int(self.position.y)))
        screen.blit(rotated, rect)
        
        # Draw exhaust trail
        for i in range(3):
            offset = Vector2(-15 - i * 5, 0).rotate(-self.angle)
            pos = self.position + offset
            color = (255, 200 - i * 50, 100 - i * 30)
            pygame.draw.circle(screen, color, (int(pos.x), int(pos.y)), 3 - i)
    
    def get_rect(self):
        """Get collision rect"""
        return pygame.Rect(self.position.x - 6, self.position.y - 6, 12, 12)


class PlasmaLaser:
    """Powerful plasma laser beam"""
    
    def __init__(self, position, charge_level):
        self.position = Vector2(position)
        self.charge = min(100, charge_level)
        self.angle = 0  # Fires to the right
        self.damage = self.charge * 0.8  # Damage based on charge
        self.width = 10 + self.charge * 0.15
        self.active = True
        self.lifetime = 0.6
        self.alpha = 255
    
    def update(self, dt):
        """Update laser"""
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.active = False
        
        # Fade out near end
        self.alpha = int(255 * (self.lifetime / 0.6))
    
    def draw(self, screen):
        """Draw the laser beam"""
        # Beam extends to the right edge
        start_pos = self.position
        end_pos = Vector2(850, self.position.y)
        
        # Draw multiple layers for glow effect
        for i in range(3):
            width = int(self.width * (3 - i) * 0.6)
            alpha = max(0, min(255, self.alpha // (i + 1)))
            
            # Create surface for this layer
            surf = pygame.Surface((850, 600), pygame.SRCALPHA)
            
            if i == 0:
                color = (100, 200, 255, alpha)
            elif i == 1:
                color = (150, 220, 255, alpha // 2)
            else:
                color = (200, 240, 255, alpha // 3)
            
            pygame.draw.line(surf, color, start_pos, end_pos, width)
            screen.blit(surf, (0, 0))
    
    def get_damage_at_position(self, pos):
        """Check if position is hit by laser"""
        if abs(pos.y - self.position.y) < self.width / 2 and pos.x > self.position.x:
            return self.damage * 0.02  # Damage per frame
        return 0


class WeaponSystem:
    """Manages all weapon systems for the aircraft"""
    
    def __init__(self, aircraft):
        self.aircraft = aircraft
        
        # Weapon levels and ammo
        self.primary_level = 1  # 1=single, 2=double, 3=triple spread
        self.missile_count = 5
        self.max_missiles = 10
        self.laser_charge = 0
        self.max_laser_charge = 100
        self.shield_energy = 50
        self.max_shield_energy = 100
        
        # Charging state
        self.is_charging_laser = False
        
        # Cooldowns (in seconds)
        self.cooldowns = {
            'primary': 0,
            'missile': 0,
            'laser': 0,
            'shield': 0
        }
        
        self.cooldown_times = {
            'primary': 0.15,
            'missile': 1.5,
            'laser': 3.0,
            'shield': 8.0
        }
        
        # Active projectiles
        self.bullets = []
        self.missiles = []
        self.lasers = []
    
    def update(self, dt):
        """Update all weapons and projectiles"""
        # Update cooldowns
        for key in self.cooldowns:
            if self.cooldowns[key] > 0:
                self.cooldowns[key] = max(0, self.cooldowns[key] - dt)
        
        # Update laser charging
        if self.is_charging_laser and self.laser_charge < self.max_laser_charge:
            self.laser_charge = min(self.max_laser_charge, self.laser_charge + 40 * dt)
        
        # Slowly regenerate laser charge
        if not self.is_charging_laser and self.laser_charge < self.max_laser_charge:
            self.laser_charge = min(self.max_laser_charge, self.laser_charge + 5 * dt)
        
        # Slowly regenerate shield energy
        if self.shield_energy < self.max_shield_energy:
            self.shield_energy = min(self.max_shield_energy, self.shield_energy + 3 * dt)
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update(dt)
            if not bullet.active:
                self.bullets.remove(bullet)
        
        # Update missiles (pass enemies for homing)
        for missile in self.missiles[:]:
            # We'll pass enemies from collision detection
            missile.update(dt, [])
            if not missile.active:
                self.missiles.remove(missile)
        
        # Update lasers
        for laser in self.lasers[:]:
            laser.update(dt)
            if not laser.active:
                self.lasers.remove(laser)
    
    def fire_primary(self):
        """Fire primary weapon"""
        if self.cooldowns['primary'] > 0:
            return False
        
        self.cooldowns['primary'] = self.cooldown_times['primary']
        
        # Create bullets based on level
        if self.primary_level == 1:
            # Single bullet forward
            bullet = Bullet(self.aircraft.position, 0)
            self.bullets.append(bullet)
        
        elif self.primary_level == 2:
            # Double bullets
            offset_up = Vector2(0, -10)
            offset_down = Vector2(0, 10)
            bullet1 = Bullet(self.aircraft.position + offset_up, 0)
            bullet2 = Bullet(self.aircraft.position + offset_down, 0)
            self.bullets.extend([bullet1, bullet2])
        
        elif self.primary_level >= 3:
            # Triple spread
            bullet1 = Bullet(self.aircraft.position, 0)
            bullet2 = Bullet(self.aircraft.position, 15)
            bullet3 = Bullet(self.aircraft.position, -15)
            self.bullets.extend([bullet1, bullet2, bullet3])
        
        return True
    
    def fire_missile(self):
        """Fire homing missile"""
        if self.cooldowns['missile'] > 0 or self.missile_count <= 0:
            return False
        
        self.cooldowns['missile'] = self.cooldown_times['missile']
        self.missile_count -= 1
        
        missile = HomingMissile(self.aircraft.position)
        self.missiles.append(missile)
        return True
    
    def fire_laser(self):
        """Fire plasma laser (requires charge)"""
        if self.cooldowns['laser'] > 0 or self.laser_charge < 30:
            return False
        
        self.cooldowns['laser'] = self.cooldown_times['laser']
        
        laser = PlasmaLaser(self.aircraft.position, self.laser_charge)
        self.lasers.append(laser)
        
        # Consume charge
        self.laser_charge = 0
        self.is_charging_laser = False
        
        return True
    
    def activate_shield(self):
        """Activate shield"""
        if self.cooldowns['shield'] > 0 or self.shield_energy < 40:
            return False
        
        self.cooldowns['shield'] = self.cooldown_times['shield']
        self.shield_energy -= 40
        
        self.aircraft.activate_shield(5.0)
        return True
    
    def upgrade_primary(self):
        """Upgrade primary weapon"""
        if self.primary_level < 3:
            self.primary_level += 1
            return True
        return False
    
    def add_missiles(self, count):
        """Add missiles"""
        self.missile_count = min(self.max_missiles, self.missile_count + count)
    
    def draw(self, screen):
        """Draw all active projectiles"""
        for laser in self.lasers:
            laser.draw(screen)
        
        for bullet in self.bullets:
            bullet.draw(screen)
        
        for missile in self.missiles:
            missile.draw(screen)
