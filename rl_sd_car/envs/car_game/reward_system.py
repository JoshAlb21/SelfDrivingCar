from typing import List
import numpy as np

#TODO add check points
class CheckPoint:

    position: tuple
    check_times: int

    def __init__(self, x, y):

        self.position = x, y
        self.check_times

    def checked(self):

        self.check_times += 1


class RewardType:

    reward_points: float
    reward_type: str  # positive or negative
    description: str

    def __init__(self, reward_points, description):

        self.reward_points = reward_points
        self.description = description

        if reward_points < 0.0:
            reward_type = 'negative'
        else:
            reward_type = 'positive'


class RewardAccount:

    total_account: float
    rewards: list
    latest_rewards: List[RewardType]

    def __init__(self):
        self.rewards = []
        self.total_account = 0
        self.latest_rewards = [RewardType(0.0, 'init_reward')] #dummy value

    def add_total_reward_list(self, reward_list: List[RewardType]):

        self.rewards.extend(reward_list)

        self.total_account += sum([reward.reward_points for reward in reward_list])

    def get_reward_account(self) -> float:
        return self.total_account

    def get_latest_rewards(self):
        # Extract reward points of every RewardType object in list
        reward = sum([reward.reward_points for reward in self.latest_rewards])

        return reward

    def get_list_of_rewards(self):
        return self.rewards

    def update_reward_account(self, on_track: bool, collision: bool, check_point: bool, velocity_x: float, velocity_y: float, max_velocity_x: float):
        'Define the reward function'

        rewards = []
        if on_track:
            rewards.append(RewardType(0.0, 'on_track')) #not too high otherwise agent will not move at all
        else:
            rewards.append(RewardType(-1.0, 'off_track')) #the whole time while off-track!
        if collision:
            rewards.append(RewardType(-1.0, 'collision')) #only once
        if check_point:
            rewards.append(RewardType(+1, 'check_point'))

        velocity_reward = velocity_x/(max_velocity_x*20) # Normalize x-velocity reward [0,0.05] # lower than 1 because vel reward can be achieved every step
        rewards.append(RewardType(velocity_reward, 'vel_bonus'))

        #TODO add check points

        self.latest_rewards = rewards
        self.add_total_reward_list(rewards)
