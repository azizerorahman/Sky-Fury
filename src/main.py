import pygame
import sys
from game import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Sky Fury - Initial Prototype")

    game = Game(screen)
    try:
        game.run()
    except Exception as e:
        print("Error during runtime:", e)
    finally:
        pygame.quit()

if __name__ == '__main__':
    main()
