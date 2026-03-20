import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import random
from collections import deque
from Gridworld import Gridworld

class GridWorldWrapper:
    """
    Gridworld environment wrapper to interface with Q-learning agent.
    """

    def __init__(self, size=4, mode='static'):
        self.game = Gridworld(size=size, mode=mode)
        self.size = size
        self.action_map = {0: 'u', 1: 'd', 2: 'l', 3: 'r'}  # 0 = up, 1 = down, 2 = left, 3 = right
    
    def reset(self):
        """ Reset the environment and return the initial state. """
        self.game = Gridworld(size=self.size, mode='static')
        return self.get_state()
    
    def get_state(self):
        """ Get the agent's current position and turn out to the state representation. """
        pos = self.game.board.components['Player'].pos
        return pos[0] * self.size + pos[1]
    
    def step(self, action):
        """ Take an action in the environment and return the new state, reward, and done flag. """
        # Take the action
        self.game.makeMove(self.action_map[action])

        # Get the reward
        reward = self.game.reward()
        
        # Get the new state
        new_state = self.get_state()

        # Check if the episode is done
        done = (reward == 10 or reward == -10) # Reach the goal or hit the trap

        return new_state, reward, done
    
    def render(self):
        """ Render the current state of the environment. """
        print(self.game.display())

# Main
if __name__ == "__main__":

    # Initialize the environment wrapper
    env = GridWorldWrapper(size=4, mode='static')