from os import walk
import pygame

WIDTH, HEIGHT = 864, 768

pipe_pair_sizes = [
    (1, 7),
    (2, 6),
    (3, 5),
    (4, 4),
    (5, 3),
    (6, 2),
    (7, 1)
]
pipe_size = HEIGHT // 10
pipe_gap = (pipe_size * 2) + (pipe_size // 2) - 30
ground_space = 100


def import_sprite(path):
    surface_list = []
    for _, __, img_file in walk(path):
        for image in img_file:
            full_path = f"{path}/{image}"
            img_surface = pygame.image.load(full_path).convert_alpha()
            surface_list.append(img_surface)
    return surface_list
