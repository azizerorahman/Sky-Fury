"""
Custom Cursor System for Sky Fury
Creates a crosshair cursor for better game experience
"""

import pygame

class CustomCursor:
    """Custom crosshair cursor for the game"""
    
    def __init__(self):
        self.create_crosshair_cursor()
    
    def create_crosshair_cursor(self):
        """Create a crosshair cursor surface"""
        size = 32
        self.cursor_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw crosshair
        center = size // 2
        color = (0, 255, 100)  # Bright green
        thickness = 2
        gap = 4
        length = 10
        
        # Vertical line (top)
        pygame.draw.line(self.cursor_surface, color, 
                        (center, center - gap - length), 
                        (center, center - gap), thickness)
        # Vertical line (bottom)
        pygame.draw.line(self.cursor_surface, color, 
                        (center, center + gap), 
                        (center, center + gap + length), thickness)
        # Horizontal line (left)
        pygame.draw.line(self.cursor_surface, color, 
                        (center - gap - length, center), 
                        (center - gap, center), thickness)
        # Horizontal line (right)
        pygame.draw.line(self.cursor_surface, color, 
                        (center + gap, center), 
                        (center + gap + length, center), thickness)
        
        # Center dot
        pygame.draw.circle(self.cursor_surface, color, (center, center), 2)
        
        # Outer circle
        pygame.draw.circle(self.cursor_surface, color, (center, center), 12, 1)
    
    def draw(self, screen, pos):
        """Draw the custom cursor at the given position"""
        cursor_rect = self.cursor_surface.get_rect(center=pos)
        screen.blit(self.cursor_surface, cursor_rect)
