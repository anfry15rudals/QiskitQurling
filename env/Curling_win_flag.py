import gym
import numpy as np
from numpy import random
from gym import spaces

MAX_SCORE = 30

class Curling(gym.Env):
    """
    input:
        action: 0 or 1; 0: conservative, 1: aggressive
    output:
        [0]: is_winning; 1:winning, 0: draw, -1: losing
        [1]: hammer; 1: with hammer, -1: without hammer
    inner variable:
        self.total_score: accumulated score of every end so far
        self.hammer: 1: with hammer, 0: without hammer
    """

    def __init__(self, reward_type="winner_takes_it_all"):
#     super(Curling, self).__init__()
        self.action_space = gym.spaces.Discrete(2)  # [0, 1]. 0: conservative, 1: aggressive
        self.observation_space = gym.spaces.Box(low=np.array([-1*MAX_SCORE, -1]), high=np.array([MAX_SCORE, 1]), dtype=np.int8)
        
        # inner variables
        self.num_ends = 0
        self.this_end_result = 0
        self.total_score = 0
        self.single_end_score_range = np.arange(-3, 4)
        self.agressive_with_hammer_stat = (0.02867, 0.10338, 0.22607, 0.16607, 0.06996, 0.28463, 0.12122)
        self.agressive_without_hammer_stat = (0.12122, 0.28463, 0.06996, 0.16607, 0.22607, 0.10338, 0.02867)
        self.conservative_with_hammer_stat = (0, 0, 0.1, 0.2, 0.6, 0.1, 0)
        self.conservative_without_hammer_stat = (0, 0.1, 0.6, 0.2, 0.1, 0, 0)
        self.current_state = np.array([0, random.choice((1, -1), p=(0.5, 0.5))])  # (is_winning:draw, hammer)
        self.reward_type = reward_type
        
    def step(self, action):
        # calculate this end's result
        # print("RAND HAMMER:", self.current_state[1])
        if (self.current_state[1] == 1):  # with hammer
            if action:  # aggressive
                this_end_result = random.choice(self.single_end_score_range, p=self.agressive_with_hammer_stat)
            else:  # conservative
                this_end_result = random.choice(self.single_end_score_range, p=self.conservative_with_hammer_stat)
        if (self.current_state[1] == -1):  # without hammer
            if action:  # aggressive
                this_end_result = random.choice(self.single_end_score_range, p=self.agressive_without_hammer_stat)
            else:  # conservative
                this_end_result = random.choice(self.single_end_score_range, p=self.conservative_without_hammer_stat)
        
        # decide if we'll be with the hammer for the next end
        if this_end_result > 0:
            hammer = 1
        if this_end_result == 0:
            hammer = self.current_state[1]  # keep the current stance
        if this_end_result < 0:
            hammer = -1
        
        # determine the next state
        self.total_score = self.total_score + this_end_result
        self.this_end_result = this_end_result  # for reward computation
        self.is_winning = 1 if (self.total_score > 0) else (0 if self.total_score == 0 else -1)
        self.current_state = np.array([self.is_winning, hammer])
        
        # update game status
        self.num_ends = self.num_ends + 1
        self.done = True if ((self.num_ends >= 10) and (self.total_score != 0)) else False
        
        # calculate reward
        if self.reward_type == "winner_takes_it_all":
            reward = self.winner_takes_it_all()
        if self.reward_type == "each_end_counts":
            reward = self.each_end_counts()
        
        info = self.total_score # for debugging
        
        return self.current_state, reward, self.done, info
    
    def reset(self):
        self.num_ends = 0
        self.current_state = np.array([0, random.choice((1, -1), p=(0.5, 0.5))])  # [is_winning: draw, hammer]
        self.this_end_result = 0
        self.total_score = 0
        return self.current_state    

    def winner_takes_it_all(self):
        if self.done and (self.total_score > 0):
            return 1
        else:
            return 0

    def each_end_counts(self):
        if self.done and (self.total_score > 0):
            return 100 
        else:
            return self.this_end_result