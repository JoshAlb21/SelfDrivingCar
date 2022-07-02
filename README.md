PROJEKT IST AKTUELL IN ARBEIT
WORK IN PROGRESS

[![Product Name Screen Shot][product-screenshot]](https://www.pygame.org/news)

# Parameter
ppu: pixel per unit ratio
pixel_length of car/meter length of car

## 1.Step
install package:
pip install -e SelfDrivingCar

## 2.Step
create an instance of the environment with
gym.make('rl_sd_car:sd-v0')


## Action Space

Define an action space
self.action_space = spaces.Discrete(6,)

left
right
up
down
brake
nothing

## Observation Space

Define observation space

velocity (euclidian norm) [0, 20]
angle [0,360]
distance1 [0,1]
distance2 [0,1]
(later maybe more distance sensors)

<!-- MARKDOWN LINKS & IMAGES -->
[product-screenshot]: images/env_road.png
