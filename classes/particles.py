"""
Enhanced Particle System for Sky Fury
"""

import pygame
from pygame.math import Vector2
import random
import math

class Particle:
    """Single particle"""
    
    def __init__(self, position, velocity, color, size, lifetime):
        self.position = Vector2(position)
        self.velocity = Vector2(velocity)
        self.color = color
        self.size = size
        self.initial_size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.active = True
    
    def update(self, dt):
        """Update particle"""
        self.position += self.velocity * dt * 60
        self.lifetime -= dt
        
        if self.lifetime <= 0:
            self.active = False
        
        # Shrink over time
        self.size = self.initial_size * (self.lifetime / self.max_lifetime)
    
    def draw(self, screen):
        """Draw particle"""
        if self.size > 0.5:
            pygame.draw.circle(screen, self.color, 
                             (int(self.position.x), int(self.position.y)), 
                             int(self.size))


class ParticleSystem:
    """Manages all particle effects"""
    
    def __init__(self):
        self.particles = []
    
    def update(self, dt):
        """Update all particles"""
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.active:
                self.particles.remove(particle)
    
    def draw(self, screen):
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(screen)
    
    def create_explosion(self, position, size=25, count=50, colors=None):
        """Create explosion effect - enhanced for better visibility"""
        if colors is None:
            colors = [(255, 220, 100), (255, 180, 80), (255, 120, 60), (220, 100, 100), (255, 80, 40)]
        
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 12)  # Faster particles
            velocity = Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
            
            color = random.choice(colors)
            particle_size = random.uniform(size * 0.8, size * 2.0)  # Larger particles
            lifetime = random.uniform(0.5, 1.5)  # Longer lifetime
            
            self.particles.append(Particle(position, velocity, color, particle_size, lifetime))
    
    def create_hit_effect(self, position):
        """Create hit sparkles - enhanced"""
        colors = [(255, 255, 150), (255, 220, 120), (255, 180, 80)]
        self.create_explosion(position, size=8, count=20, colors=colors)
    
    def create_shield_hit(self, position):
        """Create shield impact effect - enhanced"""
        colors = [(120, 180, 255), (170, 220, 255), (220, 240, 255)]
        
        for _ in range(25):  # More particles
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(5, 15)  # Faster
            velocity = Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
            
            color = random.choice(colors)
            size = random.uniform(3, 8)  # Larger
            lifetime = random.uniform(0.3, 0.7)  # Longer
            
            self.particles.append(Particle(position, velocity, color, size, lifetime))
    
    def create_engine_trail(self, position, direction_angle, thrust):
        """Create engine exhaust"""
        if thrust <= 0:
            return
        
        count = max(1, int(thrust / 25))
        
        for _ in range(count):
            # Particles go opposite direction
            angle_offset = random.uniform(-20, 20)
            angle = direction_angle + 180 + angle_offset
            speed = random.uniform(1, 3)
            
            rad = math.radians(angle)
            velocity = Vector2(math.cos(rad) * speed, -math.sin(rad) * speed)
            
            # Color based on thrust
            red = min(255, 200 + int(thrust * 0.5))
            green = min(255, 100 + int(thrust * 0.3))
            blue = 50
            color = (red, green, blue)
            
            size = random.uniform(2, 4)
            lifetime = random.uniform(0.2, 0.4)
            
            self.particles.append(Particle(position, velocity, color, size, lifetime))
    
    def create_powerup_collect(self, position):
        """Create power-up collection effect"""
        colors = [(255, 255, 100), (100, 255, 255), (255, 100, 255)]
        
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 8)
            velocity = Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
            
            color = random.choice(colors)
            size = random.uniform(3, 6)
            lifetime = random.uniform(0.4, 0.8)
            
            self.particles.append(Particle(position, velocity, color, size, lifetime))
    
    def create_damage_smoke(self, position):
        """Create damage smoke trail"""
        if random.random() < 0.3:  # Don't create every frame
            gray = random.randint(80, 120)
            color = (gray, gray, gray)
            
            velocity = Vector2(random.uniform(-1, 1), random.uniform(-2, -1))
            size = random.uniform(3, 6)
            lifetime = random.uniform(0.8, 1.5)
            
            self.particles.append(Particle(position, velocity, color, size, lifetime))

    # Compatibility wrapper used by sky_fury.py
    def add_particles(self, x, y, particle_type='explosion', **kwargs):
        """Generic particle entry point.
        Provides a simple API used throughout the game code.
        
        Parameters
        - x, y: coordinates
        - particle_type: 'explosion' | 'hit' | 'shield' | 'engine' | 'smoke'
        - kwargs: optional parameters depending on type
          - explosion: size (int), count (int), colors (list)
          - engine: direction_angle (deg), thrust (0-100)
        """
        position = Vector2(x, y)
        ptype = (particle_type or 'explosion').lower()

        if ptype == 'explosion':
            size = kwargs.get('size', 20)
            count = kwargs.get('count', 10)
            colors = kwargs.get('colors', None)
            self.create_explosion(position, size=size, count=count, colors=colors)
        elif ptype == 'hit':
            self.create_hit_effect(position)
        elif ptype == 'shield':
            self.create_shield_hit(position)
        elif ptype == 'engine':
            direction_angle = kwargs.get('direction_angle', 180)
            thrust = kwargs.get('thrust', 50)
            self.create_engine_trail(position, direction_angle, thrust)
        elif ptype == 'smoke':
            self.create_damage_smoke(position)
        else:
            # Fallback to a small explosion
            self.create_explosion(position, size=15, count=8)
