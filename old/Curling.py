import gym
import numpy as np
from numpy import random
from gym import spaces

MAX_SCORE = 3

class Curling(gym.Env):
    def __init__(self):
#     super(Curling, self).__init__()
        self.action_space = gym.spaces.Discrete(2)  # [0, 1]. 0: conservative, 1: aggressive
        self.observation_space = gym.spaces.Box(low=np.array([-1*MAX_SCORE, 0]), high=np.array([MAX_SCORE, 1]), dtype=np.int8)
        
        # inner variables
        self.num_ends = 0
        self.score_range = np.arange(-1*MAX_SCORE, MAX_SCORE+1)
        self.agressive_with_hammer_stat = (0.02867, 0.10338, 0.22607, 0.16607, 0.06996, 0.28463, 0.12122)
        self.agressive_without_hammer_stat = (0.12122, 0.28463, 0.06996, 0.16607, 0.22607, 0.10338, 0.02867)
        self.conservative_with_hammer_stat = (0, 0, 0.1, 0.2, 0.6, 0.1, 0)
        self.conservative_without_hammer_stat = (0, 0.1, 0.6, 0.2, 0.1, 0, 0)
        self.current_state = np.array([0, random.randint(2)])  # (score, hammer)
        
    def step(self, action):
        # calculate this end's result
        if self.current_state[1]:  # with hammer
            if action:  # aggressive
                this_end_result = random.choice(self.score_range, p=self.agressive_with_hammer_stat)
            else:  # conservative
                this_end_result = random.choice(self.score_range, p=self.conservative_with_hammer_stat)
        else:
            if action:  # aggressive
                this_end_result = random.choice(self.score_range, p=self.agressive_without_hammer_stat)
            else:  # conservative
                this_end_result = random.choice(self.score_range, p=self.conservative_without_hammer_stat)
        
        # decide if we'll be with the hammer for the next end
        if this_end_result > 0:
            hammer = 1
        if this_end_result == 0:
            hammer = self.current_state[1]  # keep the current stance
        if this_end_result < 0:
            hammer = 0
        
        # determine the next state
        score_after_this_end = self.current_state[0] + this_end_result
        state = np.array([score_after_this_end, hammer])
        self.current_state = state
        
        # update game status
        self.num_ends = self.num_ends + 1
        done = True if (self.num_ends == 10) else False
        
        # calculate reward
        if done and (self.current_state[0] > 0):
            reward = 1
        else:
            reward = 0
        
        info = None  # placeholder for debug messages
        
        return state, reward, done, info
    
    def reset(self):
        self.num_ends = 0
        self.current_state = np.array([0, random.randint(2)])  # (score, hammer)
        return self.current_state      