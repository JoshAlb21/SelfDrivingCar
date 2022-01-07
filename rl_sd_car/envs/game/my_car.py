from pygame.math import Vector2
import pygame
from math import sin, cos, tan, sqrt, radians, degrees, copysign, pi, radians
from numpy import ones,vstack
from numpy.linalg import lstsq
import numpy as np


class Car:

    car_image: pygame.Surface
    ppu: int

    def __init__(self, car_image, x, y, angle=0.0, length=4, max_steering=30, max_acceleration=5.0, ppu=40):

        self.position = Vector2(x, y) #without ppu
        self.last_track_position = Vector2(0, 0) #position 1 frame ago
        self.velocity = Vector2(0.0, 0.0) # m/sec
        self.angle = angle #degrees
        self.length = length #meter kleinerer Wendekreis
        self.max_acceleration = max_acceleration #meters/second squared
        self.max_steering = max_steering
        self.max_velocity = 20
        self.brake_deceleration = 20 #10
        self.free_deceleration = 2
        self.inertia = 15 #traegheit
        self.steering_increase = 80
        self.car_image = car_image
        self.reset_point = x, y
        self.ppu = ppu

        self.not_on_track_fee = (2.0,0)
        self.max_vel_off_track = (5.0, 0)
        
        self.car_length, self.car_width = self.car_image.get_size()
        self.acceleration = 0.0
        self.steering = 0.0 #deegres positive-left, negative-right

        self.l_f_corner = Vector2(0.0, 0.0)
        self.r_f_corner = Vector2(0.0, 0.0)
        self.angle_differ = 0
        self.sensor1 = DistSensor('sensor1', 'left', 300)
        self.sensor2 = DistSensor('sensor2', 'right', 300)
    
    def handle_not_on_track(self):
        if self.velocity.x >= self.max_vel_off_track[0] and self.velocity.y >= self.max_vel_off_track[1] and self.velocity[0] > 0:
            self.velocity -= self.not_on_track_fee

    def update(self, dt): #update every frame
        self.velocity += (self.acceleration * dt, 0) #integrate to velocity, no sideways acceleration
        self.velocity.x = max(-self.max_velocity, min(self.velocity.x, self.max_velocity))

        #Left front corner
        self.l_f_corner.x = self.position.x *self.ppu + cos(radians(self.angle) + tan(self.car_width/self.car_length)) * int(sqrt(pow(self.car_length / 2, 2) + pow(self.car_width / 2, 2)))
        self.l_f_corner.y = self.position.y *self.ppu - sin(radians(self.angle) + tan(self.car_width/self.car_length)) * int(sqrt(pow(self.car_length / 2, 2) + pow(self.car_width / 2, 2)))
        #Right front corner
        self.r_f_corner.x = self.position.x * self.ppu + cos(radians(self.angle) - tan(self.car_width / self.car_length)) * int(sqrt(pow(self.car_length / 2, 2) + pow(self.car_width / 2, 2)))
        self.r_f_corner.y = self.position.y * self.ppu - sin(radians(self.angle) - tan(self.car_width / self.car_length)) * int(sqrt(pow(self.car_length / 2, 2) + pow(self.car_width / 2, 2)))

        #compute sensor position, and vectorized line
        self.sensor1.calc_sensor_pos(self, tan(self.car_width/self.car_length))
        self.sensor2.calc_sensor_pos(self, tan(self.car_width / self.car_length))

        if self.steering:
            turning_radius = self.length / sin(radians(self.steering))
            angular_velocity = self.velocity.x / turning_radius
        else:
            angular_velocity = 0

        self.position += self.velocity.rotate(-self.angle) * dt
        self.angle += degrees(angular_velocity) * dt


class DistSensor: #TODO hier weiter machen

    name:str
    side:str # left oder right
    sensor_pos:Vector2 #with ppu
    sensor_length: int

    def __init__(self, name, side, sensor_length):
        
        self.name = name
        self.side = side
        self.sensor_length = sensor_length

    def get_sensor_pos(self):
        return self.sensor_pos

    def calc_sensor_pos(self, car:Car, angle):

        sensor = Vector2(0.0,0.0)
        if self.side == "left":
            sensor.x = car.position.x * car.ppu + cos(radians(car.angle) + tan(car.car_width / car.car_length)) * int(self.sensor_length)
            sensor.y = car.position.y * car.ppu - sin(radians(car.angle) + tan(car.car_width / car.car_length)) * int(self.sensor_length)
        elif self.side == "right":
            sensor.x = car.position.x * car.ppu + cos(radians(car.angle) - tan(car.car_width / car.car_length)) * int(self.sensor_length)
            sensor.y = car.position.y * car.ppu - sin(radians(car.angle) - tan(car.car_width / car.car_length)) * int(self.sensor_length)

        self.sensor_pos = sensor

        return sensor

    def draw_sensor_line(self, car, screen):
        pygame.draw.line(screen, (0, 255, 0), car.position * car.ppu, self.get_sensor_pos())

    def get_dist_to_wall(self, car, wall_pix_color:tuple, screen, game):
        'calculate distance to wall and multiply by sensor_length'

        temp_pos = car.position*car.ppu
        car_pos = tuple(map(int, temp_pos))
        sens_pos = tuple(map(int, self.get_sensor_pos()))

        ends = np.array([[ *car_pos],
                 [*sens_pos]])

        line_points = self.connect(ends)

        # get pixel color of line points
        line_points_color = []
        for line_point in line_points:
            try:
                pix_val = game.BackGround.image.get_at(line_point)[:3]
            except IndexError:
                pix_val = (1,1,1)
            line_points_color.append(pix_val)
        

        # get index of first wall_pix
        try:
            itemindex = np.where(np.array(line_points_color)==wall_pix_color)[0][0]
            normalized_index = itemindex/line_points.shape[0]
        except IndexError: #out of sensor distance
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

        