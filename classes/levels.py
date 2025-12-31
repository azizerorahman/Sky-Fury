"""
Level Management System for Sky Fury
Defines all 3 levels with waves, enemies, and bosses
"""

import pygame
from pygame.math import Vector2
import random
import os

class LevelManager:
    """Manages game levels and progression"""
    
    def __init__(self, level=1):
        self.current_level = level
        self.max_levels = 3
        self.current_wave = 0
        self.wave_complete = False
        self.level_complete = False
        
        # Background
        self.background_surface = None
        self.scroll_x = 0
        self.scroll_speed = 1.0
        
        # Load backgrounds
        self._load_backgrounds()
        
        # Load the specified level
        self.load_level(level)
    
    def _load_backgrounds(self):
        """Load parallax backgrounds with realistic depth"""
        assets_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'images'))
        
        # Parallax speeds inspired by flight simulator - slower for distant, faster for near
        # Layers 0-15, where 0 is furthest (slowest) and 15 is nearest (fastest)
        parallax_speeds = [0.1, 0.14, 0.25, 0.27, 0.30, 0.35, 0.4, 0.45, 
                          0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.80, 0.85]
        
        # Vertical offset for each layer to create depth
        vertical_offsets = [230, 169, 150, 98, 90, 50, 50, 30, 30, 30, 5, 24, 5, 0, 0, -3]
        
        # Create layered background
        self.bg_layers = []
        
        # Load parallax layers from back to front
        for i in range(16):
            path = os.path.join(assets_dir, f'pixel_parallax_{i}.png')
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    # Scale for 1000px width screen (slight increase)
                    scale = 0.35  # Slightly larger scale for better coverage
                    new_width = int(img.get_width() * scale)
                    new_height = int(img.get_height() * scale)
                    img = pygame.transform.scale(img, (new_width, new_height))
                    
                    # Store with individual speed and offset
                    self.bg_layers.append({
                        'image': img,
                        'x': 0,
                        'speed': parallax_speeds[i],
                        'y_offset': vertical_offsets[i],
                        'layer_index': i
                    })
                except Exception as e:
                    print(f"Warning: Could not load parallax layer {i}: {e}")
        
        # Fallback if no backgrounds loaded
        if not self.bg_layers:
            surf = pygame.Surface((1000, 600))
            surf.fill((135, 206, 235))  # Sky blue
            self.bg_layers.append({'image': surf, 'x': 0, 'speed': 0.5, 'y_offset': 0, 'layer_index': 0})
    
    def load_level(self, level_num):
        """Load a specific level"""
        self.current_level = level_num
        self.current_wave = 0  # Start at wave 0
        self.wave_complete = False  # Don't start as complete
        self.level_complete = False
        self.scroll_x = 0
        self.waves_started = False  # Track if waves have been initiated
        
        return self.get_level_data(level_num)
    
    def update(self, dt, aircraft, enemy_manager):
        """Update level state and spawn enemies"""
        # Update background scroll
        self.scroll_x += self.scroll_speed * dt * 60
        self.update_background(dt)
        
        # Don't spawn enemies until aircraft has taken off
        if not aircraft.has_taken_off:
            return
        
        # Get current level data
        level_data = self.get_level_data(self.current_level)
        
        # Start first wave immediately after takeoff
        if aircraft.has_taken_off and not self.waves_started:
            self.waves_started = True
            if self.current_wave < len(level_data['waves']):
                wave = level_data['waves'][self.current_wave]
                enemy_manager.set_spawn_queue(wave['enemies'])
                enemy_manager.spawn_delay = wave.get('delay', 0.8)  # Faster spawning
        
        # Check if all waves completed
        if self.current_wave >= len(level_data['waves']):
            # Check if boss should spawn
            if not enemy_manager.boss and not hasattr(enemy_manager, 'boss_defeated'):
                # Spawn boss
                enemy_manager.spawn_boss(level_data['boss'])
            elif not enemy_manager.boss and hasattr(enemy_manager, 'boss_defeated') and enemy_manager.boss_defeated:
                # Level complete
                self.level_complete = True
            return
        
        # Check if current wave is complete (all enemies defeated and spawn queue empty)
        if enemy_manager.is_wave_complete():
            self.current_wave += 1
            
            # Spawn next wave
            if self.current_wave < len(level_data['waves']):
                wave = level_data['waves'][self.current_wave]
                # Set spawn queue with wave enemies
                enemy_manager.set_spawn_queue(wave['enemies'])
                enemy_manager.spawn_delay = wave.get('delay', 0.8)  # Faster spawning
    
    def get_level_data(self, level_num):
        """Get level configuration"""
        if level_num == 1:
            return self._level_1_data()
        elif level_num == 2:
            return self._level_2_data()
        elif level_num == 3:
            return self._level_3_data()
        else:
            return self._level_1_data()
    
    def _level_1_data(self):
        """Level 1: Drone Scramble (Easy)"""
        return {
            'name': "Level 1: Drone Scramble",
            'difficulty': "Easy",
            'description': "Basic combat training. Eliminate enemy drones.",
            'boss': "hive_queen",
            'waves': [
                # Wave 1 - Introduction
                {
                    'enemies': [
                        {'type': 'drone', 'y': 150},
                        {'type': 'drone', 'y': 250},
                        {'type': 'drone', 'y': 350},
                        {'type': 'drone', 'y': 450},
                    ],
                    'delay': 1.5
                },
                # Wave 2 - More drones
                {
                    'enemies': [
                        {'type': 'drone', 'y': 100},
                        {'type': 'drone', 'y': 200},
                        {'type': 'drone', 'y': 300},
                        {'type': 'drone', 'y': 400},
                        {'type': 'drone', 'y': 500},
                    ],
                    'delay': 1.2
                },
                # Wave 3 - Introduce bombers
                {
                    'enemies': [
                        {'type': 'drone', 'y': 150},
                        {'type': 'bomber', 'y': 250},
                        {'type': 'drone', 'y': 350},
                        {'type': 'bomber', 'y': 450},
                    ],
                    'delay': 1.5
                },
                # Wave 4 - Mixed
                {
                    'enemies': [
                        {'type': 'drone', 'y': 100},
                        {'type': 'drone', 'y': 200},
                        {'type': 'bomber', 'y': 300},
                        {'type': 'drone', 'y': 400},
                        {'type': 'bomber', 'y': 500},
                        {'type': 'drone', 'y': 250},
                    ],
                    'delay': 1.0
                },
                # Wave 5 - Final wave before boss
                {
                    'enemies': [
                        {'type': 'bomber', 'y': 150},
                        {'type': 'drone', 'y': 200},
                        {'type': 'drone', 'y': 300},
                        {'type': 'bomber', 'y': 400},
                        {'type': 'drone', 'y': 450},
                    ],
                    'delay': 1.2
                }
            ]
        }
    
    def _level_2_data(self):
        """Level 2: Stormfront Assault (Medium)"""
        return {
            'name': "Level 2: Stormfront Assault",
            'difficulty': "Medium",
            'description': "Enemy reinforcements incoming with gunship support.",
            'boss': "aegis_defender",
            'waves': [
                # Wave 1 - Immediate pressure
                {
                    'enemies': [
                        {'type': 'drone', 'y': 120},
                        {'type': 'bomber', 'y': 220},
                        {'type': 'gunship', 'y': 300},
                        {'type': 'bomber', 'y': 380},
                        {'type': 'drone', 'y': 480},
                    ],
                    'delay': 1.2
                },
                # Wave 2 - Gunship focus
                {
                    'enemies': [
                        {'type': 'gunship', 'y': 150},
                        {'type': 'drone', 'y': 250},
                        {'type': 'gunship', 'y': 350},
                        {'type': 'drone', 'y': 450},
                    ],
                    'delay': 1.5
                },
                # Wave 3 - Elite enemies
                {
                    'enemies': [
                        {'type': 'elite', 'y': 200},
                        {'type': 'bomber', 'y': 300},
                        {'type': 'elite', 'y': 400},
                        {'type': 'gunship', 'y': 250},
                        {'type': 'gunship', 'y': 350},
                    ],
                    'delay': 1.3
                },
                # Wave 4 - Heavy assault
                {
                    'enemies': [
                        {'type': 'drone', 'y': 100},
                        {'type': 'elite', 'y': 180},
                        {'type': 'bomber', 'y': 260},
                        {'type': 'gunship', 'y': 340},
                        {'type': 'elite', 'y': 420},
                        {'type': 'drone', 'y': 500},
                    ],
                    'delay': 1.0
                },
                # Wave 5 - Kamikaze introduction
                {
                    'enemies': [
                        {'type': 'kamikaze', 'y': 150},
                        {'type': 'kamikaze', 'y': 250},
                        {'type': 'elite', 'y': 300},
                        {'type': 'kamikaze', 'y': 350},
                        {'type': 'kamikaze', 'y': 450},
                    ],
                    'delay': 1.1
                },
                # Wave 6 - Final assault
                {
                    'enemies': [
                        {'type': 'elite', 'y': 120},
                        {'type': 'gunship', 'y': 200},
                        {'type': 'bomber', 'y': 280},
                        {'type': 'gunship', 'y': 360},
                        {'type': 'elite', 'y': 440},
                    ],
                    'delay': 1.2
                }
            ]
        }
    
    def _level_3_data(self):
        """Level 3: Final Showdown (Hard)"""
        return {
            'name': "Level 3: Final Showdown",
            'difficulty': "Hard",
            'description': "The enemy's ultimate weapon approaches. Survive at all costs!",
            'boss': "final_destroyer",
            'waves': [
                # Wave 1 - Chaos
                {
                    'enemies': [
                        {'type': 'kamikaze', 'y': 100},
                        {'type': 'elite', 'y': 180},
                        {'type': 'gunship', 'y': 260},
                        {'type': 'kamikaze', 'y': 340},
                        {'type': 'elite', 'y': 420},
                        {'type': 'kamikaze', 'y': 500},
                    ],
                    'delay': 0.9
                },
                # Wave 2 - Elite squadron
                {
                    'enemies': [
                        {'type': 'elite', 'y': 150},
                        {'type': 'elite', 'y': 250},
                        {'type': 'elite', 'y': 350},
                        {'type': 'elite', 'y': 450},
                    ],
                    'delay': 1.3
                },
                # Wave 3 - Mixed assault
                {
                    'enemies': [
                        {'type': 'bomber', 'y': 120},
                        {'type': 'gunship', 'y': 200},
                        {'type': 'elite', 'y': 280},
                        {'type': 'gunship', 'y': 360},
                        {'type': 'bomber', 'y': 440},
                        {'type': 'kamikaze', 'y': 300},
                    ],
                    'delay': 0.8
                },
                # Wave 4 - Kamikaze swarm
                {
                    'enemies': [
                        {'type': 'kamikaze', 'y': 150},
                        {'type': 'kamikaze', 'y': 200},
                        {'type': 'elite', 'y': 250},
                        {'type': 'kamikaze', 'y': 300},
                        {'type': 'kamikaze', 'y': 350},
                        {'type': 'elite', 'y': 400},
                        {'type': 'kamikaze', 'y': 450},
                    ],
                    'delay': 0.7
                },
                # Wave 5 - Everything
                {
                    'enemies': [
                        {'type': 'elite', 'y': 100},
                        {'type': 'gunship', 'y': 170},
                        {'type': 'bomber', 'y': 240},
                        {'type': 'kamikaze', 'y': 280},
                        {'type': 'elite', 'y': 340},
                        {'type': 'gunship', 'y': 410},
                        {'type': 'kamikaze', 'y': 480},
                    ],
                    'delay': 0.9
                },
                # Wave 6 - Final wave
                {
                    'enemies': [
                        {'type': 'elite', 'y': 150},
                        {'type': 'elite', 'y': 250},
                        {'type': 'gunship', 'y': 200},
                        {'type': 'gunship', 'y': 350},
                        {'type': 'bomber', 'y': 300},
                        {'type': 'kamikaze', 'y': 400},
                    ],
                    'delay': 1.0
                },
                # Wave 7 - Last stand
                {
                    'enemies': [
                        {'type': 'elite', 'y': 180},
                        {'type': 'elite', 'y': 280},
                        {'type': 'elite', 'y': 380},
                        {'type': 'kamikaze', 'y': 230},
                        {'type': 'kamikaze', 'y': 330},
                    ],
                    'delay': 1.0
                }
            ]
        }
    
    def update_background(self, dt):
        """Update scrolling background"""
        for layer in self.bg_layers:
            layer['x'] -= layer['speed'] * dt * 60
            # Wrap around
            if layer['x'] <= -layer['image'].get_width():
                layer['x'] = 0
    
    def draw_background(self, screen, aircraft=None):
        """Draw the scrolling parallax background with depth"""
        # Fill with sky color first
        screen.fill((135, 206, 235))
        
        for layer in self.bg_layers:
            # Calculate y position with vertical offset for depth
            y_pos = layer['y_offset']
            
            # Draw multiple copies for seamless scrolling
            x_offset = layer['x']
            img_width = layer['image'].get_width()
            
            # Draw enough copies to cover screen
            copies_needed = 3  # Draw 3 copies to ensure coverage
            for i in range(copies_needed):
                x_pos = x_offset + (i * img_width)
                screen.blit(layer['image'], (x_pos, y_pos))
        
        # Draw runway only if aircraft hasn't taken off yet
        if aircraft and not aircraft.has_taken_off:
            self._draw_runway(screen)
    
    def _draw_runway(self, screen):
        """Draw the runway at the start - updated for 1000px width"""
        # Ground
        pygame.draw.rect(screen, (100, 80, 60), (0, 500, 1000, 100))
        
        # Runway - wider for new screen
        pygame.draw.rect(screen, (50, 50, 50), (50, 500, 400, 20))
        
        # Runway markings
        for i in range(8):
            x = 70 + i * 45
            pygame.draw.rect(screen, (255, 255, 255), (x, 505, 20, 10))
    
    def draw_level_info(self, screen):
        """Draw level information overlay"""
        font_title = pygame.font.SysFont('Arial', 32, bold=True)
        font_info = pygame.font.SysFont('Arial', 18)
        
        level_data = self.get_level_data(self.current_level)
        
        # Semi-transparent background
        overlay = pygame.Surface((400, 120), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (200, 50))
        
        # Level name
        title = font_title.render(level_data['name'], True, (255, 255, 100))
        screen.blit(title, (210, 60))
        
        # Difficulty
        diff_color = (0, 255, 0) if level_data['difficulty'] == "Easy" else \
                     (255, 255, 0) if level_data['difficulty'] == "Medium" else \
                     (255, 100, 100)
        difficulty = font_info.render(f"Difficulty: {level_data['difficulty']}", True, diff_color)
        screen.blit(difficulty, (210, 100))
        
        # Description
        desc = font_info.render(level_data['description'], True, (200, 200, 200))
        screen.blit(desc, (210, 125))
