import pygame
import math
import random

pygame.init()

# --- 화면 설정 ---
WIDTH, HEIGHT = 1800, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("턴제 탱크 포트리스")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

# --- 색상 ---
WHITE = (255,255,255)
BLACK = (0,0,0)
GREEN = (0,200,0)
RED = (200,0,0)
BLUE = (0,100,255)
GRAY = (120,120,120)

GROUND_Y = HEIGHT - 60
GRAVITY = 0.35

PLAYER_TURN = 0
ENEMY_TURN = 1
current_turn = PLAYER_TURN

TANK_SIZE = 20
MAX_MOVE_PER_TURN = TANK_SIZE * 4

# --- 초기화 함수 ---
def init_game():
    global player, enemy, projectile, current_turn
    player = {
        "x": 300, "y": GROUND_Y - TANK_SIZE, "angle": 45,
        "direction": "right", "power": 0, "charging": False,
        "score": 0, "hit_timer": 0, "move_used": 0
    }
    enemy = {
        "x": 1400, "y": GROUND_Y - TANK_SIZE, "angle": 135,
        "direction": "left", "power": 0, "score": 0, "hit_timer": 0, "move_used": 0
    }
    projectile = None
    current_turn = PLAYER_TURN

init_game()

# --- 포신 각도 조정 (방향 기반) ---
def adjust_angle_by_direction(tank, delta):
    if tank["direction"] == "right":
        min_a, max_a = 15, 75
    else:
        min_a, max_a = 105, 165

    # 끝단에서 큰 스텝 적용
    if tank["angle"] <= min_a and delta < 0:
        tank["angle"] -= 30
    elif tank["angle"] >= max_a and delta > 0:
        tank["angle"] += 30
    else:
        tank["angle"] += delta

    # 절대 범위 제한
    tank["angle"] = max(min_a, min(max_a, tank["angle"]))

# --- 포탄 생성 ---
def fire(tank):
    rad = math.radians(tank["angle"])
    power = tank["power"]
    return {"x": tank["x"], "y": tank["y"], "vx": math.cos(rad)*power, "vy": -math.sin(rad)*power}

# --- 탱크 그리기 ---
def draw_tank(tank,color):
    if tank["hit_timer"]>0:
        tank["hit_timer"]-=1
        color = WHITE if tank["hit_timer"]%4<2 else color
    pygame.draw.rect(screen,color,(tank["x"]-TANK_SIZE,tank["y"]-TANK_SIZE//2,TANK_SIZE*2,TANK_SIZE))
    end_x = tank["x"] + math.cos(math.radians(tank["angle"]))*30
    end_y = tank["y"] - math.sin(math.radians(tank["angle"]))*30
    pygame.draw.line(screen,BLACK,(tank["x"],tank["y"]),(end_x,end_y),3)

# --- 이동 처리 ---
def move_tank(tank,dx):
    if tank["move_used"]>=MAX_MOVE_PER_TURN: return
    remaining = MAX_MOVE_PER_TURN - tank["move_used"]
    actual_move = min(abs(dx),remaining)
    tank["x"] += actual_move if dx>0 else -actual_move
    tank["move_used"] += actual_move
    tank["direction"] = "right" if dx>0 else "left"

def draw_move_gauge(tank,x,y):
    ratio = tank["move_used"]/MAX_MOVE_PER_TURN
    percent = int(ratio*100)
    pygame.draw.rect(screen,(80,80,80),(x,y,120,12))
    pygame.draw.rect(screen,GREEN,(x,y,int(120*ratio),12))
    pygame.draw.rect(screen,WHITE,(x,y,120,12),1)
    label=font.render(f"{percent}%",True,WHITE)
    screen.blit(label,(x+130,y-2))

# --- 폭발 ---
def draw_explosion(x,y):
    for r in range(10,40,6):
        pygame.draw.circle(screen,RED,(int(x),int(y)),r,2)
    pygame.display.flip()
    pygame.time.delay(120)

# --- 포탄 업데이트 ---
def update_projectile():
    global projectile,current_turn
    if projectile is None: return
    prev_x,prev_y = projectile["x"],projectile["y"]
    projectile["x"] += projectile["vx"]
    projectile["y"] += projectile["vy"]
    projectile["vy"] += GRAVITY
    pygame.draw.circle(screen,BLACK,(int(projectile["x"]),int(projectile["y"])),5)

    def hit_check(tank):
        tx,ty=tank["x"],tank["y"]
        dx=projectile["x"]-prev_x;dy=projectile["y"]-prev_y
        if dx==0 and dy==0: return False
        t=((tx-prev_x)*dx+(ty-prev_y)*dy)/(dx*dx+dy*dy);t=max(0,min(1,t))
        closest_x=prev_x+t*dx;closest_y=prev_y+t*dy
        dist=math.hypot(tx-closest_x,ty-closest_y)
        return dist<22

    if current_turn==PLAYER_TURN and hit_check(enemy):
        player["score"]+=1
        enemy["hit_timer"] = 20
        draw_explosion(enemy["x"],enemy["y"])
        projectile=None
        switch_turn()
        return
    if current_turn==ENEMY_TURN and hit_check(player):
        enemy["score"]+=1
        player["hit_timer"] = 20
        draw_explosion(player["x"],player["y"])
        projectile=None
        switch_turn()
        return
    if projectile["y"]>GROUND_Y:
        draw_explosion(projectile["x"],GROUND_Y)
        projectile=None
        switch_turn()
        return

# --- 턴 전환 ---
def switch_turn():
    global current_turn
    if current_turn==PLAYER_TURN:
        current_turn=ENEMY_TURN
        player["move_used"] = 0
    else:
        current_turn=PLAYER_TURN
        enemy["move_used"] = 0

# --- 적 AI ---
def enemy_logic():
    global projectile
    dx=player["x"]-enemy["x"]
    dy=enemy["y"]-player["y"]
    g=GRAVITY
    distance=abs(dx); distance=1 if distance<1 else distance

    theta = math.radians(45)
    denom = (distance*math.tan(theta)-dy)
    base_power = 18 if denom <=0 else math.sqrt((g*distance*distance)/(2*(math.cos(theta)**2)*denom))
    base_angle=45
    if dx<0: base_angle = 180 - base_angle

    if "shot_count" not in enemy: enemy["shot_count"] = 0
    enemy["shot_count"] +=1
    reduction = 0.5 ** (enemy["shot_count"]//5)
    angle_error=random.uniform(-8,8)*reduction
    power_error=random.uniform(-6,6)*reduction

    enemy["angle"] = base_angle + angle_error
    # 방향 기반 각도 제한 적용
    adjust_angle_by_direction(enemy,0)
    enemy["power"] = max(8,min(base_power+power_error,40))
    projectile=fire(enemy)

# --- 게임 루프 ---
running = True
while running:
    clock.tick(60)
    screen.fill(WHITE)
    pygame.draw.rect(screen,GRAY,(0,GROUND_Y,WIDTH,60))

    for event in pygame.event.get():
        if event.type==pygame.QUIT: running=False
        if current_turn==PLAYER_TURN:
            if event.type==pygame.KEYDOWN and event.key==pygame.K_SPACE: player["charging"]=True
            if event.type==pygame.KEYUP and event.key==pygame.K_SPACE:
                player["charging"]=False
                projectile=fire(player)
                player["power"]=0

    keys=pygame.key.get_pressed()
    if current_turn==PLAYER_TURN:
        if keys[pygame.K_LEFT]: move_tank(player,-2)
        if keys[pygame.K_RIGHT]: move_tank(player,2)
        if keys[pygame.K_UP]: adjust_angle_by_direction(player,1)
        if keys[pygame.K_DOWN]: adjust_angle_by_direction(player,-1)
        if player["charging"]: player["power"] = min(player["power"]+0.3,30)

    if current_turn==ENEMY_TURN and projectile is None: enemy_logic()

    update_projectile()

    draw_tank(player,BLUE)
    draw_tank(enemy,RED)

    draw_move_gauge(player,20,20)
    draw_move_gauge(enemy,WIDTH-180,20)

    text=font.render(f"Player {player['score']} : Enemy {enemy['score']}",True,BLACK)
    screen.blit(text,(WIDTH//2-80,20))

    if current_turn==PLAYER_TURN:
        gx,gy,gauge_width,gauge_height=40,HEIGHT-40,200,20
        pygame.draw.rect(screen,BLACK,(gx,gy,gauge_width,gauge_height),2)
        power_ratio=player["power"]/30
        pygame.draw.rect(screen,BLUE,(gx,gy,gauge_width*power_ratio,gauge_height))
        screen.blit(font.render("POWER",True,BLACK),(gx,gy-22))

    winner=None
    if player["score"]>=5: winner="PLAYER"
    if enemy["score"]>=5: winner="ENEMY"

    if winner:
        win_text=font.render(f"{winner} WIN! Press R to Restart",True,RED if winner=="ENEMY" else BLUE)
        screen.blit(win_text,(WIDTH//2-150,HEIGHT//2))
        pygame.display.flip()
        waiting=True
        while waiting:
            for event in pygame.event.get():
                if event.type==pygame.QUIT: waiting=False;running=False
                if event.type==pygame.KEYDOWN and event.key==pygame.K_r: init_game();waiting=False

    pygame.display.flip()

pygame.quit()
