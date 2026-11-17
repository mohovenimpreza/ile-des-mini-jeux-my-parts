import pygame, math, random
from jeux.ete_theme import (draw_game_bg, draw_wood_panel, draw_wave_line,
                            draw_game_over, BLANC, BRUN, BRUN2, MER, MER_FONC,
                            SABLE, SABLE2, SOLEIL, ORANGE, ROUGE_VIF, VERT_PALM,
                            ROSE, JAUNE_VIF, BOIS, BOIS_FONC)

pygame.init()
L_INTERNE, H_INTERNE = 700, 500

try:
    font_pixel = pygame.font.SysFont("Courier New", 17, bold=True)
    font_main  = pygame.font.SysFont("Courier New", 32, bold=True)
    font_small = pygame.font.SysFont("Courier New", 13)
except Exception:
    font_pixel = pygame.font.Font(None, 20)
    font_main  = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 16)


class Breakout:
    # dimensions raquette
    W_PADDLE, H_PADDLE = 90, 12
    # rayon balle
    BALL_R = 7
    # grille de briques
    COLS, ROWS = 10, 5
    BW, BH = 54, 16
    # offset pour centrer la grille
    BX0 = (L_INTERNE - 10 * (54 + 4)) // 2
    BY0 = 60

    def __init__(self):
        self.level = 1
        self.score = 0
        self.lives = 3
        self.reset()

    def reset(self):
        # raquette centree
        self.px = L_INTERNE // 2 - self.W_PADDLE // 2
        self.py = H_INTERNE - 50

        # balle posee sur la raquette au debut
        self.bx = float(L_INTERNE // 2)
        self.by = float(self.py - self.BALL_R - 2)
        speed = 4.0 + self.level * 0.4
        self.vx = speed
        self.vy = -speed
        self.launched = False

        self.game_over = False
        self.particles = []    # fx particules lors des collisions
        self.bricks = self._gen_bricks()

    def _gen_bricks(self):
        # couleurs par ligne (du haut vers le bas)
        colors = [ROUGE_VIF, ORANGE, SOLEIL, VERT_PALM, MER]
        bricks = []
        for r in range(self.ROWS):
            for c in range(self.COLS):
                x = self.BX0 + c * (self.BW + 4)
                y = self.BY0 + r * (self.BH + 4)
                # les briques du haut ont plus de vie
                hp = self.ROWS - r
                bricks.append({
                    'rect':  pygame.Rect(x, y, self.BW, self.BH),
                    'hp':    hp,
                    'mhp':   hp,
                    'color': colors[r % len(colors)],
                })
        return bricks

    def _spawn_particles(self, x, y, color, n=6):
        # eclate n particules depuis (x,y)
        for _ in range(n):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(1.5, 4.0)
            self.particles.append({
                'x': float(x), 'y': float(y),
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': random.randint(15, 30),
                'color': color,
                'r': random.randint(2, 5),
            })

    def handle_event(self, event):
        # appel depuis la boucle principale pour lancer la balle
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if not self.launched and not self.game_over:
                self.launched = True

    def update(self, dt=0):
        if self.game_over:
            return

        # deplacement raquette
        touches = pygame.key.get_pressed()
        if touches[pygame.K_LEFT]  and self.px > 0:
            self.px -= 6
        if touches[pygame.K_RIGHT] and self.px < L_INTERNE - self.W_PADDLE:
            self.px += 6

        # update particules
        for p in self.particles[:]:
            p['x']    += p['vx']
            p['y']    += p['vy']
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)

        # avant lancement: balle colle a la raquette
        if not self.launched:
            self.bx = self.px + self.W_PADDLE // 2
            self.by = self.py - self.BALL_R - 2
            return

        # mouvement balle
        self.bx += self.vx
        self.by += self.vy

        # rebond mur gauche / droite
        if self.bx - self.BALL_R <= 0:
            self.bx = float(self.BALL_R)
            self.vx = abs(self.vx)
        if self.bx + self.BALL_R >= L_INTERNE:
            self.bx = float(L_INTERNE - self.BALL_R)
            self.vx = -abs(self.vx)

        # rebond plafond
        if self.by - self.BALL_R <= 0:
            self.by = float(self.BALL_R)
            self.vy = abs(self.vy)

        # balle perdue en bas
        if self.by + self.BALL_R >= H_INTERNE:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                self.launched = False
            return

        ball_rect   = pygame.Rect(int(self.bx) - self.BALL_R, int(self.by) - self.BALL_R,
                                  self.BALL_R * 2, self.BALL_R * 2)
        paddle_rect = pygame.Rect(self.px, self.py, self.W_PADDLE, self.H_PADDLE)

        # collision raquette
        if ball_rect.colliderect(paddle_rect) and self.vy > 0:
            # angle de rebond selon l'endroit du hit (-0.5 a +0.5)
            rel   = (self.bx - self.px) / self.W_PADDLE - 0.5
            speed = math.hypot(self.vx, self.vy)
            angle = math.radians(-90 + rel * 120)   # entre -150 et -30 deg
            self.vx = speed * math.cos(angle)
            self.vy = speed * math.sin(angle)
            self._spawn_particles(int(self.bx), self.py, SOLEIL, n=4)

        # collision briques
        for brick in self.bricks[:]:
            if not ball_rect.colliderect(brick['rect']):
                continue

            brick['hp'] -= 1
            self.score  += brick['mhp'] * 10 * self.level
            self._spawn_particles(brick['rect'].centerx, brick['rect'].centery, brick['color'])

            # cote du rebond par overlap minimal
            b  = brick['rect']
            ov = {
                'left':   abs(ball_rect.right  - b.left),
                'right':  abs(ball_rect.left   - b.right),
                'top':    abs(ball_rect.bottom - b.top),
                'bottom': abs(ball_rect.top    - b.bottom),
            }
            side = min(ov, key=ov.get)
            if side in ('top', 'bottom'):
                self.vy *= -1
            else:
                self.vx *= -1

            if brick['hp'] <= 0:
                self.bricks.remove(brick)
            break   # une seule brique par frame

        # toutes les briques cassees = level suivant
        if not self.bricks:
            self.level += 1
            self.lives  = min(self.lives + 1, 5)   # bonus 1 vie
            self.reset()
            self.launched = True    # relance directe au niveau suivant

    def draw(self, surf):
        t = pygame.time.get_ticks() / 1000.0
        draw_game_bg(surf)
        draw_wave_line(surf, H_INTERNE - 35, t, color=(0, 160, 200), alpha=80)

        # --- briques ---
        for brick in self.bricks:
            ratio   = brick['hp'] / brick['mhp']
            c       = brick['color']
            darken  = int((1 - ratio) * 70)
            dc      = tuple(max(0, ch - darken) for ch in c)

            pygame.draw.rect(surf, dc, brick['rect'], border_radius=4)
            # reflet en haut
            hl = tuple(min(255, ch + 60) for ch in dc)
            pygame.draw.rect(surf, hl,
                             (brick['rect'].x + 4, brick['rect'].y + 3, brick['rect'].w - 8, 4),
                             border_radius=2)
            pygame.draw.rect(surf, BRUN, brick['rect'], 1, border_radius=4)

            # fissures si endommagee
            if brick['hp'] < brick['mhp']:
                mx, my = brick['rect'].centerx, brick['rect'].centery
                for ox, oy, ex, ey in [(-6, -2, 2, 4), (3, -3, -1, 3)]:
                    pygame.draw.line(surf, BRUN, (mx + ox, my + oy), (mx + ex, my + ey), 1)

        # --- particules ---
        for p in self.particles:
            alpha = int(255 * p['life'] / 30)
            s = pygame.Surface((p['r'] * 2, p['r'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*p['color'], alpha), (p['r'], p['r']), p['r'])
            surf.blit(s, (int(p['x']) - p['r'], int(p['y']) - p['r']))

        # --- raquette style planche de surf ---
        pr = pygame.Rect(self.px, self.py, self.W_PADDLE, self.H_PADDLE)
        pygame.draw.rect(surf, BOIS,     pr, border_radius=6)
        # ligne deco au centre
        pygame.draw.rect(surf, SOLEIL,
                         (self.px + 10, self.py + 4, self.W_PADDLE - 20, 4),
                         border_radius=2)
        pygame.draw.rect(surf, BOIS_FONC, pr, 2, border_radius=6)

        # --- balle = noix de coco ---
        cx, cy = int(self.bx), int(self.by)
        pygame.draw.circle(surf, BRUN,       (cx, cy), self.BALL_R)
        pygame.draw.circle(surf, (120, 70, 25), (cx - 2, cy - 2), self.BALL_R - 3)
        pygame.draw.circle(surf, BRUN2,      (cx, cy), self.BALL_R, 1)
        # ptits "poils" de coco
        for i in range(3):
            a = math.radians(20 + i * 55)
            pygame.draw.line(surf, (80, 40, 10),
                             (cx, cy),
                             (cx + int(5 * math.cos(a)), cy + int(5 * math.sin(a))), 1)

        # --- message avant lancement ---
        if not self.launched and not self.game_over:
            msg = font_small.render("ESPACE pour lancer", True, SABLE)
            surf.blit(msg, (L_INTERNE // 2 - msg.get_width() // 2, self.py - 22))

        # --- UI ---
        # score
        draw_wood_panel(surf, (6, 6, 160, 26), radius=5)
        surf.blit(font_small.render(f"SCORE: {self.score}", True, BRUN), (12, 10))

        # niveau
        draw_wood_panel(surf, (L_INTERNE // 2 - 55, 6, 110, 26), radius=5)
        lbl = f"NIVEAU: {self.level}"
        surf.blit(font_small.render(lbl, True, BRUN),
                  (L_INTERNE // 2 - font_small.size(lbl)[0] // 2, 10))

        # vies affichees comme des cocos
        draw_wood_panel(surf, (L_INTERNE - 120, 6, 114, 26), radius=5)
        for i in range(self.lives):
            lx = L_INTERNE - 108 + i * 22
            pygame.draw.circle(surf, BRUN, (lx, 19), 7)
            pygame.draw.circle(surf, (120, 70, 25), (lx - 2, 17), 4)

        # hint controles
        ht = font_small.render("<- -> deplacer   ESPACE lancer", True, SABLE)
        surf.blit(ht, (L_INTERNE // 2 - ht.get_width() // 2, H_INTERNE - 18))

        if self.game_over:
            draw_game_over(surf, font_main)