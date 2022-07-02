from subprocess import list2cmdline
from pygame.math import Vector2
import pygame
from math import sin, cos, tan, sqrt, radians, degrees, copysign, pi, radians
from numpy import ones, vstack
from numpy.linalg import lstsq
import numpy as np
import math
from typing import List


class Car:

    car_image: pygame.Surface
    ppu: int
    angle: float

    def __init__(self, car_image, x, y, angle=0.0, length=4, max_steering=30, max_acceleration=5.0, ppu=40):

        self.position = Vector2(x, y)  # without ppu
        self.last_track_position = Vector2(0, 0)  # position 1 frame ago
        self.velocity = Vector2(0.0, 0.0)  # m/sec
        self.vel_history = []
        self.angle = angle  # degrees
        self.length = length  # meter kleinerer Wendekreis
        self.max_acceleration = max_acceleration  # meters/second squared
        self.max_steering = max_steering
        self.max_velocity = 20
        self.brake_deceleration = 20  # 10
        self.free_deceleration = 2
        self.inertia = 15  # traegheit
        self.steering_increase = 80
        self.car_image = car_image
        self.reset_point = x, y
        self.ppu = ppu

        self.on_track: bool
        self.on_track_hist_list = []
        self.not_on_track_fee = (2.0, 0)
        self.max_vel_off_track = (5.0, 0)

        self.car_length, self.car_width = self.car_image.get_size()
        self.acceleration = 0.0
        self.steering = 0.0  # deegres positive-left, negative-right

        self.angle_differ = 0
        self.sensor1 = DistSensor('left_front', 300, tan(self.car_width/self.car_length))
        self.sensor2 = DistSensor('left_middle', 300, 0.5*tan(self.car_width/self.car_length))
        self.sensor3 = DistSensor('front', 300, 0.0)
        self.sensor4 = DistSensor('right_middle', 300, -0.5*tan(self.car_width/self.car_length))
        self.sensor5 = DistSensor('right_front', 300, -tan(self.car_width / self.car_length))
        sensor_list = [self.sensor1, self.sensor2, self.sensor3, self.sensor4, self.sensor5]
        self.sensor_manager = DistSensorManager(sensor_list)
        
    
    def get_velocity_norm_history(self, n_max:int=100) -> list:
        'Returns the velocity norm of the last times steps (maximum n last time steps)'
        self.update_velocity_norm_history() #TODO should be updated in game loop
        if len(self.vel_history) > n_max: self.vel_history.pop(0)

        return self.vel_history

    def update_velocity_norm_history(self, reset_list:bool=False):
        if reset_list:
            self.vel_history = []
        vel_vec = np.array([self.velocity.x, self.velocity.y])
        vel_norm = np.linalg.norm(vel_vec)
        self.vel_history.append(vel_norm)

    def handle_not_on_track(self):
        if self.velocity.x >= self.max_vel_off_track[0] and self.velocity.y >= self.max_vel_off_track[1] and self.velocity[0] > 0:
            self.velocity -= self.not_on_track_fee
    
    def update_on_track(self, on_track:bool, reset_list:bool=False):
        if reset_list:
            self.on_track_hist_list = []
        self.on_track = on_track
        self.on_track_hist_list.append(on_track)

    def get_on_track_history(self, n_max:int=100) -> list:
        'Returns the on_track bool of the last times steps (maximum n last time steps)'
        if len(self.on_track_hist_list) > n_max:
            self.on_track_hist_list.pop(0)
        
        return self.on_track_hist_list

    def update(self, dt):  # update every frame
        # integrate to velocity, no sideways acceleration
        self.velocity += (self.acceleration * dt, 0)
        self.velocity.x = max(-self.max_velocity,
                              min(self.velocity.x, self.max_velocity))

        # compute sensor position, and vectorized line
        self.sensor_manager.update_sensor_positions(self)

        if self.steering:
            turning_radius = self.length / sin(radians(self.steering))
            angular_velocity = self.velocity.x / turning_radius
        else:
            angular_velocity = 0

        self.position += self.velocity.rotate(-self.angle) * dt

        self.angle += degrees(angular_velocity) * dt
        map_to_360 = lambda total_angle: total_angle - 360.0 * math.floor(total_angle/360.0)
        self.angle = map_to_360(self.angle)


class DistSensor:

    name: str
    sensor_pos: Vector2
    sensor_length: int
    wall_pix_color: tuple # Default: black
    add_angle: float

    def __init__(self, name, sensor_length, add_angle, wall_pix_color: tuple = (0, 0, 0)):

        self.name = name
        self.sensor_length = sensor_length
        self.wall_pix_color = wall_pix_color
        self.add_angle = add_angle

    def get_sensor_pos(self):
        return self.sensor_pos

    def calc_sensor_pos(self, car: Car):

        sensor = Vector2(0.0, 0.0)

        # with ppu
        start_point_x = car.position.x * car.ppu
        start_point_y = car.position.y * car.ppu
        car_angle = radians(car.angle)

        sensor.x = start_point_x + \
                cos(car_angle + self.add_angle) * int(self.sensor_length)
        sensor.y = start_point_y - \
                sin(radians(car.angle) + self.add_angle) * int(self.sensor_length)

        self.sensor_pos = sensor

        return sensor

    def draw_sensor_line(self, car, screen):
        pygame.draw.line(screen, (0, 255, 0), car.position *
                         car.ppu, self.get_sensor_pos())

    def get_dist_to_wall(self, car:Car, game):
        'Calculate distance to wall and multiply by sensor_length'

        temp_pos = car.position*car.ppu
        car_pos = tuple(map(int, temp_pos))
        sens_pos = tuple(map(int, self.get_sensor_pos()))

        ends = np.array([[*car_pos],
                         [*sens_pos]])

        line_points = self.connect(ends)

        # get pixel color of line points
        line_points_color = []
        for line_point in line_points:
            try:
                pix_val = game.BackGround.image.get_at(line_point)[:3]
            except IndexError:
                pix_val = (1, 1, 1)
            line_points_color.append(pix_val)

        # get index of first wall_pix
        try:
            itemindex = np.where(np.array(line_points_color)
                                 == self.wall_pix_color)[0][0]
            normalized_index = itemindex/line_points.shape[0]
        except IndexError:  # out of sensor distance
            normalized_index = -1
        distance_to_wall = normalized_index * self.sensor_length

        return distance_to_wall

    def connect(self, ends):
        d0, d1 = np.abs(np.diff(ends, axis=0))[0]
        if d0 > d1:
            return np.c_[np.linspace(ends[0, 0], ends[1, 0], d0+1, dtype=np.int32),
                         np.round(np.linspace(ends[0, 1], ends[1, 1], d0+1))
                         .astype(np.int32)]
        else:
            return np.c_[np.round(np.linspace(ends[0, 0], ends[1, 0], d1+1))
                         .astype(np.int32),
                         np.linspace(ends[0, 1], ends[1, 1], d1+1, dtype=np.int32)]


class DistSensorManager:

    all_dist_sensors: list

    def __init__(self):
        self.all_dist_sensors = []

    def add_sensors(self, sensor:List[DistSensor]):
        self.all_dist_sensors.extend(sensor)

    def update_sensor_positions(self, car:Car):
        'Updates the sensor position for each sensor in its list of sensors'
        for sensor in self.all_dist_sensors:
            sensor.calc_sensor_pos(car)
    
    def draw_sensor_lines(self, car:Car, screen:pygame.Surface):
        for sensor in self.all_dist_sensors:
            sensor.draw_sensor_line(car, screen)
    
    def get_distances(self, car:Car, game):
        'Calculate distance to wall for all sensors'
        distances = []
        for sensor in self.all_dist_sensors:
            distances.append(sensor.get_dist_to_wall(car, game))
        return distances
