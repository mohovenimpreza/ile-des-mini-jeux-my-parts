"""Records the demo GIFs in screenshots/ by running the real game code headless.
The games are played by a tiny autopilot (BFS for Snake, paddle tracking for Breakout).
Run from the repo root: python tools/record_gifs.py  (needs pygame and pillow)."""
import os; os.environ["SDL_VIDEODRIVER"]="dummy"; os.environ["SDL_AUDIODRIVER"]="dummy"
import sys, random; sys.path.insert(0,".")
import pygame
from collections import deque
from PIL import Image
random.seed(7)
pygame.init(); s=pygame.display.set_mode((700,500))
from jeux.snake import SnakeNeon
from jeux.breakout import Breakout

def grab(frames):
    raw=pygame.image.tostring(s,"RGB"); frames.append(Image.frombytes("RGB",(700,500),raw).resize((560,400)))

def save(frames,path,ms):
    p=frames[0].quantize(colors=128,method=Image.Quantize.MEDIANCUT)
    fr=[f.quantize(palette=p,dither=Image.Dither.NONE) for f in frames]
    fr[0].save(path,save_all=True,append_images=fr[1:],duration=ms,loop=0,optimize=True)

# ---------- Snake autopilot (BFS to apple/bonus, else survive) ----------
def snake_move(g):
    body=set(g.snake); blocked=body|g.walls
    start=g.snake[0]; targets={g.apple}
    if g.bonus: targets.add(g.bonus)
    q=deque([(start,None)]); seen={start}; first={}
    while q:
        c,f=q.popleft()
        if c in targets and f is not None: return f
        for d in ((1,0),(-1,0),(0,1),(0,-1)):
            n=(c[0]+d[0],c[1]+d[1])
            if not(0<=n[0]<g.COLS and 0<=n[1]<g.ROWS) or n in blocked or n in seen: continue
            if c==start and (d[0]==-g.direction[0] and d[1]==-g.direction[1]): continue
            seen.add(n); q.append((n,f or d))
    for d in ((1,0),(-1,0),(0,1),(0,-1)):
        n=(start[0]+d[0],start[1]+d[1])
        if 0<=n[0]<g.COLS and 0<=n[1]<g.ROWS and n not in blocked and not(d[0]==-g.direction[0] and d[1]==-g.direction[1]): return d
    return g.direction

g=SnakeNeon(); fr=[]
for i in range(1600):
    g.set_dir(snake_move(g)); g.update(16); g.draw(s)
    if i%3==0: grab(fr)
    if g.game_over: break
print("snake frames",len(fr),"score",g.score,"level",g.level)
save(fr[:220],"screenshots/snake.gif",50)

# ---------- Breakout autopilot (paddle tracks ball) ----------
class Keys:
    def __init__(s_,l,r): s_.l,s_.r=l,r
    def __getitem__(s_,k): return s_.l if k==pygame.K_LEFT else s_.r if k==pygame.K_RIGHT else False
b=Breakout(); fr=[]
orig=pygame.key.get_pressed
for i in range(2400):
    tgt=b.bx-b.W_PADDLE/2+ (12 if (i//90)%2 else -12)
    pygame.key.get_pressed=lambda: Keys(b.px>tgt+4,b.px<tgt-4)
    if not b.launched and i>20: b.launched=True
    b.update(16); b.draw(s)
    if i%3==0: grab(fr)
    if b.game_over or not b.bricks: break
pygame.key.get_pressed=orig
print("breakout frames",len(fr),"score",b.score,"bricks left",len(b.bricks),"lives",b.lives)
save(fr[:220],"screenshots/breakout.gif",50)
