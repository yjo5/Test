import pygame
import random

# --- Settings ---
WIDTH, HEIGHT = 600, 800
PLAYER_SPEED = 5
BULLET_SPEED = 8
ENEMY_SPEED = 3
SPAWN_RATE = 30  # frames

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Shooting Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# --- Player ---
player = pygame.Rect(WIDTH // 2 - 25, HEIGHT - 60, 50, 40)

# --- Game objects ---
bullets = []
enemies = []
frame_count = 0
score = 0
running = True


def draw_text(text, x, y):
    img = font.render(text, True, (255, 255, 255))
    screen.blit(img, (x, y))


while running:
    clock.tick(60)
    frame_count += 1

    # --- Events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # Player movement
    if keys[pygame.K_LEFT] and player.left > 0:
        player.x -= PLAYER_SPEED
    if keys[pygame.K_RIGHT] and player.right < WIDTH:
        player.x += PLAYER_SPEED

    # Shoot
    if keys[pygame.K_SPACE]:
        if len(bullets) < 5:
            bullets.append(pygame.Rect(player.centerx - 5, player.top, 10, 20))

    # Spawn enemies
    if frame_count % SPAWN_RATE == 0:
        x_pos = random.randint(0, WIDTH - 40)
        enemies.append(pygame.Rect(x_pos, -40, 40, 40))

    # Move bullets
    for bullet in bullets[:]:
        bullet.y -= BULLET_SPEED
        if bullet.bottom < 0:
            bullets.remove(bullet)

    # Move enemies
    for enemy in enemies[:]:
        enemy.y += ENEMY_SPEED
        if enemy.top > HEIGHT:
            enemies.remove(enemy)

    # Collision
    for enemy in enemies[:]:
        for bullet in bullets[:]:
            if enemy.colliderect(bullet):
                enemies.remove(enemy)
                bullets.remove(bullet)
                score += 1
                break

        # Game over if enemy hits player
        if enemy.colliderect(player):
            running = False

    # --- Draw ---
    screen.fill((20, 20, 30))

    pygame.draw.rect(screen, (0, 200, 255), player)

    for bullet in bullets:
        pygame.draw.rect(screen, (255, 255, 0), bullet)

    for enemy in enemies:
        pygame.draw.rect(screen, (255, 80, 80), enemy)

    draw_text(f"Score: {score}", 10, 10)

    pygame.display.flip()


# --- Game over screen ---
pygame.quit()
print("Game Over! Score:", score)

