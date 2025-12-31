"""
SKY FURY - Flight Combat Simulator
Main Game Loop and State Management

A left-to-right scrolling aerial combat game featuring:
- Realistic takeoff from airbase runway
- 3 difficulty levels with progressive challenges
- Multiple weapon systems: Primary guns, homing missiles, plasma laser, shield
- 5 diverse enemy types with unique behaviors
- 3 epic boss battles with multi-phase attacks
- Power-up system for upgrades and recovery
- Professional UI with comprehensive HUD

Controls:
- Arrow Keys: Navigate aircraft
- SPACE: Fire primary weapon
- E: Launch homing missile
- R (Hold): Charge and fire plasma laser
- F: Activate energy shield
- ESC: Pause game
"""

import pygame
import sys
from classes.aircraft import Aircraft
from classes.weapons import WeaponSystem
from classes.enemies import EnemyManager
from classes.powerups import PowerUpManager
from classes.particles import ParticleSystem
from classes.collision import check_collisions
from classes.levels import LevelManager
from classes.ui import UserInterface
from classes.audio import AudioManager
from classes.cursor import CustomCursor

# Game constants
SCREEN_WIDTH = 1000  # Increased from 800 for better UI spacing
SCREEN_HEIGHT = 600
FPS = 60

# Game states
STATE_MENU = 'menu'
STATE_LEVEL_SELECT = 'level_select'
STATE_TAKEOFF = 'takeoff'  # NEW: Dedicated takeoff runway phase
STATE_PLAYING = 'playing'  # Combat phase with simple controls
STATE_PAUSED = 'paused'
STATE_GAME_OVER = 'game_over'
STATE_VICTORY = 'victory'

class SkyFury:
    """Main game class"""
    
    def __init__(self):
        pygame.init()
        
        # Screen setup
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Sky Fury - Flight Combat Simulator")
        
        # Hide system cursor and use custom one
        pygame.mouse.set_visible(False)
        self.custom_cursor = CustomCursor()
        
        # Clock
        self.clock = pygame.time.Clock()
        
        # Game state
        self.state = STATE_MENU
        self.running = True
        
        # Game systems
        self.ui = UserInterface()
        self.audio = AudioManager()
        
        # Load airport and city parallax for takeoff screen
        self._load_takeoff_backgrounds()
        
        # Level data
        self.current_level = 1
        self.unlocked_levels = 3  # All levels unlocked for testing
        self.demo_boss_level = 0  # Track which boss to spawn (0=none, 1-3=bosses)
        
        # Game objects (initialized in start_game)
        self.aircraft = None
        self.weapon_system = None
        self.enemy_manager = None
        self.powerup_manager = None
        self.particle_system = None
        self.level_manager = None
        
        # Transition smoothing
        self.transition_timer = 0.0
        
        # Fade system for smooth transitions
        self.fade_alpha = 0  # 0 = transparent, 255 = full black
        self.fade_direction = 0  # 0 = no fade, 1 = fade out, -1 = fade in
        self.fade_speed = 400  # Alpha units per second
    
    def _load_takeoff_backgrounds(self):
        """Load airport and city parallax backgrounds for takeoff screen"""
        import os
        
        # Initialize defaults first
        self.airport_bg = None
        self.city_parallax = []
        self.city_parallax_speeds = []
        self.city_scroll_offset = 0
        
        assets_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), 'assets', 'images'))
        
        try:
            # Load airport background from images folder
            airport_path = os.path.join(assets_dir, 'airport.png')
            if os.path.exists(airport_path):
                self.airport_bg = pygame.image.load(airport_path).convert_alpha()
            
            # Load city parallax layers
            self.city_parallax = []
            for i in range(1, 4):
                parallax_path = os.path.join(assets_dir, f'city_parallax_{i}.png')
                if os.path.exists(parallax_path):
                    img = pygame.image.load(parallax_path).convert_alpha()
                    self.city_parallax.append(img)
            
            # Parallax speeds for city layers (slower = further away)
            self.city_parallax_speeds = [0.3, 0.5, 0.7]  # Slower than in-flight parallax
            
        except Exception as e:
            print(f"Warning: Could not load takeoff backgrounds: {e}")
            self.airport_bg = None
            self.city_parallax = []
            self.city_parallax_speeds = []
    
    def start_game(self, level=1):
        """Initialize a new game"""
        self.current_level = level
        
        # Create game objects
        self.aircraft = Aircraft()
        self.weapon_system = WeaponSystem(self.aircraft)
        self.aircraft.weapon_system = self.weapon_system  # Link weapon system to aircraft
        self.enemy_manager = EnemyManager()
        self.powerup_manager = PowerUpManager()
        self.particle_system = ParticleSystem()
        self.level_manager = LevelManager(level)
        
        # Start with TAKEOFF phase (runway)
        self.state = STATE_TAKEOFF
        
        # Play level music
        self.audio.play_music('level')
        
        # Show level start message
        self.ui.show_message(f"LEVEL {level} - TAKEOFF!", 3.0)
    
    def handle_events(self):
        """Process input events"""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Mouse click handling for menus
                if self.state == STATE_MENU:
                    # Simple click to start
                    self.state = STATE_LEVEL_SELECT
                elif self.state == STATE_LEVEL_SELECT:
                    # Click on level boxes (adjusted for 1000px width)
                    if 200 <= mouse_pos[0] <= 350 and 250 <= mouse_pos[1] <= 450:
                        self.start_game(1)
                    elif 425 <= mouse_pos[0] <= 575 and 250 <= mouse_pos[1] <= 450:
                        self.start_game(2)
                    elif 650 <= mouse_pos[0] <= 800 and 250 <= mouse_pos[1] <= 450:
                        self.start_game(3)
                elif self.state in [STATE_GAME_OVER, STATE_VICTORY]:
                    # Click to restart or menu
                    self.start_game(self.current_level)
            
            elif event.type == pygame.KEYDOWN:
                # TAB key: Cycle through bosses (for screen recording/demo)
                if event.key == pygame.K_TAB and self.state == STATE_PLAYING:
                    # Clear all enemies
                    self.enemy_manager.enemies = []
                    self.enemy_manager.spawn_queue = []
                    
                    # Cycle to next boss (1 -> 2 -> 3 -> 1 -> ...)
                    self.demo_boss_level = (self.demo_boss_level % 3) + 1
                    
                    # Boss type mapping
                    boss_types = ["hive_queen", "aegis_defender", "final_destroyer"]
                    boss_names = ["HIVE QUEEN", "AEGIS DEFENDER", "TITAN FORTRESS"]
                    
                    # Spawn the selected boss
                    self.enemy_manager.spawn_boss(boss_types[self.demo_boss_level - 1])
                    self.ui.show_message(f"BOSS {self.demo_boss_level}: {boss_names[self.demo_boss_level - 1]}!", 2.0)
                    self.audio.play_sound('level_complete')
                
                # Universal controls
                if event.key == pygame.K_ESCAPE:
                    if self.state == STATE_TAKEOFF:
                        self.state = STATE_PAUSED
                        self.audio.pause_music()
                    elif self.state == STATE_PLAYING:
                        self.state = STATE_PAUSED
                        self.audio.pause_music()
                    elif self.state == STATE_PAUSED:
                        self.state = STATE_PLAYING if self.aircraft.has_taken_off else STATE_TAKEOFF
                        self.audio.unpause_music()
                    elif self.state == STATE_LEVEL_SELECT:
                        self.state = STATE_MENU
                
                # Menu state
                if self.state == STATE_MENU:
                    if event.key == pygame.K_RETURN:
                        self.state = STATE_LEVEL_SELECT
                    elif event.key == pygame.K_q:
                        self.running = False
                
                # Level select state
                elif self.state == STATE_LEVEL_SELECT:
                    if event.key == pygame.K_1 and self.unlocked_levels >= 1:
                        self.start_game(1)
                    elif event.key == pygame.K_2 and self.unlocked_levels >= 2:
                        self.start_game(2)
                    elif event.key == pygame.K_3 and self.unlocked_levels >= 3:
                        self.start_game(3)
                
                # Pause state
                elif self.state == STATE_PAUSED:
                    if event.key == pygame.K_m:
                        self.state = STATE_MENU
                        self.audio.stop_music()
                        self.audio.play_music('menu')
                    elif event.key == pygame.K_q:
                        self.running = False
                
                # Game over / Victory state
                elif self.state in [STATE_GAME_OVER, STATE_VICTORY]:
                    if event.key == pygame.K_r:
                        self.start_game(self.current_level)
                    elif event.key == pygame.K_m:
                        self.state = STATE_MENU
                        self.audio.stop_music()
                        self.audio.play_music('menu')
                    elif event.key == pygame.K_q:
                        self.running = False
    
    def _handle_takeoff_controls(self, keys, dt):
        """Handle controls during takeoff phase - acceleration and smooth pitch control"""
        # UP arrow = accelerate on runway AND smoothly pitch up for takeoff
        if keys[pygame.K_UP]:
            self.aircraft.thrust = min(100, self.aircraft.thrust + 5)
            # Smoothly aim nose-up as we roll forward (more natural ramp)
            # Start rotation later and cap to a modest angle
            start_x = 180
            end_x = 300
            progress = 0.0
            if self.aircraft.position.x > start_x:
                progress = min(1.0, (self.aircraft.position.x - start_x) / (end_x - start_x))
            target_angle = 18.0 * progress  # Ramp up to ~18°
            # Lerp toward target for smooth rotation (slower smoothing for natural feel)
            self.aircraft.angle += (target_angle - self.aircraft.angle) * 2.5 * dt
        else:
            # Gradual thrust decay
            self.aircraft.thrust = max(0, self.aircraft.thrust - 1)
        
        # DOWN arrow = brake and gently reduce pitch
        if keys[pygame.K_DOWN]:
            self.aircraft.brakes_active = True
            self.aircraft.thrust = max(0, self.aircraft.thrust - 5)
            self.aircraft.angle = max(0, self.aircraft.angle - 20.0 * dt)
        else:
            self.aircraft.brakes_active = False
    
    def _handle_combat_controls(self, keys, dt):
        """Handle simple arrow key controls during combat phase"""
        # During transition, smoothly level the aircraft
        if self.transition_timer > 0:
            self.transition_timer -= dt
            # Gradually level out to 0° from takeoff angle
            self.aircraft.angle += (0 - self.aircraft.angle) * 2.0 * dt
            # Smoothly move to combat starting position
            target_x = 150
            target_y = 300
            self.aircraft.position.x += (target_x - self.aircraft.position.x) * 1.5 * dt
            self.aircraft.position.y += (target_y - self.aircraft.position.y) * 1.5 * dt
            return  # Skip normal controls during transition
        
        # Simple direct position control with arrow keys
        move_speed = 5.0
        
        if keys[pygame.K_UP]:
            self.aircraft.position.y -= move_speed
        if keys[pygame.K_DOWN]:
            self.aircraft.position.y += move_speed
        if keys[pygame.K_LEFT]:
            self.aircraft.position.x -= move_speed
        if keys[pygame.K_RIGHT]:
            self.aircraft.position.x += move_speed
        
        # Keep aircraft in bounds (left side of screen for combat)
        self.aircraft.position.x = max(50, min(250, self.aircraft.position.x))
        self.aircraft.position.y = max(20, min(580, self.aircraft.position.y))
        
        # Update angle based on vertical movement for visual feedback
        if keys[pygame.K_UP]:
            self.aircraft.angle = min(15, self.aircraft.angle + 0.5)
        elif keys[pygame.K_DOWN]:
            self.aircraft.angle = max(-15, self.aircraft.angle - 0.5)
        else:
            # Return to level
            if self.aircraft.angle > 0:
                self.aircraft.angle = max(0, self.aircraft.angle - 0.3)
            elif self.aircraft.angle < 0:
                self.aircraft.angle = min(0, self.aircraft.angle + 0.3)
    
    def _handle_aircraft_controls(self, keys, dt):
        """Handle continuous aircraft control inputs"""
        # Thrust control
        if keys[pygame.K_UP]:
            self.aircraft.thrust = min(100, self.aircraft.thrust + 2)
        if keys[pygame.K_DOWN]:
            self.aircraft.thrust = max(-20 if self.aircraft.on_ground else 0, self.aircraft.thrust - 2)
        
        # Pitch control
        if keys[pygame.K_LEFT]:
            self.aircraft.angle = min(15, self.aircraft.angle + 1.0)
        if keys[pygame.K_RIGHT]:
            self.aircraft.angle = max(-15, self.aircraft.angle - 1.0)
        
        # Other controls
        self.aircraft.brakes_active = keys[pygame.K_d]
        self.aircraft.spoilers_active = keys[pygame.K_s]
        
        # Flaps
        if keys[pygame.K_q]:
            self.aircraft.flaps = min(3, self.aircraft.flaps + 0.1)
        if keys[pygame.K_a]:
            self.aircraft.flaps = max(0, self.aircraft.flaps - 0.1)
    
    def _handle_weapon_controls(self, keys, dt):
        """Handle weapon firing controls"""
        # Primary weapon (auto-fire when held)
        if keys[pygame.K_SPACE]:
            if self.weapon_system.fire_primary():
                self.audio.play_sound('shoot')
        
        # Homing missile
        if keys[pygame.K_e]:
            if self.weapon_system.fire_missile():
                self.audio.play_sound('missile')
        
        # Laser charging
        if keys[pygame.K_r]:
            self.weapon_system.is_charging_laser = True
        else:
            if self.weapon_system.is_charging_laser:
                if self.weapon_system.fire_laser():
                    self.audio.play_sound('laser')
                self.weapon_system.is_charging_laser = False
        
        # Shield
        if keys[pygame.K_f]:
            if self.weapon_system.activate_shield():
                self.aircraft.activate_shield(5.0)
                self.audio.play_sound('shield')
    
    def update(self, dt):
        """Update game logic"""
        # Update messages
        self.ui.update_messages(dt)
        
        # TAKEOFF PHASE - Runway acceleration
        if self.state == STATE_TAKEOFF:
            keys = pygame.key.get_pressed()
            
            # Update fade if active
            if self.fade_direction != 0:
                self.fade_alpha += self.fade_direction * self.fade_speed * dt
                if self.fade_alpha <= 0:
                    self.fade_alpha = 0
                    self.fade_direction = 0
                elif self.fade_alpha >= 255:
                    self.fade_alpha = 255
            
            # Update city parallax scrolling for atmosphere
            self.city_scroll_offset += 20 * dt  # Slow scroll
            
            # Handle takeoff controls
            self._handle_takeoff_controls(keys, dt)
            
            # Update aircraft physics
            self.aircraft.update(dt)
            
            # Check if aircraft has flown completely off-screen (out of view)
            if self.aircraft.has_taken_off and self.aircraft.position.y < 1000:
                # Start fade-out transition
                if self.fade_direction == 0:  # Only trigger once
                    self.fade_direction = 1  # Start fading out
                
                # Wait for full black before switching
                if self.fade_alpha >= 255 and self.state == STATE_TAKEOFF:
                    # Create takeoff splash effect
                    for _ in range(30):
                        self.particle_system.add_particles(
                            self.aircraft.position.x - 30, 
                            self.aircraft.position.y + 20, 
                            particle_type='explosion'
                        )
                    # Transition to combat phase while screen is still black
                    self.state = STATE_PLAYING
                    self.aircraft.invulnerable = False  # Clear invulnerability for combat
                    self.aircraft.invulnerable_timer = 0.0
                    self.transition_timer = 1.5  # Smooth 1.5s transition period
                    self.ui.show_message("COMBAT ZONE - ENGAGE!", 2.0)
                    self.audio.play_sound('level_complete')
                    # Start fading back in from black
                    self.fade_direction = -1
        
        # COMBAT PHASE - Simple arrow key movement
        elif self.state == STATE_PLAYING:
            keys = pygame.key.get_pressed()
            
            # Update fade if active
            if self.fade_direction != 0:
                self.fade_alpha += self.fade_direction * self.fade_speed * dt
                if self.fade_alpha <= 0:
                    self.fade_alpha = 0
                    self.fade_direction = 0
                elif self.fade_alpha >= 255:
                    self.fade_alpha = 255
            
            # Handle simple combat controls (arrow keys for movement)
            self._handle_combat_controls(keys, dt)
            
            # Handle weapon controls
            self._handle_weapon_controls(keys, dt)
            
            # UPDATE AIRCRAFT - critical for timers and state
            self.aircraft.update(dt)
            
            # Update weapons
            self.weapon_system.update(dt)
            
            # Update level manager (spawns enemies)
            self.level_manager.update(dt, self.aircraft, self.enemy_manager)
            
            # Update enemies (pass missiles for homing)
            self.enemy_manager.update(dt, self.aircraft.position, self.weapon_system.missiles)
            
            # Update power-ups
            self.powerup_manager.update(dt)
            
            # Update particles
            self.particle_system.update(dt)
            
            # Check collisions
            check_collisions(
                self.aircraft,
                self.enemy_manager,
                self.powerup_manager,
                self.particle_system
            )
            
            # Check for aircraft death (crashed or destroyed)
            if self.aircraft.health <= 0:
                # Create explosion effect
                self.particle_system.create_explosion(self.aircraft.position, size=50, count=100)
                self.audio.play_sound('player_explosion')
                
                # Lose a life
                self.aircraft.lose_life()
                
                # If no lives left, game over
                if self.aircraft.lives <= 0:
                    self.state = STATE_GAME_OVER
                    self.ui.save_high_score(self.aircraft.score)
                    self.audio.stop_music()
                    self.audio.play_sound('game_over')
                else:
                    # Return to takeoff phase for respawn
                    self.state = STATE_TAKEOFF
                    self.fade_alpha = 0
                    self.fade_direction = 0
                    self.ui.show_message(f"RESPAWN - Lives remaining: {self.aircraft.lives}", 2.0)
            
            # Check for level completion
            elif self.level_manager.level_complete:
                if self.current_level < 3:
                    # Next level
                    self.current_level += 1
                    self.ui.show_message(f"LEVEL {self.current_level - 1} COMPLETE!", 3.0)
                    self.audio.play_sound('level_complete')
                    # Restart with next level
                    pygame.time.wait(2000)
                    self.start_game(self.current_level)
                else:
                    # Victory!
                    self.state = STATE_VICTORY
                    self.ui.save_high_score(self.aircraft.score)
                    self.audio.stop_music()
                    self.audio.play_sound('level_complete')
            
            # Update music based on boss status
            if self.enemy_manager.boss and self.audio.current_track != 'boss':
                self.audio.play_music('boss')
            elif not self.enemy_manager.boss and self.audio.current_track == 'boss':
                self.audio.play_music('level')
    
    def draw(self):
        """Render everything"""
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        if self.state == STATE_MENU:
            # Draw menu
            self.ui.draw_menu(self.screen)
        
        elif self.state == STATE_LEVEL_SELECT:
            # Draw level selection
            self.ui.draw_level_select(self.screen, self.unlocked_levels)
        
        elif self.state == STATE_TAKEOFF:
            # FULL SCREEN RUNWAY - Takeoff Phase
            self._draw_takeoff_screen()
        
        elif self.state in [STATE_PLAYING, STATE_PAUSED]:
            # Draw game world
            self.level_manager.draw_background(self.screen, self.aircraft)
            
            # Draw takeoff instructions if on ground
            if self.aircraft.on_ground and not self.aircraft.has_taken_off:
                self.ui.draw_takeoff_instructions(self.screen)
            
            # Draw game objects
            self.powerup_manager.draw(self.screen)
            self.enemy_manager.draw(self.screen)
            self.weapon_system.draw(self.screen)
            self.aircraft.draw(self.screen)
            self.particle_system.draw(self.screen)
            
            # Draw HUD
            self.ui.draw_hud(self.screen, self.aircraft, self.weapon_system)
            
            # Draw messages
            self.ui.draw_messages(self.screen)
            
            # Draw pause overlay
            if self.state == STATE_PAUSED:
                self.ui.draw_pause_menu(self.screen)
        
        elif self.state == STATE_GAME_OVER:
            # Draw final game state
            if self.aircraft and self.weapon_system:
                self.level_manager.draw_background(self.screen, self.aircraft)
                self.powerup_manager.draw(self.screen)
                self.enemy_manager.draw(self.screen)
                self.weapon_system.draw(self.screen)
                self.particle_system.draw(self.screen)
            
            # Draw game over overlay
            self.ui.draw_game_over(self.screen, 
                                  self.aircraft.score if self.aircraft else 0,
                                  self.ui.high_score)
        
        elif self.state == STATE_VICTORY:
            # Draw final game state
            if self.aircraft and self.weapon_system:
                self.level_manager.draw_background(self.screen, self.aircraft)
                self.powerup_manager.draw(self.screen)
                self.enemy_manager.draw(self.screen)
                self.weapon_system.draw(self.screen)
                self.particle_system.draw(self.screen)
            
            # Draw victory overlay
            self.ui.draw_victory(self.screen, 
                                self.aircraft.score if self.aircraft else 0,
                                self.ui.high_score)
        
        # Draw custom cursor on top of everything
        if self.state in [STATE_MENU, STATE_LEVEL_SELECT, STATE_GAME_OVER, STATE_VICTORY]:
            mouse_pos = pygame.mouse.get_pos()
            self.custom_cursor.draw(self.screen, mouse_pos)
        
        # Draw fade overlay if active
        if self.fade_alpha > 0:
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(int(self.fade_alpha))
            self.screen.blit(fade_surface, (0, 0))
        
        # Flip display
        pygame.display.flip()
    
    def _draw_takeoff_screen(self):
        """Draw full-screen runway for takeoff phase - updated for 1000px width with airport/city parallax"""
        # Sky gradient background
        for y in range(600):
            color_value = int(135 + (y / 600) * 100)
            pygame.draw.line(self.screen, (color_value // 2, color_value // 2, color_value), 
                           (0, y), (1000, y))
        
        # Draw city parallax layers with slow scrolling - FIXED: render in proper sequence
        if self.city_parallax:
            # Layer 0 (furthest) - top of screen
            if len(self.city_parallax) > 0:
                layer = self.city_parallax[0]
                speed = self.city_parallax_speeds[0]
                offset = int(self.city_scroll_offset * speed) % layer.get_width()
                y_pos = 50  # Far background
                for x in range(-layer.get_width(), 1000, layer.get_width()):
                    self.screen.blit(layer, (x - offset, y_pos))
            
            # Layer 1 (middle) - middle of screen
            if len(self.city_parallax) > 1:
                layer = self.city_parallax[1]
                speed = self.city_parallax_speeds[1]
                offset = int(self.city_scroll_offset * speed) % layer.get_width()
                y_pos = 150  # Middle background
                for x in range(-layer.get_width(), 1000, layer.get_width()):
                    self.screen.blit(layer, (x - offset, y_pos))
            
            # Layer 2 (closest) - lower screen
            if len(self.city_parallax) > 2:
                layer = self.city_parallax[2]
                speed = self.city_parallax_speeds[2]
                offset = int(self.city_scroll_offset * speed) % layer.get_width()
                y_pos = 280  # Foreground
                for x in range(-layer.get_width(), 1000, layer.get_width()):
                    self.screen.blit(layer, (x - offset, y_pos))
        
        # Ground (bottom half)
        pygame.draw.rect(self.screen, (60, 120, 40), (0, 400, 1000, 200))  # Grass
        
        # Draw airport building - single instance on the ground
        if self.airport_bg:
            # Scale to ground level height
            airport_width = self.airport_bg.get_width()
            airport_height = self.airport_bg.get_height()
            # Scale to fit above grass, below city
            scale_factor = 180 / airport_height if airport_height > 0 else 1
            scaled_width = int(airport_width * scale_factor)
            scaled_height = int(airport_height * scale_factor)
            scaled_airport = pygame.transform.scale(self.airport_bg, (scaled_width, scaled_height))
            
            # Draw single airport building centered on ground
            airport_x = (1000 - scaled_width) // 2  # Center horizontally
            airport_y = 400 - scaled_height  # Place on top of grass
            self.screen.blit(scaled_airport, (airport_x, airport_y))
        
        # Runway - full screen width
        runway_y = 480
        runway_height = 80
        pygame.draw.rect(self.screen, (40, 40, 40), (0, runway_y, 1000, runway_height))  # Dark asphalt
        
        # Runway center line
        for x in range(0, 1000, 60):
            pygame.draw.rect(self.screen, (255, 255, 100), (x, runway_y + 35, 40, 10))
        
        # Runway side lines
        pygame.draw.rect(self.screen, (255, 255, 255), (0, runway_y, 1000, 3))  # Top edge
        pygame.draw.rect(self.screen, (255, 255, 255), (0, runway_y + runway_height - 3, 1000, 3))  # Bottom edge
        
        # Speed markers on side
        font = pygame.font.SysFont('Arial', 20, bold=True)
        for i, speed in enumerate([50, 100, 150, 200, 250]):
            x = 150 + i * 170
            pygame.draw.rect(self.screen, (255, 255, 255), (x, runway_y - 5, 3, 10))
            speed_text = font.render(str(speed), True, (255, 255, 255))
            self.screen.blit(speed_text, (x - 15, runway_y - 30))
        
        # Draw aircraft on runway
        self.aircraft.draw(self.screen)
        
        # Draw HUD info - slightly larger fonts for 1000px screen
        hud_font = pygame.font.SysFont('Arial', 36, bold=True)
        info_font = pygame.font.SysFont('Arial', 26)
        
        # Speed indicator
        speed = int(self.aircraft.velocity.x * 20)  # Scale for display
        speed_text = hud_font.render(f"SPEED: {speed} km/h", True, (0, 255, 100))
        self.screen.blit(speed_text, (30, 20))
        
        # Thrust indicator
        thrust_text = info_font.render(f"THRUST: {int(self.aircraft.thrust)}%", True, (255, 255, 100))
        self.screen.blit(thrust_text, (30, 65))
        
        # Takeoff speed indicator
        if speed < 100:
            status_color = (255, 100, 100)
            status = "ACCELERATE!"
        elif speed < 150:
            status_color = (255, 255, 100)
            status = "ALMOST THERE..."
        else:
            status_color = (0, 255, 100)
            status = "ROTATE - TAKEOFF!"
        
        status_text = hud_font.render(status, True, status_color)
        status_rect = status_text.get_rect(center=(500, 100))
        self.screen.blit(status_text, status_rect)
        
        # Instructions
        inst_font = pygame.font.SysFont('Arial', 22)
        instructions = [
            "↑ UP ARROW: Accelerate",
            "↓ DOWN ARROW: Brake",
            "Hold UP to build speed and takeoff!"
        ]
        
        for i, inst in enumerate(instructions):
            inst_text = inst_font.render(inst, True, (255, 255, 255))
            inst_rect = inst_text.get_rect(center=(500, 200 + i * 35))
            self.screen.blit(inst_text, inst_rect)
    
    def run(self):
        """Main game loop"""
        # Start with menu music
        self.audio.play_music('menu')
        
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(FPS) / 1000.0
            
            # Handle events
            self.handle_events()
            
            # Update
            self.update(dt)
            
            # Draw
            self.draw()
        
        # Cleanup
        pygame.quit()
        sys.exit()

def main():
    """Entry point"""
    game = SkyFury()
    game.run()

if __name__ == "__main__":
    main()
