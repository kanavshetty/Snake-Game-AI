import torch
import random
import numpy as np
from snake import snake_game_AI, Direction, Point
from collections import deque
from model import Linear_Model_Qnet, q_trainer
from helper import plot


max_memory = 100000
batch_size = 1000
LR = 0.001                                      # Defines the learnign rate of the algorithm

class Agent:
    def __init__(self):
        self.num_games = 0
        self.epsilon = 0                                # Parmater to control the randomness
        self.gamma = 0.9                                  # Parameter for discout rate
        self.memory = deque(maxlen = max_memory)       # We use a deque here so that the elements on the left the data structure get popped when the max length of max_memory is met
        self.model = Linear_Model_Qnet(11,256,3)
        self.trainer = q_trainer(self.model, lr = LR, gamma = self.gamma)


    def get_state(self, game):

        head = game.snake_body_list_of_coordinates[0]
        dir_left = game.direction == Direction.LEFT
        dir_right = game.direction == Direction.RIGHT
        dir_up = game.direction == Direction.UP
        dir_down = game.direction == Direction.DOWN

        point_left = Point( head[0]- 10, head[1])
        point_right = Point(head[0] + 10, head[1])
        point_up = Point(head[0], head[1] - 10)
        point_down = Point(head[0], head[1] + 10)

        state = [
            (dir_right and game.game_over(point_right)) or (dir_left and game.game_over(point_left)) or (dir_up and game.game_over(point_up)) or (dir_down and game.game_over(point_down)),
            (dir_up and game.game_over(point_right)) or (dir_down and game.game_over(point_left)) or (dir_left and game.game_over(point_up)) or (dir_right and game.game_over(point_down)),
            (dir_down and game.game_over(point_right)) or (dir_up and game.game_over(point_left)) or (dir_right and game.game_over(point_up)) or (dir_left and game.game_over(point_down)),
            dir_left,
            dir_right,
            dir_up,
            dir_down,

            game.food[0] < game.head[0],
            game.food[0] > game.head[0],
            game.food[1] < game.head[1],
            game.food[1] > game.head[1]
        ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append( (state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory)>batch_size:
            mini_sample = random.sample(self.memory, batch_size)
        else:
            mini_sample = self.memory
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):

        self.epsilon = 80 - self.num_games
        final_move = [0,0,0]

        if random.randint(0,200) < self.epsilon:
            move = random.randint(0,2)
            final_move[move] = 1    
        else:
            state0 = torch.tensor(state, dtype = torch.float)
            prediction = self.model(state0)

            move = torch.argmax(prediction).item()
            if move < len(final_move):
                final_move[move] = 1
        return final_move

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game  = snake_game_AI()
    while True:
        state_old = agent.get_state(game)                                   # This is to get the old state of the game
        
        final_move = agent.get_action(state_old)                            # This is to get the final move from the agent based on the current or old state of the game

        reward, done, score = game.moving_snake(final_move)                 # This step performs the move and updates the state of the game
        state_new = agent.get_state(game)                                   # This gives us the new state of the game

        agent.train_short_memory(state_old, final_move, reward, state_new, done)  # This is to train the short memory

        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            game._reset()
            agent.num_games +=1
            agent.train_long_memory()

            if score>record:
                record = score

            print('Game: ', agent.num_games, 'Score: ', score, 'Record: ', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score/agent.num_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

if __name__ == '__main__':
    train()