PROJEKT IST AKTUELL IN ARBEIT

# 1.Step
install package:
pip install -e rl-sd-car

# 2.Step
create an instance of the environment with
gym.make('rl_sd_car:sd-v0')


## Action Space

        # Define an action space
        self.action_space = spaces.Discrete(6,)

left
right
up
down
brake
nothing