"""
This program is a space shooter game created using pygame library in Python3.
Player flies a spacship and tries to avoid getting hit by rocks. He can use
laser gun to smash enemies or simply outmaneuver them.
Ship's shields can last several hits, but the bigger the stone is the more
shield hit point player loses.
Moreover, pilot has 3 backup ships (extra lives). After last one is lost
the game is over.
Destroying rocks gives points, the point is to get highest score.
Keep in mind that the difficulty is changing. The longer a player is flying,
the bigger speed rocks have.
"""
import pygame
import random
import time
import pickle
from os import path
# colors
black = (0, 0, 0)
white = (255, 255, 255)
grey = (200, 200, 200)
space_blue = (0, 100, 255)
orange = (255, 140, 0)
# setting game folders
game_folder = path.dirname(__file__)
img_folder = path.join(game_folder, 'assets', 'img')
snd_folder = path.join(game_folder, 'assets', 'snd')
# loading graphics
background_img = pygame.image.load(path.join(
    img_folder, 'Backgrounds\space.png'))
welcome_background_img = pygame.image.load(path.join(
    img_folder, 'Backgrounds\welcome.png'))
player_img = pygame.image.load(path.join(
    img_folder, 'PNG\playerShip1_blue.png'))
shield_img = pygame.image.load(path.join(
    img_folder, 'PNG\Effects\shield1.png'))
life_img = pygame.image.load(path.join(
    img_folder, 'PNG', 'UI\playerLife1_blue.png'))
bullets_images = {}
bullets_images[1] = pygame.image.load(path.join(
    img_folder, 'PNG\Lasers\laserBlue01.png'))
bullets_images[2] = pygame.image.load(path.join(
    img_folder, 'PNG\Lasers\laserRed01.png'))
bullets_images[3] = pygame.image.load(path.join(
    img_folder, 'PNG\Lasers\laserGreen11.png'))
rocks_images = []
rocks_list = ['meteorGrey_big1.png', 'meteorGrey_big2.png',
              'meteorGrey_big3.png', 'meteorGrey_big4.png',
              'meteorGrey_med1.png', 'meteorGrey_med2.png',
              'meteorGrey_small1.png', 'meteorGrey_small2.png',
              'meteorGrey_tiny1.png', 'meteorGrey_tiny1.png']
for img in rocks_list:
    rocks_images.append(pygame.image.load(path.join(
        img_folder, 'PNG\Meteors', img)))
explosion_anim = {}
explosion_anim['bullet'] = []
explosion_anim['player'] = []
explosion_anim['death'] = []
for i in range(9):
    file_name = 'ex{}.png'.format(i)
    img = pygame.image.load(path.join(img_folder, 'PNG\Explosions', file_name))
    img.set_colorkey(black)
    img_large = pygame.transform.scale(img, (75, 75))
    explosion_anim['bullet'].append(img_large)
    img_small = pygame.transform.scale(img, (32, 32))
    explosion_anim['player'].append(img_small)
    file_name = 'death{}.png'.format(i)
    img = pygame.image.load(path.join(img_folder, 'PNG\Explosions', file_name))
    img.set_colorkey(black)
    explosion_anim['death'].append(img)
powerUps_images = {}
powerUps_images['shield'] = pygame.image.load(path.join(
    img_folder, 'PNG', 'Power-ups', 'shield_bronze.png'))
powerUps_images['weapon'] = pygame.image.load(path.join(
    img_folder, 'PNG', 'Power-ups', 'bolt_gold.png'))
# loading sounds
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.mixer.init()
theme_sound = pygame.mixer.music.load(path.join(snd_folder, 'theme.wav'))
pygame.mixer.music.set_volume(0.6)  # sets theme music volume
shoot_sound = pygame.mixer.Sound(path.join(snd_folder, 'pew.wav'))
shoot_sound.set_volume(0.4)
explosion_sounds = []
explosion_list = ['expl1.wav', 'expl2.wav']
for snd in explosion_list:
    explosion_sounds.append(pygame.mixer.Sound(path.join(snd_folder, snd)))
for i in explosion_sounds:
    i.set_volume(0.5)
death_sound = pygame.mixer.Sound(path.join(snd_folder, 'death.wav'))
powerUp_sound = pygame.mixer.Sound(path.join(snd_folder, 'power.wav'))
powerUp_sound.set_volume(2)
# configuration
pygame.init()
pygame.key.set_repeat(50, 50)  # (first delay after press, repetition rate)
fps = pygame.time.Clock()  # fps
playing_area_height = 900  # multiples of grid_size should be used
playing_area_width = 720
text_box_size = 60
pygame.display.set_caption("SpaceFox")
icon = pygame.image.load(path.join(img_folder, 'icon.png'))
icon = pygame.transform.scale(icon, (32, 32))
pygame.display.set_icon(icon)
scr = pygame.display.set_mode((
    playing_area_width, playing_area_height + text_box_size))
win = scr.get_rect()  # window
playing_area = scr.get_rect()
playing_area.h = win.h - text_box_size  # leaving some space for text box
playing_area.bottom = win.bottom
player_y_mov_ratio = 1.3  # describes the ratio of area for player in Y axis
# difficulty - variables used to make the game harder over time
difficulty_timer = 0
diff_min_range = 0  # min speed of rock
diff_max_range = 7  # max speed of rock
period = 10  # period of difficulty upgrades
max_rocks_on_screen = 11
powerUp_chance = 0.93
powerUP_time = 5*1000  # 1000 - 1 second
score_on_rock_kill = 1
score_on_powerUP = 10
# text related variables
# messages
# fonts
myfont = pygame.font.Font('freesansbold.ttf', 48)
myfont2 = pygame.font.Font('freesansbold.ttf', 54)
myfont3 = pygame.font.Font('freesansbold.ttf', 18)
myfont4 = pygame.font.Font('freesansbold.ttf', 14)
mid_msg = myfont.render("======== SpaceFox ========", True, space_blue)
# text boxes
mid_msg_box = mid_msg.get_rect()
mid_msg_box.midtop = win.midtop
mid_msg_box.move(0, 10)
score_msg = myfont.render("00", True, white)
score_box = score_msg.get_rect()
score_box.midtop = mid_msg_box.midbottom
highScore_msg = myfont.render("0000", True, white)
highScore_box = highScore_msg.get_rect()
highScore_box.topright = mid_msg_box.bottomright
# groups
allSprites = pygame.sprite.Group()
rocks = pygame.sprite.Group()
bullets = pygame.sprite.Group()
explosions = pygame.sprite.Group()
powerUps = pygame.sprite.Group()


# classes
class Player(pygame.sprite.Sprite):
    """
    Most important class in the program. It keeps every player related
    variables and mechanics.
    It's responsible for firing the gun, ship movement - also keyboard input,
    shields, scoring, and dying mechanisms.
    """
    def __init__(self, graphic):
        super(Player, self).__init__()
        allSprites.add(self)
        # image
        self.image = graphic.convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 40))
        # rectangle for positioning
        self.rect = self.image.get_rect()
        self.rect.midbottom = playing_area.midbottom
        self.rect.bottom = playing_area.height - 10
        # speed
        self.speedx = 0
        # collisions
        self.radius = int(self.rect.width*.4)  # radius for collisions
        # save
        self.saver = Saver()
        # scoring
        self.score = 0
        self.score_msg = myfont.render(str(self.score), True, white)
        self.highScore = self.saver.getHighscore()
        self.highScore_msg = myfont.render(str(self.highScore), True, grey)
        # shields
        self.shield = 100
        # weapon power
        self.weapon_lvl = 1
        self.weapon_timer = pygame.time.get_ticks()
        # shooting
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        # lives
        self.lives = 4
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()

    def update(self):
        """
        This Function upgrades ships position and takes keyboard input.
        Speed is always set to 0 at the beggining and then it is modified
        by user's input.
        Boundries for ship's movement are also chcecked here.
        At the end there unhide mechanism that brings ship back to the screen
        after death.
        At the end of the ends there is code responsible for timing out
        the weapon power up - it decreases weapon lvl by 1 every 4 seconds
        (can be changed) down to minimum lvl 1.
        """
        # speed
        self.speedx = 0
        self.speedy = 0
        # keyboard input
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        if keystate[pygame.K_UP]:
            self.speedy = -4
        if keystate[pygame.K_DOWN]:
            self.speedy = 4
        if keystate[pygame.K_ESCAPE]:
            self.save()
            finish()
        if keystate[pygame.K_r]:
            self.saver.resetHighscore()
        # actual movement
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        # shooting
        if keystate[pygame.K_SPACE]:
            self.shoot()
        # boundries for movement
        if self.rect.right > playing_area.right:
            self.rect.right = playing_area.right
        if self.rect.left < playing_area.left:
            self.rect.left = playing_area.left
        if not self.hidden:
            if self.rect.bottom > playing_area.bottom:
                self.rect.bottom = playing_area.bottom
            if self.rect.top < playing_area.bottom / player_y_mov_ratio:
                self.rect.top = playing_area.bottom / player_y_mov_ratio
        # unhiding after death
        if self.hidden and pygame.time.get_ticks() -\
        self.hide_timer > 6000 and self.lives > 0:  # 6000 - 1 second at 60 fps
            self.hidden = False
            self.rect.midbottom = playing_area.midbottom
            self.rect.bottom = playing_area.height - 10
        # timing for weapon lvls
        if self.weapon_lvl >= 2 and pygame.time.get_ticks() -\
        self.weapon_timer > powerUP_time:
            self.weapon_lvl -= 1
            self.weapon_timer = pygame.time.get_ticks()

    def shoot(self):
        """
        Function responsible for creating bullets in front of the ship,
        when the laser gun is fired.
        It checks whether the delay is enough to make another shoot and
        if the ship is not hidden.
        3 weapon lvls are defined here
        """
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay and not self.hidden:
            self.last_shot = now
            if self.weapon_lvl == 1:
                bullet = Bullet(
                    self.rect.centerx, self.rect.top, self.weapon_lvl)
            elif self.weapon_lvl == 2:
                bullet1 = Bullet(
                    self.rect.left, self.rect.centery, self.weapon_lvl)
                bullet2 = Bullet(
                    self.rect.right, self.rect.centery, self.weapon_lvl)
            elif self.weapon_lvl >= 3:
                bullet = Bullet(
                    self.rect.centerx, self.rect.top, self.weapon_lvl)
                bullet1 = Bullet(
                    self.rect.left, self.rect.centery, self.weapon_lvl)
                bullet2 = Bullet(
                    self.rect.right, self.rect.centery, self.weapon_lvl)
                bullet1.image = pygame.transform.rotate(bullet1.image, 10)
                bullet1.speedx = -2
                bullet2.image = pygame.transform.rotate(bullet2.image, -10)
                bullet2.speedx = 2
            shoot_sound.play()

    def getBonus(self, hit):
        """
        Function responsible for giving player bonuses depending on the type
        of power up that he obtained.
        Shield - adds shield power up to max Shield depending on the rock size
        from which the power up was dropped.
        Weapon - overpowers weapon to shoot 2 or 3 bullets.
        """
        if hit.type == 'shield':
            self.shield += hit.radius*2.4
            if self.shield >= 100:
                self.shield = 100
        if hit.type == 'weapon':
            self.weapon_lvl += 1
            self.weapon_timer = pygame.time.get_ticks()

    def addScore(self, score):
        """
        This function adds score points to player's total score.
        """
        self.score += score
        self.score_msg = myfont.render(str(self.score), True, white)

    def drawShieldBar(self):
        """
        This function is responsible for drawing UI's element - Shield Bar.
        """
        bar_length = 300
        bar_height = 10
        if self.shield < 0:
            self.shield = 0
        fill = (self.shield / 100) * bar_length
        outline_rect = pygame.Rect(0, 0, bar_length, bar_height)
        fill_rect = pygame.Rect(0, 0, fill, bar_height)
        outline_rect.bottomleft = playing_area.bottomleft
        fill_rect.bottomleft = playing_area.bottomleft
        pygame.draw.rect(scr, space_blue, fill_rect)
        pygame.draw.rect(scr, grey, outline_rect, 2)

    def drawLives(self):
        """
        This function draws small ship icons at the top of the screen
        representing player's remaining lives.
        """
        for i in range(self.lives - 1):
            img_rect = life_img.get_rect()
            img_rect.top = mid_msg_box.bottom
            img_rect.left = mid_msg_box.left + (img_rect.width + 5)*i
            scr.blit(life_img, img_rect)

    def hide(self):
        """
        Function responsible for hiding the ship when it is destroyed -
        "taking it to a safe place", where nothing can hit it.
        It also resets shields and removes 1 from total lives.
        """
        self.lives -= 1
        self.shield = 100
        self.hidden = True
        self_hide_timer = pygame.time.get_ticks()
        # moves the player below the screen where he is "safe"
        self.rect.center = (playing_area.centerx, playing_area.bottom + 200)

    def save(self):
        """
        Function used to save a highscore of a player to a file save.pkl
        located in game's dir.
        """
        self.saver.saveHighscore(self.highScore, self.score)


class Saver:
    """
    Class responsible for saving the highscores and reading them from a file.
    Uses pickle to serialize data.
    """
    def getHighscore(self):
        """
        This function reads highscore froma save.pkl file.
        Returns int(high score).
        """
        f = open("save.pkl", 'rb')
        high_score = pickle.load(f)
        f.close()
        return int(high_score)

    def saveHighscore(self, high_score, current_score):
        """
        This method saves the highest score to a file save.pkl.
        At the beggining it checks whether the new score
        is bigger than previous.
        """
        if high_score < current_score:
            data = current_score
            f = open("save.pkl", 'wb')
            pickle.dump(data, f)
            f.close()

    def resetHighscore(self):
        """
        This function can be used to reset the high score, when needed.
        Overwrites the last high score with 0.
        Visuals apply after round end.
        """
        data = 0
        f = open("save.pkl", 'wb')
        pickle.dump(data, f)
        f.close()


class Bullet(pygame.sprite.Sprite):
    """
    Projecticle class. It describes the bullet properties.
    """
    def __init__(self, x, y, lvl):
        super(Bullet, self).__init__()
        # image
        if lvl > 3:
            lvl = 3
        self.image = bullets_images[lvl].convert_alpha()
        # scales bullets
        # self.image = pygame.transform.scale(self.image, (10, 20))
        # rectangle for positioning
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        # speed
        self.speedy = -10
        self.speedx = 0
        # groups
        allSprites.add(self)
        bullets.add(self)

    def update(self):
        """
        Function responsible for updating the bullet's position.
        Boundries are also set here.
        If the bullet leaves screen it gets killed.
        """
        # movement
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        # kill if it moves off the top of the screen
        if self.rect.bottom < playing_area.top:
            self.kill()


class Rock(pygame.sprite.Sprite):
    """
    Enemy class is every enemy that player encounters.
    At this stage it is used only for creating rocks.
    Enemies are spawned outside of the playing area to get rid of
    poping objects out of nowhere.
    """
    def __init__(self):
        super(Rock, self).__init__()
        # image
        self.image_orig = random.choice(rocks_images).convert_alpha()
        self.image = self.image_orig.copy()
        # rectangle for positioning
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(playing_area_width - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        # speed
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        # collisions
        self.radius = int(self.rect.width*.85 / 2)  # radius for collisions
        # rotation
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()
        # groups
        allSprites.add(self)
        rocks.add(self)

    def update(self):
        """44
        Function responsible for updating the enemy's state.
        It allows the object to move, perform animations etc.
        Boundries and effects of leaving the screen are set here.
        When a rock leaves the playing area it is not killed -
        it is respawned at the top with different attributes.
        """
        # rotation
        self.rotate()
        # movement
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        # leaving the screen
        if self.rect.top > playing_area_height + 10 or self.rect.left <\
        playing_area.left - self.rect.width or self.rect.right >\
        playing_area_width + self.rect.width:
            self.rect.x = random.randrange(
                playing_area_width - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedx = random.randrange(-3, 3)
            self.speedy = random.randrange(diff_min_range, diff_max_range)
            self.rot_speed = random.randrange(-8, 8)

    def rotate(self):
        """
        Function responsible for rock rotation animation.
        It has to recalculate image's center every time a rotation occurs
        in order to keep animation smooth and nice.
        """
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center


class Explosion(pygame.sprite.Sprite):
    """
    Class responsible for explosion effects.
    It's initializer takes argument based on the type of the explosion.
    'bullet' - is when a bullet collide with the rock
    'player' - rock hits player
    'death'  - player dies
    """
    def __init__(self, center, size):
        super(Explosion, self).__init__()
        # type
        self.size = size
        # image
        self.image = explosion_anim[self.size][0]
        # rectangle for positioning
        self.rect = self.image.get_rect()
        self.rect.center = center
        # animation
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50
        # sound
        if size == 'death':
            death_sound.play()
        else:
            random.choice(explosion_sounds).play()
        # groups
        allSprites.add(self)
        explosions.add(self)

    def update(self):
        """
        Function responsible for animation of the explosion and
        for it's positioning.
        After there are no more explosion frames to be displayed
        it kills the explosion Sprite.
        """
        now = pygame.time.get_ticks()
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


class ShieldBlit(pygame.sprite.Sprite):
    """
    Class responsible for handling the shield "got hit effect".
    """
    def __init__(self, player):
        super(ShieldBlit, self).__init__()
        self.player = player
        # image
        self.image = shield_img.convert_alpha()
        # rectangle for positioning
        self.rect = self.image.get_rect()
        self.rect.center = player.rect.center
        # animation
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50
        # groups
        allSprites.add(self)

    def follow_ship(self):
        """
        Allows the shield to follow the ship instead of staying in place.
        """
        self.rect.center = self.player.rect.center

    def update(self):
        """
        Function responsible for updating the visuals of the shield and
        for killing it when it's time.
        Also invokes the follow_ship() method.
        """
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == 10 or not self.player.alive():
                self.kill()
            else:
                self.follow_ship()


class EnemyFactory:
    """
    Simple class responsible for creating enemy units.
    """
    def spawn_Rock(self, number):
        """
        Creates instances of rock Sprite.
        """
        for i in range(number):
            r = Rock()


class Power(pygame.sprite.Sprite):
    def __init__(self, center):
        super(Power, self).__init__()
        # type
        self.type = random.choice(['shield', 'weapon'])
        # image
        self.image = powerUps_images[self.type].convert_alpha()
        # rectangle for positioning
        self.rect = self.image.get_rect()
        self.rect.center = center
        # speed
        self.speedy = 2
        # collisions
        self.radius = int(self.rect.width*.85 / 2)  # radius for collisions
        # groups
        allSprites.add(self)
        powerUps.add(self)

    def update(self):
        """
        Function responsible for movement of power ups
        and for their disappearing after they reach end of the screen.
        """
        # movement
        self.rect.y += self.speedy
        # kills if it moves off the bottom of the screen
        if self.rect.top > playing_area.bottom:
            self.kill()


# functions
def welcome_screen():
    """
    Displays a welcome screen containing the game's title,
    used programming language and author's initials.
    """
    scr.fill(black)
    background = pygame.transform.scale(
        welcome_background_img, (win.width, win.height))
    scr.blit(background, win)

    welcome = myfont2.render("Welcome to", True, black)
    welcome_box = welcome.get_rect()
    welcome_box.topleft = win.center
    scr.blit(welcome, welcome_box)

    welcome2 = myfont2.render("SpaceFox!", True, black)
    welcome2_box = welcome2.get_rect()
    welcome2_box.topright = welcome_box.bottomright
    scr.blit(welcome2, welcome2_box)

    welcome3 = myfont3.render("Made in Python by ML", True, orange)
    welcome3_box = welcome3.get_rect()
    welcome3_box.topright = welcome2_box.bottomright
    scr.blit(welcome3, welcome3_box)
    pygame.display.flip()
    pygame.time.wait(2500)


def starting_screen(current_score, high_score):
    """
    Function displays introduction to the game telling user how to control
    the ship and some other basis of the game.
    The method takes two int arguments representing the scores in order to
    display player's score if it wasn't the first round and the
    current highest score.
    It waits for player to tap a button or to quit (also by clicking ESC).
    """
    scr.blit(welcome_background_img, win)

    title = myfont.render("SpaceFox", True, space_blue)
    title_box = title.get_rect()
    title_box.midtop = win.midtop
    scr.blit(title, title_box)

    ship_preview = player_img.get_rect()
    ship_preview.center = playing_area.center
    ship_preview.centery += 200
    scr.blit(player_img, ship_preview)

    weapon_preview = powerUps_images['weapon'].get_rect()
    weapon_preview.centerx = (playing_area.left + ship_preview.centerx)/2
    weapon_preview.centery = ship_preview.centery
    scr.blit(powerUps_images['weapon'], weapon_preview)

    shield_preview = powerUps_images['shield'].get_rect()
    shield_preview.centerx = (playing_area.right + ship_preview.centerx)/2
    shield_preview.centery = ship_preview.centery
    scr.blit(powerUps_images['shield'], shield_preview)

    weapon_msg = myfont4.render("Weapon overcharge", True, grey)
    weapon_box = weapon_msg.get_rect()
    weapon_box.top = weapon_preview.bottom + 10
    weapon_box.centerx = weapon_preview.centerx
    scr.blit(weapon_msg, weapon_box)

    shield_msg = myfont4.render("Shield regeneration", True, grey)
    shield_box = shield_msg.get_rect()
    shield_box.top = shield_preview.bottom + 10
    shield_box.centerx = shield_preview.centerx
    scr.blit(shield_msg, shield_box)

    instructions = myfont3.render(
        "Use ARROW keys to maneuver your ship", True, white)
    instructions_box = instructions.get_rect()
    instructions_box.midtop = ship_preview.midbottom
    instructions_box.centery += 100
    scr.blit(instructions, instructions_box)

    instructions2 = myfont3.render(
        "Press SPACE in order to fire from the mounted laser gun", True, white)
    instructions2_box = instructions2.get_rect()
    instructions2_box.midtop = instructions_box.midbottom
    scr.blit(instructions2, instructions2_box)

    instructions3 = myfont3.render(
        "You will have 3 ships in reserve, but be carefull!", True, white)
    instructions3_box = instructions3.get_rect()
    instructions3_box.midtop = instructions2_box.midbottom
    scr.blit(instructions3, instructions3_box)

    instructions4 = myfont3.render(
        "Your shields drop faster, when you get hit by a bigger object...",
        True, white)
    instructions4_box = instructions4.get_rect()
    instructions4_box.midtop = instructions3_box.midbottom
    scr.blit(instructions4, instructions4_box)

    score = myfont2.render(
        "Your score: " + str(current_score),
        True, white)
    score_box = score.get_rect()
    score_box.center = win.center
    if current_score > 0:  # condition eliminating blitting the message at 0 pt
        scr.blit(score, score_box)

    score2 = myfont2.render(
        "Highest score: " + str(high_score),
        True, grey)
    score2_box = score2.get_rect()
    score2_box.midtop = score_box.midbottom
    scr.blit(score2, score2_box)

    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finish()
            if event.type == pygame.KEYUP:
                waiting = False
                if current_score != 0:
                    pygame.time.wait(3000)  # to prevent auto restart


def finish():
    """
    Displays the endgame screen.
    After that quits the game.
    """
    scr.blit(welcome_background_img, win)
    mid_msg = myfont.render("Thank you for playing!", True, white)
    mid_msg_box = mid_msg.get_rect()
    mid_msg_box.center = win.center
    scr.blit(mid_msg, mid_msg_box)
    pygame.display.flip()
    pygame.time.wait(1000)
    quit()


def track_difficulty():
    """
    Function keeps track of difficulty. Every 10 seconds min and max speed
    for rocks is getting faster.
    Moreover the more rocks player avoids, the more faster rocks will come,
    due to resetting rocks position and properties instead of spawning
    after leaving playing_area.
    Newly spawned rock will get base speed on its first run.
    There is also an option to increase the number of metheors over time
    (uncomment to enable).
    """
    global difficulty_timer
    global diff_min_range
    global diff_max_range
    now = time.time()
    if now - difficulty_timer > period:
        diff_min_range += 1
        diff_max_range += 1
        # temp = EnemyFactory().spawn_Rock(1)
        difficulty_timer = now


def reset_difficulty():
    """
    Function resets all difficulty related variables.
    Used when a new round is beggining.
    """
    global difficulty_timer
    global diff_min_range
    global diff_max_range
    difficulty_timer = 0
    diff_min_range = 0
    diff_max_range = 7


def main():
    player = Player(player_img)
    # player.saver.resetHighscore()  # Can be used to reset the high score
    rocksFactory = EnemyFactory()
    pygame.mixer.music.play(loops=-1)  # playing theme song
    welcome_screen()
    # main loop
    game_over = True
    running = True
    while (running):
        # at the beggining of a new round
        if game_over:
            player.save()
            starting_screen(player.score, player.highScore)
            difficulty_timer = time.time()
            game_over = False
            allSprites.empty()
            rocks.empty()
            bullets.empty()
            explosions.empty()
            # powerups.empty()
            player = Player(player_img)
            reset_difficulty()
            rocksFactory.spawn_Rock(max_rocks_on_screen)
        # event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                player.save()
                finish()
        # updating
        allSprites.update()
        track_difficulty()
        # player-rock collisions
        # lists sprites that collided with player
        hits = pygame.sprite.spritecollide(
            player, rocks, True, pygame.sprite.collide_circle)
        # False determines whether player kills the rock on collision
        for hit in hits:
            player.shield -= hit.radius*1.85  # dmg multiplier
            explosion = Explosion(hit.rect.center, 'player')
            blit = ShieldBlit(player)
            rocksFactory.spawn_Rock(2)
            if player.shield <= 0:
                death = Explosion(player.rect.center, 'death')
                player.hide()
        # bullet-rock collisions
        bulletHits = pygame.sprite.groupcollide(rocks, bullets, True, True)
        for hit in bulletHits:
            explosion = Explosion(hit.rect.center, 'bullet')
            rocksFactory.spawn_Rock(1)
            player.addScore(score_on_rock_kill)
            # random picks decimal 0<x<1 so 0.9 is 10% chance
            if random.random() > powerUp_chance:
                pow = Power(hit.rect.center)
        # player - powerUp collisions
        powerUpHits = pygame.sprite.spritecollide(
            player, powerUps, True, pygame.sprite.collide_circle)
        for hit in powerUpHits:
            player.getBonus(hit)
            player.addScore(score_on_powerUP)
            powerUp_sound.play()
        # stopping after player ran out of lives
        if player.lives == 0 and not explosions:
            game_over = True

        # drawing
        scr.fill(black)  # resetting screen
        scr.blit(background_img, win)  # background
        allSprites.draw(scr)  # drawing all sprites
        player.drawShieldBar()  # drawing UI
        player.drawLives()  # drawing UI
        scr.blit(mid_msg, mid_msg_box)  # title box
        scr.blit(player.score_msg, score_box)  # drawing player's current score
        scr.blit(player.highScore_msg, highScore_box)

        pygame.display.flip()
        fps.tick(70)  # fps rate
    finish()

if __name__ == "__main__":
    main()
