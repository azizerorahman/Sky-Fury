"""
User Interface System for Sky Fury
Includes HUD, menus, and all UI elements
"""

import pygame
import json
import os

class UserInterface:
    """Manages all UI elements"""
    
    def __init__(self):
        pygame.font.init()
        
        # Professional font families with fallbacks
        font_families = ['Segoe UI', 'Tahoma', 'Verdana', 'Arial', 'sans-serif']
        
        # Try to load the best available font
        self.font_huge = self._load_best_font(font_families, 68, bold=True)  # Menu titles
        self.font_large = pygame.font.SysFont(font_families, 38, bold=True)  # Score
        self.font_medium = pygame.font.SysFont(font_families, 26, bold=True)  # Lives, weapons
        self.font_small = pygame.font.SysFont(font_families, 22, bold=False)  # General UI
        self.font_tiny = pygame.font.SysFont(font_families, 16, bold=False)  # Labels
        
        # Colors - enhanced palette
        self.white = (255, 255, 255)
        self.yellow = (255, 240, 100)
        self.gold = (255, 215, 0)
        self.red = (255, 90, 90)
        self.green = (100, 255, 120)
        self.blue = (100, 180, 255)
        self.cyan = (0, 255, 255)
        self.gray = (160, 160, 160)
        self.dark_gray = (60, 60, 60)
        
        # Messages
        self.messages = []
        
        # High score
        self.high_score = self._load_high_score()
        
        # Load menu background
        self.menu_background = self._load_menu_background()
    
    def _load_best_font(self, families, size, bold=False):
        """Load the first available font from the family list"""
        return pygame.font.SysFont(families, size, bold=bold)
    
    def _draw_text_with_shadow(self, surface, text, font, color, x, y, center=False, shadow_offset=2):
        """Draw text with shadow for better readability"""
        # Render shadow
        shadow = font.render(text, True, (0, 0, 0))
        shadow_rect = shadow.get_rect()
        if center:
            shadow_rect.center = (x + shadow_offset, y + shadow_offset)
        else:
            shadow_rect.topleft = (x + shadow_offset, y + shadow_offset)
        surface.blit(shadow, shadow_rect)
        
        # Render main text
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        surface.blit(text_surface, text_rect)
        
        return text_rect
    
    def _load_high_score(self):
        """Load high score from file"""
        try:
            if os.path.exists('highscore.json'):
                with open('highscore.json', 'r') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
        except:
            pass
        return 0
    
    def save_high_score(self, score):
        """Save high score to file"""
        if score > self.high_score:
            self.high_score = score
            try:
                with open('highscore.json', 'w') as f:
                    json.dump({'high_score': score}, f)
            except:
                pass
    
    def _load_menu_background(self):
        """Load menu background image or create gradient"""
        assets_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'images'))
        candidate_files = ['menu_bg.jpg', 'menu_background.png']
        
        for filename in candidate_files:
            try:
                path = os.path.join(assets_dir, filename)
                if os.path.exists(path):
                    img = pygame.image.load(path)
                    # Scale to screen size (1000x600)
                    return pygame.transform.scale(img, (1000, 600))
            except Exception:
                continue
        
        # Create gradient background as fallback - centered with sky colors
        bg = pygame.Surface((1000, 600))
        # Sky blue gradient (top to bottom)
        for y in range(600):
            # Brighter blue at top, darker at bottom
            ratio = y / 600
            r = int(70 + ratio * 30)
            g = int(130 + ratio * 80)
            b = int(180 - ratio * 50)
            pygame.draw.line(bg, (r, g, b), (0, y), (1000, y))
        return bg
    
    def show_message(self, text, duration=2.0):
        """Add a temporary message"""
        self.messages.append({
            'text': text,
            'duration': duration,
            'timer': duration
        })
    
    def update_messages(self, dt):
        """Update message timers"""
        for msg in self.messages[:]:
            msg['timer'] -= dt
            if msg['timer'] <= 0:
                self.messages.remove(msg)
    
    def draw_messages(self, screen):
        """Draw temporary messages with shadow"""
        y_offset = 150
        for msg in self.messages:
            alpha = min(255, int(255 * msg['timer'] / msg['duration']))
            
            # Background box
            text_surf = self.font_medium.render(msg['text'], True, self.gold)
            bg_surf = pygame.Surface((text_surf.get_width() + 40, text_surf.get_height() + 20), pygame.SRCALPHA)
            bg_surf.fill((0, 0, 0, int(alpha * 0.7)))
            bg_rect = bg_surf.get_rect(center=(500, y_offset))
            screen.blit(bg_surf, bg_rect)
            
            # Text with shadow
            self._draw_text_with_shadow(screen, msg['text'], self.font_medium, self.gold, 500, y_offset, center=True, shadow_offset=2)
            
            y_offset += 60
    
    def draw_menu(self, screen):
        """Draw main menu with background"""
        # Draw background with 70% opacity
        bg_copy = self.menu_background.copy()
        bg_copy.set_alpha(int(255 * 0.7))
        screen.blit(bg_copy, (0, 0))
        
        # Semi-transparent overlay for text readability
        overlay = pygame.Surface((1000, 600), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))
        screen.blit(overlay, (0, 0))
        
        # Title
        title = self.font_huge.render("SKY FURY", True, self.yellow)
        title_rect = title.get_rect(center=(500, 120))
        screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.font_medium.render("Flight Combat Simulator", True, self.white)
        subtitle_rect = subtitle.get_rect(center=(500, 180))
        screen.blit(subtitle, subtitle_rect)
        
        # Instructions
        instructions = [
            "Arrow Keys: Move Aircraft",
            "SPACE: Fire Primary Weapon",
            "E: Fire Homing Missile",
            "R (Hold): Charge Plasma Laser",
            "F: Activate Shield",
            "",
            "Press ENTER to Start"
        ]
        
        y = 280
        for line in instructions:
            if line:
                self._draw_text_with_shadow(screen, line, self.font_small, self.white, 500, y, center=True, shadow_offset=1)
            y += 35
        
        # High score
        self._draw_text_with_shadow(screen, f"High Score: {self.high_score}", self.font_small, self.gold, 20, 560, center=False, shadow_offset=1)
        
        # Credits
        self._draw_text_with_shadow(screen, "© 2025 Sky Fury", self.font_tiny, self.gray, 500, 580, center=True, shadow_offset=1)
    
    def draw_level_select(self, screen, unlocked_levels=3):
        """Draw level selection screen"""
        # Draw background with 70% opacity
        bg_copy = self.menu_background.copy()
        bg_copy.set_alpha(int(255 * 0.7))
        screen.blit(bg_copy, (0, 0))
        
        # Semi-transparent overlay for text readability
        overlay = pygame.Surface((1000, 600), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))
        screen.blit(overlay, (0, 0))
        
        title = self.font_large.render("SELECT LEVEL", True, self.yellow)
        title_rect = title.get_rect(center=(500, 100))
        screen.blit(title, title_rect)
        
        # Level boxes - centered on screen
        start_x = (1000 - (3 * 150 + 2 * 75)) // 2  # Center the boxes
        for i in range(3):
            x = start_x + i * 225  # 150 width + 75 spacing
            y = 250
            width = 150
            height = 200
            
            # Box
            color = self.white if i < unlocked_levels else self.gray
            pygame.draw.rect(screen, color, (x, y, width, height), 3)
            
            if i < unlocked_levels:
                # Level number
                level_text = self.font_large.render(str(i + 1), True, self.yellow)
                level_rect = level_text.get_rect(center=(x + width // 2, y + 60))
                screen.blit(level_text, level_rect)
                
                # Difficulty
                difficulties = ["EASY", "MEDIUM", "HARD"]
                diff_colors = [self.green, self.yellow, self.red]
                diff_text = self.font_small.render(difficulties[i], True, diff_colors[i])
                diff_rect = diff_text.get_rect(center=(x + width // 2, y + 120))
                screen.blit(diff_text, diff_rect)
                
                # Press key instruction
                key_text = self.font_tiny.render(f"Press {i+1}", True, self.white)
                key_rect = key_text.get_rect(center=(x + width // 2, y + 170))
                screen.blit(key_text, key_rect)
            else:
                # Locked
                lock_text = self.font_medium.render("LOCKED", True, self.gray)
                lock_rect = lock_text.get_rect(center=(x + width // 2, y + height // 2))
                screen.blit(lock_text, lock_rect)
        
        # Back instruction
        back_text = self.font_small.render("Press ESC to return", True, self.gray)
        back_rect = back_text.get_rect(center=(500, 500))
        screen.blit(back_text, back_rect)
    
    def draw_hud(self, screen, aircraft, weapon_system):
        """Draw in-game HUD with organized layout"""
        # Semi-transparent background bar
        hud_bg = pygame.Surface((1000, 90), pygame.SRCALPHA)
        hud_bg.fill((0, 0, 0, 150))
        screen.blit(hud_bg, (0, 0))
        
        # LEFT SECTION: Health and Fuel bars
        self._draw_bar(screen, 20, 15, 220, 25, aircraft.health, aircraft.max_health, 
                      "HEALTH", (0, 255, 100))
        self._draw_bar(screen, 20, 50, 220, 20, aircraft.fuel, aircraft.max_fuel, 
                      "FUEL", (255, 255, 100))
        
        # CENTER SECTION: Score and Lives
        self._draw_text_with_shadow(screen, f"SCORE: {aircraft.score}", self.font_large, self.gold, 500, 28, center=True, shadow_offset=2)
        self._draw_text_with_shadow(screen, f"LIVES: {aircraft.lives}", self.font_medium, self.red, 500, 60, center=True, shadow_offset=1)
        
        # RIGHT SECTION: Weapons and systems
        # Primary weapon
        self._draw_text_with_shadow(screen, f"WEAPON Lv.{weapon_system.primary_level}", self.font_small, self.white, 700, 18, center=False, shadow_offset=1)
        
        # Missiles count
        self._draw_text_with_shadow(screen, f"MISSILES: {weapon_system.missile_count}", self.font_small, (255, 180, 100), 700, 48, center=False, shadow_offset=1)
        
        # Laser and Shield bars (stacked vertically on far right)
        self._draw_bar(screen, 880, 15, 100, 12, weapon_system.laser_charge, 
                      weapon_system.max_laser_charge, "LASER", (100, 200, 255))
        
        self._draw_bar(screen, 880, 45, 100, 12, weapon_system.shield_energy, 
                      weapon_system.max_shield_energy, "SHIELD", (150, 100, 255))
    
    def _draw_bar(self, screen, x, y, width, height, value, max_value, label, color):
        """Draw a resource bar"""
        # Background
        pygame.draw.rect(screen, (50, 50, 50), (x, y, width, height))
        
        # Value
        fill_width = int(width * (value / max_value))
        pygame.draw.rect(screen, color, (x, y, fill_width, height))
        
        # Border
        pygame.draw.rect(screen, self.white, (x, y, width, height), 1)
        
        # Label
        label_text = self.font_tiny.render(label, True, self.white)
        screen.blit(label_text, (x, y - 12))
    
    def draw_pause_menu(self, screen):
        """Draw pause menu"""
        # Semi-transparent overlay
        overlay = pygame.Surface((1000, 600), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Title
        title = self.font_huge.render("PAUSED", True, self.yellow)
        title_rect = title.get_rect(center=(500, 200))
        screen.blit(title, title_rect)
        
        # Instructions
        instructions = [
            "ESC - Resume",
            "M - Return to Menu",
            "Q - Quit Game"
        ]
        
        y = 320
        for line in instructions:
            text = self.font_medium.render(line, True, self.white)
            text_rect = text.get_rect(center=(500, y))
            screen.blit(text, text_rect)
            y += 60
    
    def draw_game_over(self, screen, score, high_score):
        """Draw game over screen"""
        # Background
        overlay = pygame.Surface((1000, 600), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Title
        title = self.font_huge.render("GAME OVER", True, self.red)
        title_rect = title.get_rect(center=(500, 180))
        screen.blit(title, title_rect)
        
        # Score
        score_text = self.font_large.render(f"Final Score: {score}", True, self.yellow)
        score_rect = score_text.get_rect(center=(500, 280))
        screen.blit(score_text, score_rect)
        
        # High score
        if score > high_score:
            hs_text = self.font_medium.render("NEW HIGH SCORE!", True, self.green)
        else:
            hs_text = self.font_medium.render(f"High Score: {high_score}", True, self.white)
        hs_rect = hs_text.get_rect(center=(500, 340))
        screen.blit(hs_text, hs_rect)
        
        # Instructions
        restart_text = self.font_small.render("Press R to Restart - M for Menu - Q to Quit", True, self.gray)
        restart_rect = restart_text.get_rect(center=(500, 450))
        screen.blit(restart_text, restart_rect)
    
    def draw_victory(self, screen, score, high_score):
        """Draw victory screen"""
        # Background
        overlay = pygame.Surface((1000, 600), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Title
        title = self.font_huge.render("VICTORY!", True, self.green)
        title_rect = title.get_rect(center=(500, 150))
        screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.font_medium.render("Mission Accomplished", True, self.yellow)
        subtitle_rect = subtitle.get_rect(center=(500, 220))
        screen.blit(subtitle, subtitle_rect)
        
        # Score
        score_text = self.font_large.render(f"Final Score: {score}", True, self.yellow)
        score_rect = score_text.get_rect(center=(500, 300))
        screen.blit(score_text, score_rect)
        
        # High score
        if score > high_score:
            hs_text = self.font_medium.render("NEW HIGH SCORE!", True, self.green)
        else:
            hs_text = self.font_medium.render(f"High Score: {high_score}", True, self.white)
        hs_rect = hs_text.get_rect(center=(500, 360))
        screen.blit(hs_text, hs_rect)
        
        # Instructions
        restart_text = self.font_small.render("Press R to Restart - M for Menu - Q to Quit", True, self.gray)
        restart_rect = restart_text.get_rect(center=(500, 470))
        screen.blit(restart_text, restart_rect)
    
    def draw_takeoff_instructions(self, screen):
        """Draw takeoff instructions"""
        text = "Press UP to increase thrust - Reach 70% thrust and angle UP to take off"
        instruction = self.font_small.render(text, True, self.yellow)
        
        # Background
        bg_surf = pygame.Surface((instruction.get_width() + 40, 40), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 180))
        bg_rect = bg_surf.get_rect(center=(400, 500))
        screen.blit(bg_surf, bg_rect)
        
        # Text
        inst_rect = instruction.get_rect(center=(400, 500))
        screen.blit(instruction, inst_rect)
