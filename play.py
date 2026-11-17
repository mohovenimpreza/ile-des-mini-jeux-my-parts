"""Small launcher to try my two mini-games on their own (outside the full team game).

    python play.py            -> menu
    1 = Snake   2 = Breakout   R = restart   Esc = back / quit
"""
import pygame
from jeux.snake import SnakeNeon
from jeux.breakout import Breakout

W, H = 700, 500
pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("L'Île des Mini-Jeux - Snake & Breakout")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

game = None
running = True
while running:
    dt = clock.tick(60)
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                if game is None:
                    running = False
                else:
                    game = None
            elif game is None:
                if ev.key == pygame.K_1:
                    game = SnakeNeon()
                elif ev.key == pygame.K_2:
                    game = Breakout()
            else:
                if ev.key == pygame.K_r:
                    game.reset()
                if isinstance(game, SnakeNeon):
                    moves = {pygame.K_UP: (0, -1), pygame.K_DOWN: (0, 1),
                             pygame.K_LEFT: (-1, 0), pygame.K_RIGHT: (1, 0)}
                    if ev.key in moves:
                        game.set_dir(moves[ev.key])
                else:
                    game.handle_event(ev)

    if game is None:
        screen.fill((20, 30, 50))
        for i, t in enumerate(["1 - Snake", "2 - Breakout", "Esc - quit"]):
            screen.blit(font.render(t, True, (255, 255, 255)), (250, 180 + i * 50))
    else:
        game.update(dt)
        game.draw(screen)
    pygame.display.flip()

pygame.quit()
