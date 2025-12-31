"""
Aircraft class for Sky Fury - handles player aircraft with simplified physics
Adapted for left-to-right scrolling gameplay with runway takeoff
"""

import pygame
from pygame.math import Vector2
import math
import os

# Constants for simplified physics
GRAVITY = 0.3
GROUND_LEVEL = 500
RUNWAY_Y = GROUND_LEVEL
RUNWAY_X_START = 50
RUNWAY_X_END = 300
MIN_TAKEOFF_SPEED = 3.5  # Slightly higher speed to avoid vertical leap
MIN_TAKEOFF_ANGLE = 5.0  # Minimum angle for takeoff
MAX_LANDING_SPEED = 3.0
MAX_LANDING_ANGLE = 15.0

class Aircraft:
    """Player aircraft with simplified physics for arcade-style gameplay"""
    
    def __init__(self):
        # Position and movement
        self.position = Vector2(100, GROUND_LEVEL)  # Start on runway
        self.velocity = Vector2(0, 0)
        self.angle = 0  # Degrees, 0 = horizontal right
        
        # Flight state
        self.on_ground = True
        self.has_taken_off = False
        self.thrust = 0  # 0-100%
        
        # Control surfaces
        self.flaps = 0  # 0-3
        self.gear_down = True
        self.brakes_active = False
        self.spoilers_active = False
        
        # Resources
        self.health = 100
        self.max_health = 100
        self.fuel = 100
        self.max_fuel = 100
        self.shield_active = False
        self.shield_duration = 0
        
        # Combat attributes
        self.weapon_system = None  # Will be assigned externally
        self.score = 0
        self.lives = 3
        self.invulnerable = False
        self.invulnerable_timer = 0
        
        # Physics properties (simplified but more responsive)
        self.max_speed = 10.0  # Increased from 8.0
        self.acceleration_rate = 0.25  # Increased from 0.15 for better responsiveness
        self.drag = 0.97  # Slightly less drag
        self.lift_factor = 0.08  # More lift for better control
        
        # Sprite dimensions for better aircraft proportions (wider than tall)
        self.width = 160  # Horizontal dimension
        self.height = 90   # Vertical dimension
        self.size = self.width  # Keep for compatibility
        self.sprites = self._load_sprites()
        self.current_sprite = self.sprites["gear_down"]
    
    def _load_sprites(self):
        """Load aircraft sprites with fallback"""
        assets_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'images'))
        
        def try_load(filename, size):
            path = os.path.join(assets_dir, filename)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.scale(img, size)
                    # Flip horizontally so aircraft faces right (left to right direction)
                    img = pygame.transform.flip(img, True, False)
                    return img
                except:
                    pass
            # Fallback: create colored surface with arrow pointing right
            surf = pygame.Surface(size, pygame.SRCALPHA)
            # Draw a simple right-pointing aircraft shape
            pygame.draw.polygon(surf, (0, 150, 255), [
                (int(size[0] * 0.85), size[1] // 2),  # Nose (right)
                (int(size[0] * 0.15), int(size[1] * 0.3)),  # Top back
                (int(size[0] * 0.15), int(size[1] * 0.7))   # Bottom back
            ])
            return surf
        
        return {
            "gear_up": try_load("plane_gear_up.png", (self.width, self.height)),
            "gear_down": try_load("plane_gear_down.png", (self.width, int(self.height * 1.1))),
            "damaged": try_load("crash.png", (self.width, self.height))
        }
    
    def update(self, dt):
        """Update aircraft physics and state"""
        
        # Update invulnerability timer
        if self.invulnerable:
            self.invulnerable_timer -= dt
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
        
        # Update shield
        if self.shield_active:
            self.shield_duration -= dt
            # Drain energy while active
            if self.weapon_system:
                self.weapon_system.shield_energy -= 3 * dt
                if self.weapon_system.shield_energy < 0:
                    self.weapon_system.shield_energy = 0
            # Turn off if depleted or expired
            if self.shield_duration <= 0 or (self.weapon_system and self.weapon_system.shield_energy <= 0):
                self.shield_active = False
                self.shield_duration = 0
        
        if self.on_ground:
            self._update_ground_physics(dt)
        else:
            self._update_air_physics(dt)
        
        # Update fuel consumption
        if self.thrust > 0:
            self.fuel = max(0, self.fuel - self.thrust * 0.005 * dt)
            if self.fuel <= 0:
                self.thrust = 0
        
        # Choose correct sprite
        if self.health < 30:
            self.current_sprite = self.sprites["damaged"]
        elif self.gear_down:
            self.current_sprite = self.sprites["gear_down"]
        else:
            self.current_sprite = self.sprites["gear_up"]
    
    def _update_ground_physics(self, dt):
        """Physics while on the ground (runway)"""
        # Apply thrust for acceleration
        if self.thrust > 0:
            self.velocity.x += self.thrust * self.acceleration_rate * dt
        
        # Apply braking
        if self.brakes_active:
            self.velocity.x *= 0.95
        else:
            # Ground friction
            self.velocity.x *= self.drag
        
        # Limit speed on ground
        self.velocity.x = min(self.velocity.x, self.max_speed)
        
        # Update position
        self.position.x += self.velocity.x

        # Clamp ground pitch to [0, 25] for natural rotation
        self.angle = max(0, min(25, self.angle))
        
        # Natural takeoff: later rotation, modest angle, adequate speed
        if self.position.x >= 240 and self.velocity.x >= MIN_TAKEOFF_SPEED and self.angle >= 15:
            self.on_ground = False
            self.has_taken_off = True
            self.gear_down = False
            self.velocity.y = -2.2  # Softer initial climb
    
    def _update_air_physics(self, dt):
        """Physics while airborne"""
        # Thrust affects horizontal speed
        if self.thrust > 0 and self.fuel > 0:
            self.velocity.x += self.thrust * self.acceleration_rate * 0.5 * dt
        
        # Angle affects vertical speed (simplified lift)
        lift = math.sin(math.radians(self.angle)) * self.lift_factor * self.velocity.x
        self.velocity.y -= lift
        
        # Gravity
        self.velocity.y += GRAVITY * dt
        
        # Drag
        self.velocity.x *= self.drag if not self.spoilers_active else 0.96
        self.velocity.y *= 0.99
        
        # Flaps increase lift and drag
        if self.flaps > 0:
            self.velocity.y -= self.flaps * 0.02
            self.velocity.x *= 0.98
        
        # Spoilers reduce lift
        if self.spoilers_active:
            self.velocity.y += 0.1
        
        # Limit speeds
        self.velocity.x = min(self.velocity.x, self.max_speed)
        self.velocity.y = max(-5, min(5, self.velocity.y))
        
        # Update position
        self.position += self.velocity

        # Clamp airborne pitch to [-10, 30] to avoid overly vertical ascent
        self.angle = max(-10, min(30, self.angle))
        
        # After takeoff, constrain aircraft to left portion of screen (shmup-style camera)
        # This creates the effect of aircraft staying still while world scrolls
        if self.has_taken_off:
            # Keep aircraft in left 30% of screen horizontally
            self.position.x = max(50, min(250, self.position.x))
        else:
            # During takeoff, allow full horizontal movement
            self.position.x = max(20, min(780, self.position.x))
        
        # Vertical constraints
        self.position.y = max(20, min(580, self.position.y))
        
        # Check if landed
        if self.position.y >= GROUND_LEVEL:
            self._check_landing()
    
    def _check_landing(self):
        """Check landing conditions"""
        # Check if over runway
        if RUNWAY_X_START <= self.position.x <= RUNWAY_X_END:
            # Check landing speed and angle
            if abs(self.velocity.y) <= MAX_LANDING_SPEED and abs(self.angle) <= MAX_LANDING_ANGLE:
                # Successful landing
                self.land()
            else:
                # Crash landing
                self.crash()
        else:
            # Crashed outside runway
            self.crash()
    
    def land(self):
        """Successful landing"""
        self.on_ground = True
        self.velocity.y = 0
        self.position.y = GROUND_LEVEL
        self.gear_down = True
    
    def crash(self):
        """Aircraft crashed"""
        self.health = 0
    
    def take_damage(self, amount):
        """Take damage from enemy attacks"""
        # Skip if invulnerable from recent hit
        if self.invulnerable:
            return False
        
        # Reduce health directly
        self.health -= amount
        if self.health < 0:
            self.health = 0
        
        # Short invulnerability window to prevent instant death
        self.invulnerable = True
        self.invulnerable_timer = 0.2
        
        # Return True if dead
        return self.health <= 0
    
    def take_shield_hit(self, energy_cost):
        """Shield absorbs damage by consuming energy"""
        if not self.shield_active or not self.weapon_system:
            return
        
        # Reduce shield energy
        self.weapon_system.shield_energy -= energy_cost
        if self.weapon_system.shield_energy < 0:
            self.weapon_system.shield_energy = 0
        
        # Deactivate shield if depleted
        if self.weapon_system.shield_energy <= 0:
            self.shield_active = False
            self.shield_duration = 0
    
    def heal(self, amount):
        """Heal the aircraft"""
        self.health = min(self.max_health, self.health + amount)
    
    def add_fuel(self, amount):
        """Add fuel"""
        self.fuel = min(self.max_fuel, self.fuel + amount)
    
    def activate_shield(self, duration=5.0):
        """Activate shield for duration"""
        self.shield_active = True
        self.shield_duration = duration
    
    def add_score(self, points):
        """Add to score"""
        self.score += points
    
    def lose_life(self):
        """Lose a life"""
        self.lives -= 1
        if self.lives > 0:
            # Reset for respawn
            self.health = self.max_health
            self.position = Vector2(100, GROUND_LEVEL)
            self.velocity = Vector2(0, 0)
            self.angle = 0  # Reset angle to horizontal
            self.on_ground = True
            self.has_taken_off = False
            self.gear_down = True
            self.thrust = 0
            self.invulnerable = True
            self.invulnerable_timer = 2.0  # Reduced from 3.0 for better visibility
            # Reload sprites to fix vanishing plane bug
            self.sprites = self._load_sprites()
            self.current_sprite = self.sprites["gear_down"]
    
    def draw(self, screen):
        """Draw the aircraft"""
        # Simple flicker during invulnerability
        if self.invulnerable:
            # Flicker by checking game ticks
            if (pygame.time.get_ticks() // 100) % 2 == 0:
                return  # Skip drawing every other 100ms
        
        # Rotate sprite based on angle
        rotated = pygame.transform.rotate(self.current_sprite, self.angle)
        rect = rotated.get_rect(center=(int(self.position.x), int(self.position.y)))
        screen.blit(rotated, rect)
        
        # Draw shield if active
        if self.shield_active:
            shield_radius = self.size
            shield_surface = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
            alpha = int(100 + 50 * math.sin(pygame.time.get_ticks() * 0.01))
            pygame.draw.circle(shield_surface, (100, 150, 255, alpha), 
                             (shield_radius, shield_radius), shield_radius, 3)
            screen.blit(shield_surface, (int(self.position.x - shield_radius), 
                                        int(self.position.y - shield_radius)))
        
        # Draw health bar above aircraft
        if self.health < self.max_health:
            bar_width = 40
            bar_height = 4
            bar_x = int(self.position.x - bar_width / 2)
            bar_y = int(self.position.y - self.size - 10)
            
            # Background
            pygame.draw.rect(screen, (100, 100, 100), 
                           (bar_x, bar_y, bar_width, bar_height))
            # Health
            health_width = int(bar_width * (self.health / self.max_health))
            color = (0, 255, 0) if self.health > 50 else (255, 255, 0) if self.health > 25 else (255, 0, 0)
            pygame.draw.rect(screen, color, 
                           (bar_x, bar_y, health_width, bar_height))
    
    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.position.x - self.size/2, self.position.y - self.size/2,
                          self.size, self.size)
