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

    total_account: float
    rewards: list
    latest_rewards: float
    vel_factor = 100

    def __init__(self):
        self.rewards = []
        self.total_account = 0

    def add_total_reward_list(self, reward_list: List[RewardType]):

        self.rewards.extend(reward_list)

        for reward in reward_list:
            self.total_account += reward.reward_points
        self.latest_rewards = sum(
            [reward.reward_points for reward in reward_list])

    def get_reward_account(self) -> float:
        return self.total_account

    def get_latest_rewards(self):
        return self.latest_rewards

    def get_list_of_rewards(self):
        return self.rewards

    def update_reward_account(self, on_track: bool, collision: bool, check_point: bool, velocity_x: float, max_velocity_x: float):

        rewards = []
        if on_track:
            rewards.append(RewardType(+1, 'on_track'))
        else:
            rewards.append(RewardType(-10, 'off_track'))
        if collision:
            rewards.append(RewardType(-1, 'collision'))
        if check_point:
            rewards.append(RewardType(+1, 'check_point'))

        velocity_reward = velocity_x/max_velocity_x*self.vel_factor
        rewards.append(RewardType(velocity_reward, 'vel_bonus'))

        self.latest_rewards = rewards
        self.add_total_reward_list(rewards)
