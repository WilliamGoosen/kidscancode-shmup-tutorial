# -*- coding: utf-8 -*-
"""
Created on Sat Aug 12 14:15:40 2023

@author: William
"""
# Shmup! game
# Frozen Jam by tgfcoder <https://twitter.com/tgfcoder> licensed under CC-BY-3
# <http://creativecommons.org/licenses/by/3.0/>
# Art from Kenney.nl
import pygame as pg
from random import random, randrange, choice
from os import path
from sys import exit
from settings import *

img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'snd')

# Initialize pygame and create window
pg.init()
pg.mixer.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption(TITLE)
clock = pg.time.Clock()

font_name = pg.font.match_font(FONT_NAME)


def draw_text(surf, text, size, x, y):
    font = pg.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)


def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
    pg.draw.rect(surf, GREEN, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2)


def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)

def should_continue_waiting():
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()   

        if event.type == pg.KEYDOWN:
            # A key was PRESSED. Now let's see which one.
            if event.key == pg.K_ESCAPE:
                # Specifically, the ESC key was pressed. Quit.
                pg.quit()
                exit()                    
            else:
                # Any other key (Space, Enter, etc.) was pressed. Start the game.
                return False
    return True    

def show_waiting_screen(*draw_callbacks):
    """
    A generic screen that waits for user input.
    
    Parameters:
        *draw_callbacks: One or more functions to call each frame to draw the screen.
                         These are "callbacks" - we pass them in to be called later.
    """
    waiting = True
    while waiting:
        waiting = should_continue_waiting()

        screen.blit(background, background_rect)

        for draw_callback in draw_callbacks:
            draw_callback()

        pg.display.flip()
        clock.tick(FPS)

def draw_start_title():
    """Callback function to draw the title for the start screen."""
    draw_text(screen, "SHMUP!", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "Arrow keys move, Space to fire", 22, WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "Press a key to begin", 18, WIDTH / 2, HEIGHT * 3 / 4)

def draw_start_highscore():
    """Callback function to draw the high score for the start screen."""
    draw_text(screen, "High Score: " + str(player.highscore), 22, WIDTH / 2, 15)

def draw_game_over_title():
    """Callback function to draw the title for the game over screen."""
    draw_text(screen, "GAME OVER", 48, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "Score: " + str(score), 22, WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "Press a key to play again", 18, WIDTH / 2, HEIGHT * 3 / 4)

def show_start_screen():
    """Shows the start screen by using the generic waiting screen with specific draw functions."""
    show_waiting_screen(draw_start_title, draw_start_highscore)


def show_game_over_screen():
    """Shows the game over screen by using the generic waiting screen with specific draw functions."""
    new_high_score_achieved = False
    if score > player.highscore:
        player.highscore = score
        new_high_score_achieved = True
        with open(path.join(player.dir, HS_FILE), "w") as f:
            f.write(str(score))

    def draw_game_over_highscore():
        """Callback function to draw the high score for the game over screen."""
        if new_high_score_achieved:
            draw_text(screen, "NEW HIGH SCORE!", 22, WIDTH / 2, HEIGHT / 2 + 40)        
        else:
            draw_text(screen, "High Score: " + str(player.highscore), 22, WIDTH / 2, HEIGHT / 2 + 40)


    show_waiting_screen(draw_game_over_title, draw_game_over_highscore)


class Player(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pg.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pg.time.get_ticks()
        self.power = 1
        self.power_time = pg.time.get_ticks()
        self.load_data()
      
    def load_data(self):
        self.dir = path.dirname(__file__)
        # Create the full path to the highscore file
        hs_file_path = path.join(self.dir, HS_FILE)

        # Check if the file exists first
        if path.exists(hs_file_path):
            # If it exists, open it and try to read the score
            try:
                with open(hs_file_path, 'r') as f:
                    self.highscore = int(f.read())
            except ValueError:
                # This happens if the file exists but is empty/corrupt (not a number)
                self.highscore = 0
        else:
            # If the file does NOT exist, set highscore to 0
            self.highscore = 0

        # (Optional) Now you can write the score back to the file to create it if it was missing or corrupt.
        with open(hs_file_path, 'w') as f:
            f.write(str(self.highscore))

    def update(self):
        # timeout for powerups
        if self.power >= 2 and pg.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pg.time.get_ticks()

        # unhide if hidden
        if self.hidden and pg.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10
            for i in range(8):
                newmob()

        self.speedx = 0
        keystate = pg.key.get_pressed()
        if keystate[pg.K_LEFT]:
            self.speedx = -8
        if keystate[pg.K_RIGHT]:
            self.speedx = 8
        if keystate[pg.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def powerup(self):
        self.power += 1
        self.power_time = pg.time.get_ticks()

    def shoot(self):
        if not self.hidden:
            now = pg.time.get_ticks()
            if now - self.last_shot > self.shoot_delay:
                self.last_shot = now
                if self.power == 1:
                    bullet = Bullet(self.rect.centerx, self.rect.top)
                    all_sprites.add(bullet)
                    bullets.add(bullet)
                    shoot_sound.play()
                if self.power == 2:
                    bullet_l = Bullet(self.rect.left, self.rect.centery)
                    bullet_r = Bullet(self.rect.right, self.rect.centery)
                    all_sprites.add(bullet_l)
                    all_sprites.add(bullet_r)
                    bullets.add(bullet_l)
                    bullets.add(bullet_r)
                    shoot_sound.play()
                if self.power >= 3:
                    bullet = Bullet(self.rect.centerx, self.rect.top)
                    bullet_l = Bullet(self.rect.left, self.rect.centery)
                    bullet_r = Bullet(self.rect.right, self.rect.centery)
                    all_sprites.add(bullet)
                    all_sprites.add(bullet_l)
                    all_sprites.add(bullet_r)
                    bullets.add(bullet)
                    bullets.add(bullet_l)
                    bullets.add(bullet_r)
                    shoot_sound.play()

    def hide(self):
        # hide the player temporarily
        self.hidden = True
        self.hide_timer = pg.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)


class Mob(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image_orig = choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 / 2)
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = randrange(WIDTH - self.rect.width)
        self.rect.y = randrange(-150, -100)
        self.speedy = randrange(1, 8)
        self.speedx = randrange(-3, 3)
        self.rot = 0
        self.rot_speed = randrange(-8, 8)
        self.last_update = pg.time.get_ticks()

    def rotate(self):
        now = pg.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pg.transform.rotate(self.image_orig, self.rot).convert_alpha()
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.left < -self.rect.width or self.rect.right > WIDTH + self.rect.width:
            self.rect.x = randrange(WIDTH - self.rect.width)
            self.rect.y = randrange(-100, -40)
            self.speedy = randrange(1, 8)


class Boss(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image_orig = boss_lrg_img
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 1.2 / 2)
        pg.draw.circle(self.image, RED, self.rect.center, self.radius, width=2)
        self.rect.midbottom = (WIDTH / 2, -self.rect.height)
        self.speedx = 0
        self.speedy = 0
        self.shoot_delay = 750
        self.last_shot = pg.time.get_ticks()
        self.life = 100
        self.rot = 0
        self.rot_speed = 90
        self.last_update = pg.time.get_ticks()

    def rotate(self):
        now = pg.time.get_ticks()
        if now - self.last_update > 500:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pg.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        if score > 75000:
            self.speedy = 3
            for meteor in mobs:
                hit_sound = choice(expl_sounds)
                hit_sound.play()
                hit_sound.set_volume(0.2)
                expl = Explosion(meteor.rect.center, 'lg')
                all_sprites.add(expl)
                meteor.kill()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.bottom > int(self.rect.height / 2):
            self.rect.bottom = int(self.rect.height / 2)
            self.speedy = 0
        if self.speedy == 0 and self.rect.bottom == int(self.rect.height / 2):
            self.shoot()
            if self.speedx == 0:
                self.speedx = 1
        if self.rect.right > WIDTH:
            # self.rect.right = WIDTH
            self.speedx = -self.speedx
        if self.rect.left < 0:
            self.rect.left = 0
            self.speedx = -self.speedx

    def shoot(self):
        now = pg.time.get_ticks()
        # shooting = randrange(self.shoot_delay - 800, self.shoot_delay)
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now  # + randrange(-self.shoot_delay + 100, 0)
            bullet_c = Bullet(self.rect.centerx, self.rect.bottom)
            bullet_c.speedy = 5
            bullet_l = Bullet(self.rect.centerx - 0.7 * self.radius, self.rect.bottom - 0.3 * self.radius)
            bullet_l.speedy = 5
            bullet_r = Bullet(self.rect.centerx + 0.7 * self.radius, self.rect.bottom - 0.3 * self.radius)
            bullet_r.speedy = 5
            all_sprites.add(bullet_c)
            all_sprites.add(bullet_l)
            all_sprites.add(bullet_r)
            boss_bullets.add(bullet_c)
            boss_bullets.add(bullet_l)
            boss_bullets.add(bullet_r)
            shoot_sound.play()


class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 / 2)
        pg.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        # kill if it moves off the top of the screen
        if self.rect.bottom < 0:
            self.kill()


class Power(pg.sprite.Sprite):
    def __init__(self, center):
        pg.sprite.Sprite.__init__(self)
        self.type = choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 4

    def update(self):
        self.rect.y += self.speedy
        # kill if it moves off the top of the screen
        if self.rect.top > HEIGHT:
            self.kill()


class Explosion(pg.sprite.Sprite):
    def __init__(self, center, size):
        pg.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pg.time.get_ticks()
        self.frame_rate = 35

    def update(self):
        now = pg.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
        if self.frame == len(explosion_anim[self.size]):
            self.kill()
        else:
            center = self.rect.center
            self.image = explosion_anim[self.size][self.frame]
            self.rect = self.image.get_rect()
            self.rect.center = center


# Load all game graphics
background = pg.image.load(path.join(img_dir, "starfield.png")).convert_alpha()
background_rect = background.get_rect()
player_img = pg.image.load(path.join(img_dir, "playerShip1_orange.png")).convert_alpha()
player_mini_img = pg.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
bullet_img = pg.image.load(path.join(img_dir, "laserRed16.png")).convert_alpha()
boss_img = pg.image.load(path.join(img_dir, "ufoRed.png")).convert_alpha()
boss_lrg_img = pg.transform.scale(boss_img, (273, 273)).convert_alpha()
meteor_images = []
meteor_list = ['meteorBrown_big1.png', 'meteorBrown_big2.png', 'meteorBrown_big3.png', 'meteorBrown_big4.png',
               'meteorBrown_med1.png', 'meteorBrown_med3.png', 'meteorBrown_small1.png', 'meteorBrown_small2.png',
               'meteorBrown_tiny1.png', 'meteorBrown_tiny2.png']
for img in meteor_list:
    img_surface = pg.image.load(path.join(img_dir, img)).convert_alpha()
    img_surface.set_colorkey(BLACK)
    meteor_images.append(img_surface)

explosion_anim = {'lg': [], 'sm': [], 'player': [], 'boss': []}
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pg.image.load(path.join(img_dir, filename)).convert_alpha()
    img.set_colorkey(BLACK)
    img_lg = pg.transform.scale(img, (75, 75)).convert_alpha()
    explosion_anim['lg'].append(img_lg)
    img_sm = pg.transform.scale(img, (60, 60)).convert_alpha()
    explosion_anim['sm'].append(img_sm)
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pg.image.load(path.join(img_dir, filename)).convert_alpha()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)
    img_boss_explode = pg.transform.scale(img, (298, 302))
    explosion_anim['boss'].append(img_boss_explode)

powerup_images = {}
powerup_images['shield'] = pg.image.load(path.join(img_dir, 'shield_gold.png')).convert_alpha()
powerup_images['gun'] = pg.image.load(path.join(img_dir, 'bolt_gold.png')).convert_alpha()

# Load all game sounds
shoot_sound = pg.mixer.Sound(path.join(snd_dir, "Laser_Shoot2.wav"))
shoot_sound.set_volume(0.2)
shield_sound = pg.mixer.Sound(path.join(snd_dir, "pow4.wav"))
power_sound = pg.mixer.Sound(path.join(snd_dir, "pow5.wav"))
life_up_sound = pg.mixer.Sound(path.join(snd_dir, "jingles_NES09.ogg"))
expl_sounds = []
for snd in ['Explosion1.wav', 'Explosion2.wav']:
    expl_sounds.append(pg.mixer.Sound(path.join(snd_dir, snd)))
player_die_sound = pg.mixer.Sound(path.join(snd_dir, 'rumble1.ogg'))
pg.mixer.music.load(path.join(snd_dir, 'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
pg.mixer.music.set_volume(0.2)

all_sprites = pg.sprite.Group()
mobs = pg.sprite.Group()
bullets = pg.sprite.Group()
bosses = pg.sprite.Group()
boss_bullets = pg.sprite.Group()
powerups = pg.sprite.Group()
player = Player()
boss = Boss()
bosses.add(boss)
all_sprites.add(boss)
all_sprites.add(player)
for i in range(8):
    newmob()
score = 0
life_gained = 0
pg.mixer.music.play(loops=-1)
show_start_screen()

# Game loop
game_over = False
running = True
while running:

    if game_over:

        show_game_over_screen()
        game_over = False
        all_sprites = pg.sprite.Group()
        mobs = pg.sprite.Group()
        bullets = pg.sprite.Group()
        bosses = pg.sprite.Group()
        boss_bullets = pg.sprite.Group()
        powerups = pg.sprite.Group()
        player = Player()
        boss = Boss()
        bosses.add(boss)
        all_sprites.add(boss)
        all_sprites.add(player)
        for i in range(8):
            newmob()
        score = 0
        life_gained = 0
        # keep loop running at the right speed
    clock.tick(FPS)

    # Process input (events)
    for event in pg.event.get():
        # check for closing the window
        if event.type == pg.QUIT:
            running = False

            # Update
    all_sprites.update()

    # check to see if a bullet hit a mob
    hits = pg.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += 62 - hit.radius
        hit_sound = choice(expl_sounds)
        hit_sound.play()
        hit_sound.set_volume(0.2)
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if random() > 0.9:
            power = Power(hit.rect.center)
            all_sprites.add(power)
            powerups.add(power)
        newmob()

    # check to see if a bullet hit boss
    boss_hits = pg.sprite.groupcollide(bullets, bosses, True, False, pg.sprite.collide_circle)
    for hit in boss_hits:
        hit_sound = choice(expl_sounds)
        hit_sound.play()
        hit_sound.set_volume(0.2)
        expl = Explosion(hit.rect.midtop, 'sm')
        all_sprites.add(expl)
        boss.life -= 2
        if random() > 0.95:
            power = Power(hit.rect.center)
            all_sprites.add(power)
            powerups.add(power)

        if boss.life <= 0:
            player_die_sound.play()
            # player_die_sound.set_volume(0.2)
            death_explosion = Explosion(boss.rect.center, 'boss')
            all_sprites.add(death_explosion)
            boss.kill()
            for i in range(8):
                newmob()

    # check to see if a boss bullet hit player
    hits = pg.sprite.spritecollide(player, boss_bullets, True)
    for hit in hits:
        hit_sound = choice(expl_sounds)
        hit_sound.play()
        hit_sound.set_volume(0.2)
        player.shield -= 10
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)

        if player.shield <= 0:
            player_die_sound.play()
            player_die_sound.set_volume(0.2)
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = 100

    # check to see if a mob hits the player
    hits = pg.sprite.spritecollide(player, mobs, True, pg.sprite.collide_circle)
    for hit in hits:
        hit_sound = expl_sounds[0]
        hit_sound.play()
        hit_sound.set_volume(0.2)
        player.power = 1
        player.shield -= hit.radius * 2
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        newmob()

        if player.shield <= 0:
            player_die_sound.play()
            player_die_sound.set_volume(0.2)
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player.hide()
            for meteor in mobs:
                meteor.kill()
            player.lives -= 1
            player.shield = 100

    # check to see if player hit a powerup
    hits = pg.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'shield':
            player.shield += randrange(10, 30)
            shield_sound.play()
            if player.shield >= 100:
                player.shield = 100
        if hit.type == 'gun':
            player.powerup()
            power_sound.play()

    # if the player died and the explosion has finished playing
    if player.lives == 0 and not death_explosion.alive():
        game_over = True

    if score > 25000 and life_gained == 0:
        life_gained = 25000
        player.lives += 1
        life_up_sound.play()
    if score > 50000 and life_gained == 25000:
        life_gained = 50000
        player.lives += 1
        life_up_sound.play()

    # Draw / render
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, "Score: " + str(score), 18, WIDTH / 2, 10)
    draw_shield_bar(screen, WIDTH - 105, 5, player.shield)
    draw_lives(screen, 5, 5, player.lives, player_mini_img)
    # *after* drawing everything, flip the display
    pg.display.flip()

pg.quit()
