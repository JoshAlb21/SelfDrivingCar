from typing import List


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

    total_account: list
    rewards: list
    latest_rewards: float

    def __init__(self):
        self.rewards = []
        self.total_account = 0

    def add_reward_list(self, reward_list: List[RewardType]):

        self.rewards.extend(reward_list)

        for reward in reward_list:
            self.total_account += reward.reward_points

    def get_reward_account(self):
        return self.total_account

    def get_list_of_rewards(self):
        return self.rewards

    def update_reward_account(self, on_track, collision, check_point, velocity_x, max_velocity_x):

        rewards = []
        if on_track:
            rewards.append(RewardType(+1, 'on_track'))
        else:
            rewards.append(RewardType(-1, 'off_track'))
        if collision:
            rewards.append(RewardType(-1, 'collision'))
        if check_point:
            rewards.append(RewardType(+1, 'check_point'))

        velocity_reward = velocity_x/max_velocity_x
        rewards.append(RewardType(velocity_reward, 'vel_bonus'))

        self.add_reward_list(rewards)

        print(f'reward_account: {self.total_account}')
