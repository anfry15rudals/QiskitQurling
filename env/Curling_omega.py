import gym
import numpy as np
from numpy import random
from gym import spaces

MAX_SCORE = 3

class Curling(gym.Env):
    def __init__(self, reward_type="winner_takes_it_all"):
#     super(Curling, self).__init__()
        self.action_space = gym.spaces.Discrete(2)  # [0, 1]. 0: conservative, 1: aggressive
        self.observation_space = gym.spaces.Box(low=np.array([-1*MAX_SCORE, 0]), high=np.array([MAX_SCORE, 1]), dtype=np.int8)
        
        # inner variables
        self.num_ends = 0
        self.this_end_result = 0
        self.score_range = np.arange(-1*MAX_SCORE, MAX_SCORE+1)
        self.agressive_with_hammer_stat = (0.02867, 0.10338, 0.22607, 0.16607, 0.06996, 0.28463, 0.12122)
        self.agressive_without_hammer_stat = (0.12122, 0.28463, 0.06996, 0.16607, 0.22607, 0.10338, 0.02867)
        self.conservative_with_hammer_stat = (0, 0, 0.1, 0.2, 0.6, 0.1, 0)
        self.conservative_without_hammer_stat = (0, 0.1, 0.6, 0.2, 0.1, 0, 0)
        choice = [-1, 1]
        self.current_state = np.array([0, random.choice(choice)])  # (score, hammer)
        self.reward_type = reward_type
        
    def step(self, action):
        # calculate this end's result
        if self.current_state[1]>0:  # with hammer
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
            hammer = -1
        if this_end_result == 0:
            hammer = self.current_state[1]  # keep the current stance
        if this_end_result < 0:
            hammer = 1
        
        # determine the next state
        score_after_this_end = self.current_state[0] + this_end_result
        state = np.array([score_after_this_end, hammer])
        self.current_state = state
        self.this_end_result = this_end_result  # for reward computation
        
        # update game status
        self.num_ends = self.num_ends + 1
        self.done = True if ((self.num_ends >= 10) and (self.current_state[0] != 0)) else False
        
        # calculate reward
        if self.reward_type == "winner_takes_it_all":
            reward = self.winner_takes_it_all()
        if self.reward_type == "each_end_counts":
            reward = self.each_end_counts()
        
        info = None  # placeholder for debug messages
        
        if self.current_state[0] > 0:
            return_state = np.array([1, self.current_state[1]])
        elif self.current_state[0] < 0:
            return_state = np.array([-1, self.current_state[1]])
        else:
            return_state = np.array([0, self.current_state[1]])
        return return_state, reward, self.done, info
    
    def reset(self):
        choice = [-1, 1]
        self.num_ends = 0
        self.current_state = np.array([0, random.choice(choice)])  # (score, hammer)
        self.this_end_result = 0
        return self.current_state    

    def winner_takes_it_all(self):
        if self.done and (self.current_state[0] > 0):
            return 1
        else:
            return 0

    def each_end_counts(self):
        if self.done and (self.current_state[0] > 0):
            return 100 + self.this_end_result
        else:
            return self.this_end_result