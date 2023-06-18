from gymnasium.envs.registration import register

register(
    id="sd-v0",
    entry_point="rl_sd_car.envs:SdCarEnv",
)
