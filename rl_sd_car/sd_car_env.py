import gym
from gym import error, spaces, utils
from gym.utils import seeding

class SdCarEnv(gym.Env):

    metadata = {'render.modes': ['human']}
    
    def __init__(self):

        super().__init__()
        
    
        # Define an action space
        self.action_space = spaces.Discrete(5,)
        '''
        left
        right
        acc
        brake
        nothing
        '''

        # Define observation space
        '''
        velocity (only x)
        angle
        distance1
        distance2
        '''
        high = np.array([20.0, 360.0, 1.0, 1.0])
        low = np.array([0.0] * 360)
        self.observation_space = spaces.Box(low, high, dtype=np.float32)

    def step(self, action):
        pass
    def reset(self):
        pass
    def render(self, mode='human'):
        pass
    def close(self):
        pass