import pygame

class Map:
    """
    A class representing a map in the tank game.
    """
    def __init__(self, map_image_path):
        # Load map image and convert to grayscale
        self.map_image = pygame.image.load(map_image_path).convert_alpha()
        self.width, self.height = self.map_image.get_size()
        self.mask = pygame.mask.from_surface(self.map_image, 127)

    def is_wall(self, position):
        # Check if pixel at given position is black in mask
        x, y = int(position[0]), int(position[1])
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.mask.get_at((x, y)) == 1
        else:
            # Position is outside of map bounds
            return True