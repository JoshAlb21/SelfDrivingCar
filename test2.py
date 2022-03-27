from stable_baselines.common.env_checker import check_env
from rl_sd_car.envs.sd_car_env import SdCarEnv

env = SdCarEnv()
check_env(env)