from pygame.math import Vector2


class EnvironmentHandlerInputs:

    def __init__(self, car):

        self.car = car

    def check_border(self):
        'Collision with border'

        # width
        if self.car.position[0] < 0:
            self.car.position[0] = 0
        elif self.car.position[0] > 40:
            self.car.position[0] = 40

        # height
        if self.car.position[1] < 0:
            self.car.position[1] = 0
        elif self.car.position[1] > 22:
            self.car.position[1] = 22

    def check_on_track(self, game, track_pixel: list):

        c_pos = [int(self.car.position[0] * game.ppu),
                 int(self.car.position[1]*game.ppu)]  # in pixel
        if c_pos in track_pixel:
            on_track = True
        else:
            on_track = False

        return on_track


class EnvironmentHandlerActions:

    def reset_to_start(self, car):

        car.position = Vector2(car.reset_point)
        car.velocity = Vector2(0.0, 0.0)
        car.angle = 90.0
