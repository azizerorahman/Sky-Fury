"""
Collision Detection System for Sky Fury
"""

import pygame
from pygame.math import Vector2

def check_collisions(aircraft, enemy_manager, powerup_manager, particle_system):
    """Handle all collision detection"""
    
    # Player bullets vs enemies
    for bullet in aircraft.weapon_system.bullets[:]:
        if not bullet.active:
            continue
        
        bullet_rect = bullet.get_rect()
        
        # Check vs regular enemies
        for enemy in enemy_manager.enemies[:]:
            if not enemy.active:
                continue
            
            if bullet_rect.colliderect(enemy.get_rect()):
                # Hit!
                destroyed = enemy.take_damage(bullet.damage)
                particle_system.create_hit_effect(bullet.position)
                bullet.active = False
                
                if destroyed:
                    particle_system.create_explosion(enemy.position)
                    aircraft.add_score(enemy.score_value)
                    powerup_manager.maybe_spawn_from_enemy(enemy.position)
                
                break
        
        # Check vs boss
        if enemy_manager.boss and enemy_manager.boss.active and bullet.active:
            if bullet_rect.colliderect(enemy_manager.boss.get_rect()):
                destroyed = enemy_manager.boss.take_damage(bullet.damage)
                particle_system.create_hit_effect(bullet.position)
                bullet.active = False
                
                if destroyed:
                    # Boss destroyed!
                    for i in range(8):
                        offset = Vector2(i * 30 - 120, (i % 2) * 40 - 20)
                        particle_system.create_explosion(enemy_manager.boss.position + offset, 
                                                        size=25, count=40)
                    aircraft.add_score(enemy_manager.boss.score_value)
                    powerup_manager.maybe_spawn_from_boss(enemy_manager.boss.position)
    
    # Player missiles vs enemies
    for missile in aircraft.weapon_system.missiles[:]:
        if not missile.active:
            continue
        
        missile_rect = missile.get_rect()
        
        # Check vs regular enemies
        for enemy in enemy_manager.enemies[:]:
            if not enemy.active:
                continue
            
            if missile_rect.colliderect(enemy.get_rect()):
                destroyed = enemy.take_damage(missile.damage)
                particle_system.create_explosion(missile.position, size=12, count=20)
                missile.active = False
                
                if destroyed:
                    particle_system.create_explosion(enemy.position, size=18, count=35)
                    aircraft.add_score(enemy.score_value)
                    powerup_manager.maybe_spawn_from_enemy(enemy.position)
                
                break
        
        # Check vs boss
        if enemy_manager.boss and enemy_manager.boss.active and missile.active:
            if missile_rect.colliderect(enemy_manager.boss.get_rect()):
                destroyed = enemy_manager.boss.take_damage(missile.damage)
                particle_system.create_explosion(missile.position, size=15, count=25)
                missile.active = False
                
                if destroyed:
                    for i in range(8):
                        offset = Vector2(i * 30 - 120, (i % 2) * 40 - 20)
                        particle_system.create_explosion(enemy_manager.boss.position + offset, 
                                                        size=25, count=40)
                    aircraft.add_score(enemy_manager.boss.score_value)
                    powerup_manager.maybe_spawn_from_boss(enemy_manager.boss.position)
    
    # Player lasers vs enemies
    for laser in aircraft.weapon_system.lasers[:]:
        if not laser.active:
            continue
        
        # Lasers hit everything in their path
        for enemy in enemy_manager.enemies[:]:
            if not enemy.active:
                continue
            
            damage = laser.get_damage_at_position(enemy.position)
            if damage > 0:
                destroyed = enemy.take_damage(damage)
                
                if destroyed:
                    particle_system.create_explosion(enemy.position)
                    aircraft.add_score(enemy.score_value)
                    powerup_manager.maybe_spawn_from_enemy(enemy.position)
        
        # Check boss
        if enemy_manager.boss and enemy_manager.boss.active:
            damage = laser.get_damage_at_position(enemy_manager.boss.position)
            if damage > 0:
                destroyed = enemy_manager.boss.take_damage(damage)
                
                if destroyed:
                    for i in range(8):
                        offset = Vector2(i * 30 - 120, (i % 2) * 40 - 20)
                        particle_system.create_explosion(enemy_manager.boss.position + offset, 
                                                        size=25, count=40)
                    aircraft.add_score(enemy_manager.boss.score_value)
                    powerup_manager.maybe_spawn_from_boss(enemy_manager.boss.position)
    
    # Enemy projectiles vs player
    aircraft_rect = aircraft.get_rect()
    
    for proj in enemy_manager.projectiles[:]:
        if not proj.active:
            continue
        
        if aircraft_rect.colliderect(proj.get_rect()):
            if aircraft.shield_active:
                # Shield absorbs hit
                aircraft.take_shield_hit(8)
                particle_system.create_shield_hit(proj.position)
            else:
                # Direct damage to health
                aircraft.take_damage(10)
                particle_system.create_hit_effect(proj.position)
            
            proj.active = False
    
    # Enemies vs player (collision damage)
    for enemy in enemy_manager.enemies[:]:
        if not enemy.active:
            continue
        
        if aircraft_rect.colliderect(enemy.get_rect()):
            if aircraft.shield_active:
                # Shield absorbs collision
                aircraft.take_shield_hit(15)
                particle_system.create_shield_hit(aircraft.position)
            else:
                # Direct collision damage
                aircraft.take_damage(15)
                particle_system.create_hit_effect(aircraft.position)
            
            # Enemy takes damage too
            enemy.take_damage(25)
            particle_system.create_explosion(enemy.position)
    
    # Boss vs player
    if enemy_manager.boss and enemy_manager.boss.active:
        if aircraft_rect.colliderect(enemy_manager.boss.get_rect()):
            if aircraft.shield_active:
                # Shield absorbs boss collision
                aircraft.take_shield_hit(20)
                particle_system.create_shield_hit(aircraft.position)
            else:
                # Heavy boss collision damage
                aircraft.take_damage(20)
                particle_system.create_hit_effect(aircraft.position)
    
    # Power-ups vs player
    messages = powerup_manager.check_collection(aircraft)
    for msg in messages:
        # Create collection effect
        particle_system.create_powerup_collect(aircraft.position)
    
    return messages
