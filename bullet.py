from typing import List

import numpy as np
import pygame

class Bullet:
  """
  A class representing a bullet in the game world.
  """
  def __init__(self,
      position: np.ndarray,
      velocity: np.ndarray,
      parent: "Tank",
      color: str = "#444444",
      damage: int = 10,
      range: float = 800):
    """
    Creates a new bullet object.

    Args:
    - position: A tuple of x and y coordinates representing the bullet's position
    - velocity: A tuple of x and y components representing the bullet's velocity
    - parent: A reference to the tank that fired the bullet
    - damage: An integer representing the amount of damage the bullet does
    """
    self.position: np.ndarray = position
    self.velocity: np.ndarray = velocity
    self.parent: "Tank" = parent
    self.color: str = color
    self.explosion_color: str = "#ff4400"
    self.origin: np.ndarray = parent.position
    self.damage: int = damage
    self.range: float = range
    self.sprite: pygame.Surface = pygame.Surface((6, 6))
    self.sprite.fill(pygame.Color(self.color))
    self.rect: pygame.Rect = self.sprite.get_rect(center=self.position)

    self.destroyed: bool = False


  def move(self, dt: float = 1):
    """
    Moves the bullet in the direction of its velocity.

    Args:
    - dt: The time delta since the last frame in seconds
    """
    if self.destroyed:
      return
    self.position += self.velocity * dt
    self.rect.center = self.position # Update the bullet's rect
    # if bullet travelled its maximum range, destroy it
    if np.linalg.norm(self.position - self.origin) >= self.range:
      self.destroy()


  def detect_bullet_collision(self, bullet: "Bullet"):
    """
    Detects collisions between this bullet and another bullet.

    Args:
    - bullet: The bullet to check for collisions with

    Returns:
    - True if the bullets collided, False otherwise
    """
    return self.rect.colliderect(bullet.rect)
  

  def detect_tank_collision(self, tank: "Tank"):
    """
    Detects collisions between this bullet and a tank.

    Args:
    - tank: The tank to check for collisions with

    Returns:
    - True if the bullet collided with the tank, False otherwise
    """
    if self.parent != tank:
      return self.rect.colliderect(tank.rect)


  def detect_wall_collision(self, wall_mask: pygame.mask.Mask) -> bool:
    """
    Detects if the tank is colliding with a wall.

    Args:
        wall_mask (pygame.mask.Mask): The mask of the wall to check for collision.

    Returns:
        bool: True if the tank is colliding with the wall, False otherwise.
    """
    # Calculate the offset between the tank and the wall
    offset = (
        self.rect.topleft[0] - wall_mask.get_rect().topleft[0],
        self.rect.topleft[1] - wall_mask.get_rect().topleft[1])

    self_mask = pygame.mask.from_surface(self.sprite)
    # Check if the masks overlap using the collide_mask method
    return wall_mask.overlap(self_mask, offset) is not None


  def destroy(self):
    """
    Destroys the bullet.
    """
    # hide the bullet
    self.destroyed = True


  def draw(self, screen: pygame.Surface):
    """
    Draws the bullet onto the game screen.

    Args:
    - screen: The surface to draw the bullet onto
    """
    if not self.destroyed:
      screen.blit(self.sprite, self.rect)
    else:
      # If the bullet is destroyed, draw a small explosion
      pygame.draw.circle(screen, pygame.Color(self.explosion_color), self.position, 10)
