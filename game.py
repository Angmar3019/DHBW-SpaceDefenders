""" Space Defenders - Pixel space ship game

    author:  Angmar3019
    date:    04.06.2023
    version: 1.0.0
    licence: GNU General Public License v3.0 
"""


import sys
import os
import math
import random
import sqlite3

from loguru import logger
logger.add("game.log")

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame
from pygame.locals import *
pygame.init()
clock = pygame.time.Clock()
clock.tick(60)

def create_database():
    """Create Database
        - Creates the database "highscore" with an ID and a score.
        - Prefills the database table with three entries with the value zero

        Tests:
            - Check if the folder "db" and the file "highscore.db" have been created
            - Check if the scoreboard has three entries with zero
    """
    if not os.path.exists('./db/'):
        os.makedirs("./db")
    db_highscore = "./db/highscore.db" 
    db_com = sqlite3.connect(db_highscore)
    db_cur = db_com.cursor()

    db_cur.execute("CREATE TABLE IF NOT EXISTS highscore (id INT AUTO_INCREMENT PRIMARY KEY, score INTEGER)")
    db_cur.execute("INSERT INTO highscore (score) VALUES ('0'),('0'),('0')")
    db_com.commit()

    logger.info("Database created and initialized")

if not os.path.exists('./db/highscore.db'):
    create_database()

db_highscore = "./db/highscore.db" 
db_com = sqlite3.connect(db_highscore)
db_cur = db_com.cursor()
logger.info("Database loaded")

windowwidth = 1280
windowheight = 720

class Window(pygame.sprite.Sprite):
    def __init__(self, x):
        """Window 
        - Creates a sprite for the window border
        - Sprite is a rect with an offset in the respective direction of the border

        Test:
            - Check if the bullet number decreases when the bullet hits the right window border
            - Check if the meteorite number decreases when the meteorite hits the left window border
        """
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(x, 0, 11, windowheight)

window_left = Window(-96)
window_right = Window(windowwidth + 96)

screen = pygame.display.set_mode((windowwidth, windowheight))



class Image_List():
    def __init__(self, array, size_x, size_y, dir):
        """Image List
        - Adds images to a given array
        - Images are converted and resized beforehand

        Args:
            - array (array): Array in which the images are to be appended
            - size_x (int):  Desired width of image
            - size_y (int):  Desired height of image
            - dir (str):     Folder in which the images to be imported are located

        Test:
            - Check log if all images from the directory are loaded
            - Check array if all images from the directory are loaded
        """
        for self.file in sorted(os.listdir(dir)):
            self.image_import = pygame.image.load(dir + self.file).convert_alpha()
            self.image = pygame.transform.scale(self.image_import, (size_x, size_y))
            array.append(self.image)
            logger.info('Image loaded "' + dir + self.file + '"')



class Text():
    def __init__(self, text, font, text_size):
        """Text
        - Renders a text with the desired font and font size

        Args:
            - text (str):      Desired text which should be displayed
            - front(str):      Desired font, e.g. "silkscreen-bold.ttf"
            - text_size (int): Desired font size

        Test:
            - Check log if all text entities are loaded
            - Check if object is created
        """
        self.font = pygame.font.Font(font, text_size)
        self.surface = self.font.render(text, True, (255,255,255))
        self.rect = self.surface.get_rect()
        logger.info('Text "' + text + '" loaded')

    def draw(self, x, y):
        """Draw text
        - Draws the pre-rendered text to a specified position

        Args:
            - x (int): X-coordinate where the text should be placed
            - y (int): Y-coordinate where the text should be placed

        Test:
            - Check if text is rendered
            - Check if correct font and size is used
        """
        self.rect.topleft = (x, y)
        screen.blit(self.surface, self.rect)



class Button():
    def __init__(self, text, width, height, image, image_hover):
        """Button
        - Renders a button
        - Places a given text with Text() inside the button
        - Also loads another image for each button to create a hover effect

        Args:
            - text (str):        Desired text which should be displayed inside the button
            - width (int):       Desired width of the button
            - height (int):      Desired height of the button
            - image (str):       Dir path of the image for the button
            - image_hover (str): Dir path of the hover image for the button

        Test:
            - Check log if all buttons are loaded
            - Check if object is created
        """
        self.width = width
        self.height = height
        self.text = text
        self.image_import = pygame.image.load(image).convert_alpha()
        self.image_hover_import = pygame.image.load(image_hover).convert_alpha()
        self.image = pygame.transform.scale(self.image_import, (width, height))
        self.image_hover = pygame.transform.scale(self.image_hover_import, (width, height))
        self.hover = False
        self.rect = self.image.get_rect()
               
        self.button_text = Text(self.text, "./assets/fonts/silkscreen-regular.ttf", 20)

        logger.info('Button "' + self.text + '" with images "' + image + " and " + image_hover + " loaded")
    
    def draw(self, x, y):
        """Draw button
        - Draws the pre-defined button to a specified position
        - If the button has the value "hover == True", it should render another button

        Args:
            - x (int): X-coordinate where the text should be placed
            - y (int): Y-coordinate where the text should be placed

        Test:
            - Check if button is rendered
            - Check if correct font and button image is used
            - Check if the hover effect is working
        """
        self.rect.topleft = (x, y)

        if self.hover:
            screen.blit(self.image_hover, (self.rect.x , self.rect.y))
        else: 
            screen.blit(self.image, (self.rect.x , self.rect.y))

        self.button_text.draw(x + (self.width - self.button_text.surface.get_width())/2, y + (self.height - self.button_text.surface.get_height())/2)



class Menu():
    def __init__(self):
        """Initialize menu
        - Loads the menu music
        - Creates the buttons for the menu and adds them to the desired button lists
        - Creates a timed event to animate the background in the menu

        Test:
            - Check if music is playing in the menu
            - Check in log if all buttons are loaded
            - Check if buttons are displayed in the menu
            - Check if the background is animated
            - Check log if menu is initialized
        """
        self.volume = 1
        pygame.display.set_caption("Menu")
        pygame.mixer.music.load("./assets/music/menu.mp3")
        pygame.mixer.music.play(loops = -1, fade_ms = 1000)
        pygame.mixer.music.set_volume(self.volume)

        self.menu_button_image       = "./assets/menu/buttons/button.png"
        self.menu_button_image_hover = "./assets/menu/buttons/button_hover.png"
        self.mute_button_image    = "./assets/menu/buttons/mute.png"
        self.unmute_button_image  = "./assets/menu/buttons/unmute.png"

        self.bg_menu = []
        Image_List(self.bg_menu, windowwidth, windowheight, "./assets/menu/background/")

        self.menu_button_height = 55
        self.menu_button_width = 175

        self.buttons = []
        self.play_button       = Button("Play",       self.menu_button_width, self.menu_button_height, self.menu_button_image,   self.menu_button_image_hover)
        self.scoreboard_button = Button("Scoreboard", self.menu_button_width, self.menu_button_height, self.menu_button_image,   self.menu_button_image_hover)
        self.tutorial_button   = Button("Tutorial",   self.menu_button_width, self.menu_button_height, self.menu_button_image,   self.menu_button_image_hover)
        self.options_button    = Button("Options",    self.menu_button_width, self.menu_button_height, self.menu_button_image,   self.menu_button_image_hover)
        self.quit_button       = Button("Quit",       self.menu_button_width, self.menu_button_height, self.menu_button_image,   self.menu_button_image_hover)

        self.back_button       = Button("Back",       self.menu_button_width, self.menu_button_height, self.menu_button_image,   self.menu_button_image_hover)
        self.mute_button       = Button("",           50,                     50,                      self.mute_button_image,   self.mute_button_image      )
        self.unmute_button     = Button("",           50,                     50,                      self.unmute_button_image, self.unmute_button_image    )

        self.buttons.append(self.play_button)
        self.buttons.append(self.scoreboard_button)
        self.buttons.append(self.tutorial_button)
        self.buttons.append(self.options_button)
        self.buttons.append(self.quit_button)

        self.bg_state = 0
        self.UPDATEBACKGROUND = pygame.USEREVENT
        pygame.time.set_timer(self.UPDATEBACKGROUND, 100)
        logger.info("Menu initialized")

    def animateBackground(self, bool):
        """Animate menu background
        - If the event sets the bool to true the next background image is set
        - If the bool is still false, therefore the event has not yet passed, the background will be rendered with the certain condition

        Args:
            - bool (bool): Indicates whether to switch to the next image

        Test:
            - Check if the background cycles through different images
            - Check if the background is animated smoothly
        """
        if bool:
            if self.bg_state >= len(self.bg_menu)-1:
                self.bg_state = 0
            else:
                self.bg_state += 1
        else:        
            screen.blit(self.bg_menu[self.bg_state], (0,0))

    def start(self):
        """Main menu
        - Menu in which one comes after the start of the program
        - You can go to the different sub-menus here
        - You can start the game
        - You can exit the program

        Test:
            - Check if title is "Menu" and heading is "Space Defenders"
            - Check if each menu button is present
            - Check if each button takes you where you want it to go
            - Check if play starts the game
            - Check if quit ends the program
        """
        pygame.display.set_caption("Menu")
        text_name = Text("Space Defenders", "./assets/fonts/silkscreen-bold.ttf", 90)
                
        while True:
            menu.animateBackground(False)
            text_name.draw(100, 60)

            offset = 0
            mouse_pos = pygame.mouse.get_pos()
            
            for button in self.buttons:
                button.draw(100, 250 + offset)
                
                button.hover = button.rect.collidepoint(mouse_pos)
                offset += 75
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    logger.info("Game endet via close button on window")
                    pygame.quit()
                    sys.exit()

                if event.type == self.UPDATEBACKGROUND:
                    menu.animateBackground(True)

                if event.type == MOUSEBUTTONDOWN:
                    if self.play_button.rect.collidepoint(mouse_pos):
                        game.play()
                    if self.scoreboard_button.rect.collidepoint(mouse_pos):
                        self.scoreboard()
                    if self.tutorial_button.rect.collidepoint(mouse_pos):
                        self.tutorial()
                    if self.options_button.rect.collidepoint(mouse_pos):
                        self.options()
                    if self.quit_button.rect.collidepoint(mouse_pos):
                        logger.info("Game endet via quit button on menu")
                        pygame.quit()
                        sys.exit()

            pygame.display.update()
            
    def scoreboard(self):
        """Scoreboard
        - Shows the first three best scores

        Test:
            - Check if title is "Scoreboard" and heading is "Scoreboard"
            - Check if "back" button is working
            - Check if after first start the three entries are each zero
            - Check if when you set a new highscore, if it appears there
        """
        pygame.display.set_caption("Scoreboard")
        text_scoreboard = Text("Scoreboard", "./assets/fonts/silkscreen-bold.ttf", 60)

        highscores = db_cur.execute("SELECT score FROM highscore ORDER BY score DESC")
        highscores = highscores.fetchall()

        text_place_1 = Text("1st Place: " + str(highscores[0][0]), "./assets/fonts/silkscreen-bold.ttf", 20)
        text_place_2 = Text("2nd Place: " + str(highscores[1][0]), "./assets/fonts/silkscreen-bold.ttf", 20)
        text_place_3 = Text("3rd Place: " + str(highscores[2][0]), "./assets/fonts/silkscreen-bold.ttf", 20)

        while True:
            menu.animateBackground(False)
            text_scoreboard.draw(100, 60)

            text_place_1.draw(100, 200)
            text_place_2.draw(100, 300)
            text_place_3.draw(100, 400)

            self.back_button.draw(100, 550)

            mouse_pos = pygame.mouse.get_pos()
            self.back_button.hover = self.back_button.rect.collidepoint(mouse_pos)
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    logger.info("Game endet via close button on window")
                    pygame.quit()
                    sys.exit()

                if event.type == self.UPDATEBACKGROUND:
                    menu.animateBackground(True)

                if event.type == MOUSEBUTTONDOWN:
                    if self.back_button.rect.collidepoint(mouse_pos):
                        menu.start()

            pygame.display.update()
    
    def tutorial(self):
        """Tutorial
        - Shows a short description of what to do in the game
        - Shows the controls for the game

        Test:
            - Check if title is "Tutorial" and heading is "Tutorial"
            - Check if "back" button is working
            - Check if game description is rendered
            - Check if controls description is rendered
        """
        pygame.display.set_caption("Tutorial")
        text_scoreboard = Text("Tutorial", "./assets/fonts/silkscreen-bold.ttf", 60)

        text_tutorial_1 = Text("Destroy as many meteroids as possible and try to survive as possible.", "./assets/fonts/silkscreen-bold.ttf", 20)
        text_tutorial_2 = Text("The more you destroy meteroids and the longer you survive, the more"  , "./assets/fonts/silkscreen-bold.ttf", 20)
        text_tutorial_3 = Text("points you get. Have fun!"                                            , "./assets/fonts/silkscreen-bold.ttf", 20)
        
        text_controls_1 = Text("W - Up                                  Spacebar - Shoot"             , "./assets/fonts/silkscreen-bold.ttf", 20)
        text_controls_2 = Text("S - Down"                                                             , "./assets/fonts/silkscreen-bold.ttf", 20)
        text_controls_3 = Text("A - Left                                ESC - Exit to menu"           , "./assets/fonts/silkscreen-bold.ttf", 20)
        text_controls_4 = Text("D - Right"                                                            , "./assets/fonts/silkscreen-bold.ttf", 20)

        while True:
            menu.animateBackground(False)
            text_scoreboard.draw(100, 60)

            text_tutorial_1.draw(100, 250)
            text_tutorial_2.draw(100, 270)
            text_tutorial_3.draw(100, 290)

            text_controls_1.draw(100, 400)
            text_controls_2.draw(100, 420)
            text_controls_3.draw(100, 440)
            text_controls_4.draw(100, 460)

            self.back_button.draw(100, 550)

            mouse_pos = pygame.mouse.get_pos()
            self.back_button.hover = self.back_button.rect.collidepoint(mouse_pos)
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    logger.info("Game endet via close button on window")
                    pygame.quit()
                    sys.exit()

                if event.type == self.UPDATEBACKGROUND:
                    menu.animateBackground(True)

                if event.type == MOUSEBUTTONDOWN:
                    if self.back_button.rect.collidepoint(mouse_pos):
                        menu.start()

            pygame.display.update()

    def options(self):
        """Options menu
        - Lets you mute the music in the game and in the menu

        Test:
            - Check if title is "Options" and heading is "Options"
            - Check if "back" button is working
            - Check if the button icons change when the music is muted and the music is turned off
            - Check if the button icons change when the music is unmuted and the music is turned on
        """
        pygame.display.set_caption("Options")
        text_scoreboard = Text("Options", "./assets/fonts/silkscreen-bold.ttf", 60)

        text_music      = Text("Music:" , "./assets/fonts/silkscreen-bold.ttf", 20)
        
        while True:
            menu.animateBackground(False)
            text_scoreboard.draw(100, 60)
           
            text_music.draw(100, 200)

            if menu.volume == 0:
                self.mute_button.draw(230, 190)
            else:
                self.unmute_button.draw(230, 190)

            self.back_button.draw(100, 550)

            mouse_pos = pygame.mouse.get_pos()
            self.back_button.hover = self.back_button.rect.collidepoint(mouse_pos)
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    logger.info("Game endet via close button on window")
                    pygame.quit()
                    sys.exit()

                if event.type == self.UPDATEBACKGROUND:
                    menu.animateBackground(True)

                if event.type == MOUSEBUTTONDOWN:
                    if self.back_button.rect.collidepoint(mouse_pos):
                        menu.start()
                    if self.mute_button.rect.collidepoint(mouse_pos) or self.unmute_button.rect.collidepoint(mouse_pos):
                        if menu.volume == 0:
                            menu.volume = 1
                            pygame.mixer.music.set_volume(menu.volume)
                            logger.info("Music turned on")
                        else:
                            menu.volume = 0
                            pygame.mixer.music.set_volume(menu.volume)
                            logger.info("Music turned off")

            pygame.display.update()

    def gameover(self, score):
        """Game Over Screen
        - Gameover screen when you die in the game
        - Shows you your achieved score
        - Writes the achieved score into the database
        - Switches the music from the game music to the menu music

        Args:
            - score (int): Score achieved in the game run

        Test:
            - Check if title is "Game Over" and heading is "Game Over"
            - Check if "back" button is working
            - Check if the achieved score is displayed in the scoreboard if it is high enough
            - Check if the music changes from the game music to the menu music
        """
        pygame.display.set_caption("Game Over")
        pygame.mixer.music.load("./assets/music/menu.mp3")
        pygame.mixer.music.play(loops = -1, fade_ms = 1000)

        text_gameover = Text("Game Over", "./assets/fonts/silkscreen-bold.ttf", 60)
        text_score = Text("Score: " + str(score), "./assets/fonts/silkscreen-regular.ttf", 40)

        db_cur.execute("INSERT INTO highscore (score) VALUES ('" + str(score) + "')")
        db_com.commit()

        while True:
            menu.animateBackground(False)
            text_gameover.draw(100, 60)

            text_score.draw(100, 200)
            self.back_button.draw(100, 550)

            mouse_pos = pygame.mouse.get_pos()
            self.back_button.hover = self.back_button.rect.collidepoint(mouse_pos)
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    logger.info("Game endet via close button on window")
                    pygame.quit()
                    sys.exit()

                if event.type == self.UPDATEBACKGROUND:
                    menu.animateBackground(True)

                if event.type == MOUSEBUTTONDOWN:
                    if self.back_button.rect.collidepoint(mouse_pos):
                        menu.start()

            pygame.display.update()



class Player(pygame.sprite.Sprite):
    def __init__(self):
        """Initialize player
        - Initialize player as a ship

        Test:
            - Check log if player is loaded
            - Check if object is created
        """
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(100, windowheight/2 , game.image_ship[0].get_width(), game.image_ship[0].get_height())
        logger.info("Player initialized")

    def update(self):
        """Update player animation
        - Animates the exhaust of the space ship
        - If you fly forward or backward the exhaust becomes bigger

        Test:
            - Check if the exhaust cycles through different images
            - Check if the exhaust gets bigger if you move forward or backward
        """
        global move
        global stand

        if move + 1 >= 4:
            move = 0
        if stand + 1 >= 4:
            stand = 0

        if left or right:
            screen.blit(game.images_move[move], (self.rect.x, self.rect.y+26-4))
            screen.blit(game.images_move[move], (self.rect.x, self.rect.y+48-4))
            move += 1
        else:
            screen.blit(game.images_stand[stand], (self.rect.x+18, self.rect.y+26-3))
            screen.blit(game.images_stand[stand], (self.rect.x+18, self.rect.y+48-3))
            stand += 1

        screen.blit(game.image_ship[0], (self.rect.x+35, self.rect.y))
    
    def shoot(self):
        """Player shoot
        - Creates a bullet at the front of the space ship

        Return:
            - Returns the bullet object

        Test:
            - Check if bullet is created at front of the space ship
            - Check if object is created
        """
        return Bullet(self.rect.x, self.rect.y)


    
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        """Initialize bullet
        - Initialize bullet at the front of the space ship

        Args:
            - x (int): X-coordinate where the bullet should be placed
            - y (int): Y-coordinate where the bullet should be placed

        Test:
            - Check if bullet is created at front of the space ship
            - Check if object is created
        """
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(x + 140, y + 30, 15, 12)
    
    def update(self, speed):
        """Update bullet
        - Moves the bullet to the right

        Args:
            - speed (int): Speed with which the bullet flies to the right

        Test:
            - Check if the bullet flies to the right
            - Check if the projectile speeds up or slows down when you change the speed
        """
        self.rect.x += speed
        screen.blit(game.image_bullet[0], (self.rect.x-56, self.rect.y-56))



class Meteoroid(pygame.sprite.Sprite):
    def __init__(self, y):
        """Initialize meteoroid
        - Initialize meteoroid in the invisible area next to the right window border
        - This is done so that it looks like the meteoroid is flying in and not just spawning

        Args:
            - y (int): Y-coordinate where the met should be placed

        Test:
            - Check if meteoroid is created next to the right window border
            - Check if object is created
        """
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(windowwidth, y, 38 , 33)
        self.state = 0

    def spawn():
        """Spawnes the meteoroid
        - Creates the meteorite at a random y-height in the window

        Return:
            - Returns the meteoroid object

        Test:
            - Check if meteoroid is created next to the right window border
            - Check if two or more meteors are randomly distributed in the y-height
            - Check if object is created
        """
        return Meteoroid(random.uniform(33, windowheight - 33))
        
    def update(self, speed):
        """Update the meteoroid
        - Moves the meteoroid to the left
        - Animates an explosion when the meteroid is hit

        Args:
            - speed (int): Speed with which the meteoroid flies to the left

        Test:
            - Check if the meteroid cycles through images for the expolsion when it was hit by a bullet
            - Check if the meteroid is deleted from the sprite group when the animation is finished
            - Check if the meteroid speeds up or slows down when you change the speed
        """
        if self.state+1 == len(game.image_meteoroid):
            self.kill()
        elif self.state > 0:
            self.state += 1

        self.rect.x -= speed
        screen.blit(game.image_meteoroid[self.state], (self.rect.x-29, self.rect.y-32))



class Game():
    def __init__(self):
        """Initialize game
        - Creats Image_Lists for different objects in game
        - Calculates the screen size and the required background images for the parallax background.

        Test:
            - Check if the image lists contain images
            - Check if all layers of the background are loaded
            - Check in the log if all images are loaded
        """
        self.images_move = []
        self.images_stand = []
        self.image_ship = []
        self.bg_game = []
        self.image_meteoroid = []
        self.image_bullet = []

        Image_List(self.images_move, 38, 8, "./assets/game/ship/exhaust/move/")
        Image_List(self.images_stand, 20, 6, "./assets/game/ship/exhaust/stand/")
        Image_List(self.image_ship, 118, 75, "./assets/game/ship/ship/")
        Image_List(self.bg_game, windowwidth, windowheight, "./assets/game/background/")
        Image_List(self.image_meteoroid, 96, 96, "./assets/game/meteoroid/")
        Image_List(self.image_bullet, 128, 128, "./assets/game/ship/shots/")

        self.bg_width = self.bg_game[0].get_width()
        self.tiles = math.ceil(windowwidth / self.bg_width) + 1
        self.scroll = [0 for x in range(len(self.bg_game))]
        logger.info("Game initialized")

    def animateBackground(self):
        """Animate moving background
        - Inspired by https://www.youtube.com/watch?v=OAH8K5lVYOU
        - Moves the different layers of the background at different speeds to create a parallax effect
        - When a layer is no longer visible, it is deleted and a new layer is inserted at the end of the image strip

        Tests:
            - Check if the background scrolls infinitely to the left
            - Check if the different layers move with different speed
        """
        for i in range(len(self.bg_game)):
            for x in range(self.tiles):
                screen.blit(self.bg_game[i], ((x * self.bg_width) + self.scroll[i], 0))

            self.scroll[i] -= ((i+1) * 0.5)

            if abs(self.scroll[i]) > self.bg_width:
                self.scroll[i] = 0

    def animateScore(self, score):
            """Display score
            - Renders the score in the top left corner of the game

            Args:
                - score (int): Score to be displayed

            Tests:
                - Check if the score and the text "Score :" are displayed in the game
                - Check if the score increases in the course of the game
            """
            font = pygame.font.Font("./assets/fonts/silkscreen-regular.ttf", 20)
            surface = font.render("Score: " + str(score), True, (255,255,255))
            rect = surface.get_rect()
            rect.topleft = (3, 0)
            screen.blit(surface, rect)

    def play(self):
        """Main game function
        - Changes the music from menu music to game music
        - Lets the player control his ship and shoot meteroids
        - Spawns the meteroids in a certain interval 
        - As the game progresses there will be more meteroids and the speed of them will increase

        Tests:
            - Check if the player can move his ship and shoot with it
            - Check if meteoroids spawn
            - Check if the player dies when he hits a meteoroids
            - Check if a meteoroid explodes when a bullet hits it
            - Check if bullets and meteoroids are removed from the sprite group when they hit a window edge with an offset
            - Check if the score increases as the game progresses and a meteoroid is hit
            - Check if a different music than in the menu is played        
        """
        pygame.display.set_caption("Space Defenders")
        pygame.mixer.music.load("./assets/music/game.mp3")
        pygame.mixer.music.play(loops = -1, fade_ms = 1000)

        global left
        global right
        global up
        global down
        global move
        global stand
    
        score = 0

        move = 0
        stand = 0
        player_speed = 3
        bullet_timer = True
        
        meteoroid_speed = 4
        meteoroid_timer = 1500
        
        previous_time = pygame.time.get_ticks()

        player = Player()
        player_group = pygame.sprite.GroupSingle(player)
        bullet_group = pygame.sprite.Group()
        meteoroid_group = pygame.sprite.Group()
        meteoroid_group_exploded = pygame.sprite.Group()

        METEOROID_TIMER = pygame.USEREVENT + 0
        pygame.time.set_timer(METEOROID_TIMER, meteoroid_timer)

        DIFFICULTY_INCREASE = pygame.USEREVENT + 1
        pygame.time.set_timer(DIFFICULTY_INCREASE, 15000)

        while True:
            game.animateBackground()

            left = False
            right = False  
            up = False  
            down = False

            score += 1

            for event in pygame.event.get():
                if event.type == METEOROID_TIMER:
                    meteoroid_group.add(Meteoroid.spawn())

                if event.type == DIFFICULTY_INCREASE:
                    meteoroid_speed += 0.25
                    if meteoroid_timer > 200:
                        meteoroid_timer -= 100
                    pygame.time.set_timer(METEOROID_TIMER, meteoroid_timer)
                    logger.info("Game difficultry increased. Meteoroid speed now at '" + str(meteoroid_speed) + "' and Meteoroid spawn timer at '" + str(meteoroid_timer) + "'ms")

                if event.type == pygame.QUIT:
                    logger.info("Game endet via close button on window")
                    pygame.quit()
                    sys.exit()
            
            key = pygame.key.get_pressed()

            if key[pygame.K_a]:
                left   = True
                right  = False
                up     = False
                down   = False

                if  player.rect.x >= 0:
                    player.rect.x -= player_speed

            if key[pygame.K_d]:
                left   = False
                right  = True
                up     = False
                down   = False

                if  player.rect.x <= windowwidth - 50:
                    player.rect.x += player_speed

            if key[pygame.K_w]:
                left   = False
                right  = False
                up     = True
                down   = False

                if  player.rect.y  >= 0:
                    player.rect.y -= player_speed

            if key[pygame.K_s]:
                left   = False
                right  = False
                up     = False
                down   = True

                if  player.rect.y <= windowheight - 50:
                    player.rect.y += player_speed

            if key[pygame.K_SPACE]:
                #Inspired by https://stackoverflow.com/a/48357144
                current_time = pygame.time.get_ticks()
                if current_time - previous_time > 500:
                    previous_time = current_time
                    bullet_group.add(player.shoot())

            if key[pygame.K_ESCAPE]:
                logger.info("Player returned to menu")
                logger.info("Gameover")
                menu.gameover(score)

            player.update()               

            gameover = pygame.sprite.spritecollide(player, meteoroid_group, True, collided = None)
            if len(gameover) != 0:
                logger.info("Player hit Meteoroid")
                logger.info("Gameover")
                menu.gameover(score)

            hit = pygame.sprite.groupcollide(meteoroid_group, bullet_group, False, True)
            for sprite in hit:
                sprite.state += 1
                meteoroid_group.remove(sprite)
                meteoroid_group_exploded.add(sprite)
                score += 100

            pygame.sprite.spritecollide(window_right, bullet_group, True)
            pygame.sprite.spritecollide(window_left, meteoroid_group, True)
            
            meteoroid_group.update(meteoroid_speed)
            meteoroid_group_exploded.update(meteoroid_speed)
            bullet_group.update(5)
            game.animateScore(score)
            pygame.display.update()



game = Game()
menu = Menu()
menu.start()