import pygame
from PIL import Image


class Background(pygame.sprite.Sprite):

    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location

    def get_pixel(self):

        width, height = self.image.get_size()
        white_pix = []
        corner_pix = []
        green_pix = []

        for x in range(1, width-1):
            for y in range(1, height-1):

                # check for white
                if self.image.get_at((x, y))[:3] == (255, 255, 255):
                    white_pix.append([x, y])

                # check env
                n_black = 0
                env = [self.image.get_at((x-1, y-1))[:3], self.image.get_at((x, y-1))[:3], self.image.get_at((x+1, y-1))[:3],
                       self.image.get_at(
                           (x-1, y))[:3], self.image.get_at((x+1, y))[:3], self.image.get_at((x-1, y+1))[:3],
                       self.image.get_at((x, y+1))[:3], self.image.get_at((x+1, y+1))[:3]]
                for i in env:
                    if i == (0, 0, 0):
                        n_black += 1
                if n_black != 0 and self.image.get_at((x, y))[:3] == (255, 255, 255):
                    corner_pix.append([x, y])

                # check green
                if self.image.get_at((x, y))[:3] == (34, 177, 76):
                    green_pix.append([x, y])

        return white_pix, corner_pix, green_pix
