import os
import pygame
from math import sin, radians, degrees, copysign
import numpy as np
from pygame.math import Vector2
import random


from my_car import Car
import background
from drive_events import EnvironmentHandlerInputs, EnvironmentHandlerActions
from reward_system import RewardAccount


class Game:

    width: int
    height: int
    car: Car
    fps: int

    def __init__(self, height, width, fps, ppu, input_human:bool):
        pygame.init()
        pygame.display.set_caption("Deep Learning Car")
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.ticks = fps
        self.exit = False
        self.ppu = ppu

        #RL related settings
        self.input_human = input_human
        self.rl_action = None
        self.pos_action_list = ["up", "down", "left", "right", "brake", "nothing"]

        pygame.font.init()
        self.myfont = pygame.font.SysFont('Comic Sans MS', 30)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        background_path = os.path.join(current_dir, 'img', 'background.png')
        self.BackGround = background.Background(background_path, [0, 0])

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

    def key_arrow_handler(self, pressed, dt):

        if pressed[pygame.K_UP] or pressed == 'up':
            if self.car.velocity.x < 0:
                self.car.acceleration = self.car.brake_deceleration
            else:
                self.car.acceleration += self.car.inertia * dt
        elif pressed[pygame.K_DOWN] or pressed == 'down':
            if self.car.velocity.x > 0:
                self.car.acceleration = -self.car.brake_deceleration
            else:
                self.car.acceleration -= self.car.inertia * dt
        elif pressed[pygame.K_SPACE] or pressed == 'brake':
            if abs(self.car.velocity.x) > dt * self.car.brake_deceleration:
                self.car.acceleration = - \
                    copysign(self.car.brake_deceleration, self.car.velocity.x)
            else:
                self.car.acceleration = -self.car.velocity.x / dt
        elif pressed[pygame.K_BACKSPACE] or pressed == 'reset':
            #self.car.position = Vector2(self.car.reset_point)
            action_handler = EnvironmentHandlerActions()
            action_handler.reset_to_start(self.car)
        else:
            if abs(self.car.velocity.x) > dt * self.car.free_deceleration:
                self.car.acceleration = - \
                    copysign(self.car.free_deceleration, self.car.velocity.x)
            else:
                if dt != 0:
                    self.car.acceleration = -self.car.velocity.x / dt
        # restrict acc (otherwise acc would increase infinetly)
        self.car.acceleration = max(-self.car.max_acceleration,
                                    min(self.car.acceleration, self.car.max_acceleration))

        if pressed[pygame.K_RIGHT] or pressed == 'right':
            self.car.steering -= self.car.steering_increase * dt
        elif pressed[pygame.K_LEFT] or pressed == 'left':
            self.car.steering += self.car.steering_increase * dt
        else:
            self.car.steering = 0
        self.car.steering = max(-self.car.max_steering,
                                min(self.car.steering, self.car.max_steering))
    def set_rl_action(self, action):

        if action in self.pos_action_list:
            self.rl_action = action

    def get_rl_action(self):
        return self.rl_action

    def test(self):
        random_pick = random.choice(self.pos_action_list) 
    
    def run(self):

        self.assemble()
        env_handler = EnvironmentHandlerInputs(self.car)
        reward_account = RewardAccount()

        # get_pixel for collision detection
        white_p, corner_p, green_p = self.BackGround.get_pixel()
        on_track = False

        while not self.exit:

            # get time since last call
            dt = self.clock.get_time() / 1000

            # check whether to quit game or not
            self.check_quit_game()

            # Input
            if self.input_human:
                pressed = pygame.key.get_pressed()
            else:
                pressed = self.get_rl_action()
            self.key_arrow_handler(pressed, dt)

            col = self.collision_detection(corner_p)
            env_handler.check_border()
            on_track = env_handler.check_on_track(self, white_p)
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
            reward_account.update_reward_account(
                on_track, col, check_point=False, velocity_x=self.car.velocity[0], max_velocity_x=self.car.max_velocity)

            # Drawing
            self.screen.fill([255, 255, 255])
            self.screen.blit(self.BackGround.image, self.BackGround.rect)

            # Draw sensor lines
            self.car.sensor1.draw_sensor_line(self.car, self.screen)
            self.car.sensor2.draw_sensor_line(self.car, self.screen)

            self.car.sensor1.get_dist_to_wall(
                self.car, (0, 0, 0), self.screen, self)
            # self.car.sensor1._get_y_differ(self.car)

            # New Car Position
            rotated = pygame.transform.rotate(
                self.car.car_image, self.car.angle)
            rect = rotated.get_rect()

            self.screen.blit(rotated, self.car.position *
                             self.ppu - (rect.width / 2, rect.height / 2))
            pygame.display.flip()

            self.clock.tick(self.ticks)  # adjust fps

        pygame.quit()


if __name__ == '__main__':

    # OPTIONS
    width = 1600  # 1280
    height = 920  # 720
    fps = 60
    # pixel per unit ratio
    # pixel_length of car/meter length of car
    ppu = 40

    game = Game(height, width, fps, ppu)
    game.run()
