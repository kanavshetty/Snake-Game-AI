import pygame                                      #importing the pygame module
import random                                      #importing this module to make the food appear randomly
import time                                        #importing this module to control the sleep time of the program
import numpy as np
from enum import Enum
from collections import namedtuple
pygame.init()                                      # Initializing the pygame game environment

#Initializing all the variables ahead of usign them later in the program

font = pygame.font.SysFont("calibri",25)            # This is the font style and size with which I wanted my text displayed
clock = pygame.time.Clock()                        # This helps us to control the frame rate of the game


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

class snake_game_AI:
    def __init__(self, screen_height = 500, screen_width = 500):
        

        self.screen_height=screen_height
        self.screen_width = screen_width

        self.game_screen = pygame.display.set_mode((self.screen_width,self.screen_height)) #Initialized the game screen with dimensions 500x500
        pygame.display.set_caption("Snake Game")     # Set the title of the game
        self.snake_x_coordinates = self.screen_height/2
        self.snake_y_coordinates = self.screen_width /2
        self._reset()
        self.score = 0
        

          
    def _reset(self):
        
        self.head = Point(self.snake_x_coordinates,self.snake_x_coordinates)
        self.direction = Direction.RIGHT
        self.snake_body_list_of_coordinates = [(self.head.x,self.head.y),(self.head.x-10,self.head.y),(self.head.x-20,self.head.y)]     # We store the coordinates of each segment of the body of the snake in tuples like (x,y) and store these tuples in a list
        self.food = None
        self._place_food()
        self.score = 0
        self.frame_iterations = 0

    def moving_snake(self,action):

        self.frame_iterations +=1  

        
        for event in pygame.event.get() :        # Each event like a mouse click is stored in this list and Iterating through each event in the list
            if(event.type == pygame.QUIT):       # If the event is closing the game window
                pygame.quit()                    # Closing the pygame game environment
                quit()                           # Exiting the program
            
               

        clockwise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clockwise.index(self.direction)

        if np.array_equal(action, [1,0,0]):
            new_dir = clockwise[idx]

        elif np.array_equal(action, [0,1,0]):
            next_idx = (idx+1)%4
            new_dir = clockwise[next_idx]    

        else:
            next_idx = (idx-1)%4
            new_dir = clockwise[next_idx]

        self.direction = new_dir

        x = self.head.x
        y = self.head.y

        if self.direction == Direction.RIGHT:
            x = (x+ 10)%self.screen_width
        elif self.direction == Direction.LEFT:
            x = (x- 10)%self.screen_width   
        elif self.direction == Direction.DOWN:
            y = (y+ 10)%self.screen_height
        elif self.direction == Direction.UP:
            y = (y- 10)%self.screen_height

        self.head = Point(x,y)
        self.snake_body_list_of_coordinates.append((self.head.x,self.head.y))                    # We append each item in the list with the new x and y coordinates of snake segment to keep track of the changes
        
        reward = 0
        game_over = False
        
        if self.game_over() or self.frame_iterations > 150*len(self.snake_body_list_of_coordinates):
            game_over = True
            self.reward = -10
            return reward, game_over, self.score

        if (self.head == self.food ):       # This if statement checks if the snake eats the food or not by matching the coordinates of the head of the snake with the coordiantes of the food
            while((self.food.x, self.food.y) in self.snake_body_list_of_coordinates):              # This while statement means that while the coordinates of the food do nto belong in the list of the snake body parts, we can exit the loop and the food coordinates are stored in new random coordinates, but if our new rnadom coorinates happen to lie within the snake's bpdy parts, this while loop ensures that we do not exit the loop until we find coordiantes for the food where it does not belong in the body of the snake
                self.score +=1
                reward = 10
                self._place_food()
        else:
            del self.snake_body_list_of_coordinates[0]                                                           # After we have appended a new segment to the body of the snake based on the direction of the snake movement, we can now delete the frist segment which is the oldest segment since we do not need it and need to keep the size of the snake the same when it does not eat food. It is important to remember that this does not run when the snake eats food, and that is how the snake grows larger by 1 unit when it eats food.
        

        self._game_screen_update()
        clock.tick(50)                # This statement helps us control the frame rate of the game. If we want to increase the difficulty we can definitely do so by changing the framerate.
        return reward, game_over, self.score

    def game_over(self, pt=None):

        if pt is None:
            pt = self.head
        
        if(pt in self.snake_body_list_of_coordinates[0:-1]) :                     # This if statement basically checks if the head of the snake which is the last element(coordinates) of the list, is already in the rest of the list. If it is already there in the list, this means that head of the snake has crashed into its body
            return True
        return False

    def _place_food(self):
        x = random.randint(0, (self.screen_width-10 )//10 )*10
        y = random.randint(0, (self.screen_height-10 )//10 )*10
        self.food = Point(x, y)


    def _game_screen_update(self):
        self.game_screen.fill((173,204,96))                                                                       # We fill the game screen with a green color
        score = font.render("Score: " + str(self.score), True, (0,0,0)  )      # We render a score for the user based on the length of the snake
        self.game_screen.blit(score,[0,0])                                                                        # We print the score to the screen on the top left
        pygame.draw.rect(self.game_screen,(255,0,0),[self.food.x,self.food.y,10,10])                # We now draw a rectangle in red tp depict the food
        for (i,j) in self.snake_body_list_of_coordinates:                                                         # Now for each tuple in the list of snake segments, we draw a rectnagle of dark green color on the screen
            pygame.draw.rect(self.game_screen,(0,0,255),[i,j,10,10])
        pygame.display.update()                                                                              # To make the rectnagle we drew above actually apear on the game screen we need to call it

    def _game_over_screen(self):
        self.game_screen.fill((0,0,0))            # We fill the screen with a black color and a print the score and Game Over! message
        score = font.render("Score: " + str(len(self.snake_body_list_of_coordinates)), True, (255,255,0))
        self.game_screen.blit(score,[0,0])
        msg = font.render("GAME OVER!", True, (255,255,255))    
        self.game_screen.blit(msg,[self.screen_width/3,self.screen_height/2])
        pygame.display.update()
        time.sleep(3)                       # We freeze the screen for 3 seconds here to give the user some time to soak in their loss and score and then we close the program automatically
        pygame.quit()
        quit()
  


