import os
import pygame
from math import sin, radians, degrees, copysign, hypot
import numpy as np
from pygame.math import Vector2
import random
import json
import pathlib
from typing import Tuple
import time

from rl_sd_car.envs.car_game.my_car import Car
from rl_sd_car.envs.car_game import background
from rl_sd_car.envs.car_game.drive_events import EnvironmentHandlerInputs, EnvironmentHandlerActions
from rl_sd_car.envs.car_game.reward_system import RewardAccount


class Game:

    width: int
    height: int
    car: Car
    fps: int
    ppu: float
    input_human: bool
    reward_account: RewardAccount

    def __init__(self, height, width, fps, ppu, input_human):
        pygame.init()
        pygame.display.set_caption("Deep Learning Car")
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.ticks = fps
        self.exit = False
        self.ppu = ppu

        # RL related settings
        self.input_human = input_human
        self.rl_action = None
        self.pos_action_list = ["up",
                                "left", "right" ] #TEST remove "nothing", "down", "brake"

        pygame.font.init()
        self.myfont = pygame.font.SysFont('Comic Sans MS', 30)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        background_path = os.path.join(current_dir, 'img', 'background.png')
        self.BackGround = background.Background(background_path, [0, 0])
        self.background_pixel = None
        self.action_handler = EnvironmentHandlerActions()

        self.angle_alpha = 0
        self.angle_beta = 0

        # RL stuff
        self.time_on_track = 0

    def assemble(self):

        # Build Car
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, 'img', 'car_small.png')
        car_image = pygame.image.load(image_path)
        car = Car(car_image, x=4, y=14, angle=90, length=2,
                  max_steering=50, max_acceleration=20.0, ppu=40)
        self.car = car

    def collision_detection(self, col_area):
        col = False
        c_pos = [int(self.car.position[0] * self.ppu),
                 int(self.car.position[1] * self.ppu)]
        if c_pos in col_area:
            col = True
            print("Collision!")

        return col

    def check_quit_game(self):
        # Event: quit game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit = True

    def key_arrow_handler(self, pressed, dt, action: str = ''):

        #TODO write update acc function or lambda
        if pressed is None and not self.input_human:
            pressed = pygame.MOUSEBUTTONDOWN
        if pressed[pygame.K_UP] or action == 'up':
            if self.car.velocity.x < 0:
                self.car.acceleration = self.car.brake_deceleration
            else:
                self.car.acceleration += self.car.inertia * dt
        elif pressed[pygame.K_DOWN] or action == 'down':
            if self.car.velocity.x > 0:
                self.car.acceleration = -self.car.brake_deceleration
            else:
                self.car.acceleration -= self.car.inertia * dt
        elif pressed[pygame.K_SPACE] or action == 'brake':
            if abs(self.car.velocity.x) > dt * self.car.brake_deceleration:
                self.car.acceleration = - \
                    copysign(self.car.brake_deceleration, self.car.velocity.x)
            else:
                try:
                    self.car.acceleration = -self.car.velocity.x / dt
                except ZeroDivisionError:
                    self.car.acceleration
        elif pressed[pygame.K_BACKSPACE] or action == 'reset':
            self.action_handler.reset_to_start(self.car)
        else:
            if abs(self.car.velocity.x) > dt * self.car.free_deceleration:
                self.car.acceleration = - \
                    copysign(self.car.free_deceleration, self.car.velocity.x)
            else:
                if dt != 0:
                    self.car.acceleration = -self.car.velocity.x / dt
        # restrict acc (otherwise acc would increase infinitely)
        self.car.acceleration = max(-self.car.max_acceleration,
                                    min(self.car.acceleration, self.car.max_acceleration))

        if pressed[pygame.K_RIGHT] or action == 'right':
            self.car.steering -= self.car.steering_increase * dt
        elif pressed[pygame.K_LEFT] or action == 'left':
            self.car.steering += self.car.steering_increase * dt
        else:
            self.car.steering = 0
        self.car.steering = max(-self.car.max_steering,
                                min(self.car.steering, self.car.max_steering))

    def set_rl_action(self, action):
        if action < len(self.pos_action_list):
            self.rl_action = action
        else:
            print("No valid action")

    def get_rl_action(self) -> str:
        'Gets the action integer number and converts it in action string'

        rl_action = self.pos_action_list[self.rl_action-1]
        return rl_action

    def get_rl_observation(self, disable_dist: bool = False) -> Tuple[float]:

        velocity = hypot(self.car.velocity[0], self.car.velocity[1])
        angle = self.car.angle
        if not disable_dist:
            dist1, dist2, dist3, dist4, dist5, dist6, dist7 = self.car.sensor_manager.get_distances(self.car, self)
        else:
            dist1, dist2, dist3, dist4, dist5, dist6, dist7 = (1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
        
        return velocity, angle, dist1, dist2, dist3, dist4, dist5, dist6, dist7

    def init_game(self):
        ''' Initiate all necessary functions and modules'''
        self.assemble()
        white_p, corner_p, green_p = self.BackGround.get_pixel()
        self.background_pixel = [white_p, corner_p, green_p]
        env_handler = EnvironmentHandlerInputs(self.car)
        self.env_handler = env_handler
        self.reward_account = RewardAccount()

    def run_game_loop(self):

        self.init_game()
        while not self.exit:
            self.game_loop_function()

        pygame.quit()

    def game_loop_function(self):
        '''Function one have to call in while loop or in step function (rl)'''

        # get time since last call
        dt = self.clock.get_time() / 1000

        # check whether to quit game or not
        self.check_quit_game()

        # Input
        if self.input_human:
            pressed = pygame.key.get_pressed()
            self.key_arrow_handler(pressed, dt)
        else:
            action = self.get_rl_action()
            pressed = pygame.key.get_pressed() #just a dummy to call the self.key_arrow_handler function
            self.key_arrow_handler(pressed, dt, action)
        white_p, corner_p, green_p = self.background_pixel
        col = self.collision_detection(corner_p)
        self.env_handler.check_border()
        on_track = self.env_handler.check_on_track(self, white_p)
        self.car.update_on_track(on_track)
        self.car.update(dt)
        # if not on track
        if not on_track:
            self.car.handle_not_on_track()
            #self.car.position = self.car.last_track_position
            self.time_on_track = 0
        else:
            self.car.last_track_position = self.car.position
            self.time_on_track += 1

        # Reinforcement Stuff
        self.reward_account.update_reward_account(
            on_track, col, check_point=False, velocity_x=self.car.velocity[0], velocity_y=self.car.velocity[1],
            max_velocity_x=self.car.max_velocity)

        # Drawing
        self.screen.fill([255, 255, 255])
        self.screen.blit(self.BackGround.image, self.BackGround.rect)

        # Draw sensor lines
        self.car.sensor_manager.draw_sensor_lines(self.car, self.screen)

        self.car.sensor1.get_dist_to_wall(
            self.car, self)
        
        # New Car Position
        rotated = pygame.transform.rotate(
            self.car.car_image, self.car.angle)
        rect = rotated.get_rect()

        self.screen.blit(rotated, self.car.position *
                         self.ppu - (rect.width / 2, rect.height / 2))
        pygame.display.flip()

        self.clock.tick(self.ticks)  # adjust fps


def create_game() -> Game:
    current_path = pathlib.Path(__file__).parent.resolve()
    config_path = os.path.join(current_path, 'config.json')
    with open(config_path) as json_data_file:
        config = json.load(json_data_file)

    game = Game(config["game"]["screen_height"], config["game"]["screen_widht"],
                config["game"]["fps"], config["game"]["ppu"],
                config["rl_config"]["human_input"])

    return game


if __name__ == '__main__':

    game = create_game()
    game.run_game_loop()
