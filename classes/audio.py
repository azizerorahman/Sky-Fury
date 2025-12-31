"""
Audio Management System for Sky Fury
Handles music and sound effects
"""

import pygame
import os

class AudioManager:
    """Manages all game audio"""
    
    def __init__(self):
        pygame.mixer.init()
        
        # Volume settings
        self.music_volume = 0.4
        self.sfx_volume = 0.6
        
        # Get assets directory
        assets_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'sounds'))
        
        # Music tracks - using background.mp3
        music_file = os.path.join(assets_dir, 'background.mp3')
        self.music_tracks = {
            'menu': music_file,
            'level': music_file,
            'boss': music_file
        }
        
        # Sound effects
        self.sounds = {}
        self._load_sounds()
        
        # Current track
        self.current_track = None
    
    def _load_sounds(self):
        """Load all sound effects"""
        assets_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'sounds'))
        
        # Define sound mappings with proper paths - using existing files
        sound_files = {
            'shoot': os.path.join(assets_dir, 'shoot.wav'),
            'missile': os.path.join(assets_dir, 'shoot.wav'),
            'laser': os.path.join(assets_dir, 'shootLaser.wav'),
            'explosion': os.path.join(assets_dir, 'enemyKill.wav'),
            'player_explosion': os.path.join(assets_dir, 'fighterKill.wav'),
            'hit': os.path.join(assets_dir, 'hit.wav'),
            'powerup': os.path.join(assets_dir, 'shoot.wav'),  # Reuse available sound
            'shield_hit': os.path.join(assets_dir, 'hit.wav'),
            'level_complete': os.path.join(assets_dir, 'shootLaser.wav'),  # Reuse
            'game_over': os.path.join(assets_dir, 'fighterKill.wav'),  # Reuse
            'shield': os.path.join(assets_dir, 'shoot.wav')  # Reuse
        }
        
        # Load each sound
        for name, path in sound_files.items():
            try:
                if os.path.exists(path):
                    sound = pygame.mixer.Sound(path)
                    sound.set_volume(self.sfx_volume)
                    self.sounds[name] = sound
                else:
                    # Create placeholder sound if file doesn't exist
                    self.sounds[name] = None
            except Exception as e:
                print(f"Warning: Could not load sound {name}: {e}")
                self.sounds[name] = None
    
    def play_sound(self, sound_name, volume_modifier=1.0):
        """Play a sound effect"""
        if sound_name in self.sounds and self.sounds[sound_name] is not None:
            try:
                # Set temporary volume
                self.sounds[sound_name].set_volume(self.sfx_volume * volume_modifier)
                self.sounds[sound_name].play()
            except:
                pass
    
    def play_music(self, track_name, loop=True):
        """Play background music"""
        if track_name not in self.music_tracks:
            return
        
        # Don't restart if already playing
        if self.current_track == track_name and pygame.mixer.music.get_busy():
            return
        
        try:
            music_path = self.music_tracks[track_name]
            if os.path.exists(music_path):
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1 if loop else 0)
                self.current_track = track_name
        except Exception as e:
            print(f"Warning: Could not play music {track_name}: {e}")
    
    def stop_music(self):
        """Stop current music"""
        pygame.mixer.music.stop()
        self.current_track = None
    
    def pause_music(self):
        """Pause current music"""
        pygame.mixer.music.pause()
    
    def unpause_music(self):
        """Resume paused music"""
        pygame.mixer.music.unpause()
    
    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            if sound is not None:
                sound.set_volume(self.sfx_volume)
