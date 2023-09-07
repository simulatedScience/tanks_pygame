import time

import numpy as np
import pygame

from bullet import Bullet

class Tank(pygame.sprite.Sprite):
  """
  A class representing a tank in the game world.
  Tanks are shown as rectangles with a turret on top. The turret is constructed from a circle and a rectangle.
  The tank can be moved, rotated and fired. The turret can also be rotated separately from the tank.
  """
  def __init__(self,
               position: np.ndarray,
               rotation: float,
               color: str,
               bullet_color: str = None,
               velocity: np.ndarray = np.zeros(2),
               fire_cooldown: float = 0.5,
               health: int = 100,
               max_health: int = 100,
               name: str=""):
    """
    Creates a new tank object.

    Args:
    - position: A tuple of x and y coordinates representing the tank's position 
    - rotation: A float representing the angle of the tank's turret in degrees
    - color: A string representing the color of the tank
    - velocity: A tuple of x and y components representing the tank's velocity
    - health: An integer representing the tank's remaining health
    - max_health: An integer representing the tank's maximum health
    """
    super().__init__()
    self.position: np.ndarray = position
    self.last_position: np.ndarray = position
    self.rotation: float = rotation
    print(f"placing tank at {position} with rotation {self.rotation}")
    self.last_rotation: float = self.rotation
    self.turret_rotation: float = np.mod(rotation + 180, 360.0)
    
    self.name: str = name

    self.velocity: np.ndarray = velocity
    self.rotation_speed = 100.0  # Degrees per second
    self.max_speed: float = 2  # Pixels per second

    self.new_velocity: np.ndarray = self.velocity
    self.new_rotation: float = self.rotation
    self.new_turret_rotation: float =self.turret_rotation
    # gameplay parameters
    self.fire_cooldown: float = fire_cooldown
    self.last_fired: float = time.time()
    self.bullet_damage: int = 10
    self.health: int = health
    self.max_health: int = max_health
    # parameters for the tank's sprite
    self.color: str = color
    self.bullet_color: str = bullet_color if bullet_color else color
    self.turret_offset: np.ndarray = np.array([-8, 0])
    self.tank_length, self.tank_width = 60, 30
    self.turret_radius: int = 15 # in pixels
    self.cannon_length, self.cannon_width = 25, 10
    self.health_bar_height: int = 10
    self.health_bar_y_offset: int = self.tank_length//2# + self.health_bar_height
    # self.fire_sound: pygame.mixer.Sound = pygame.mixer.Sound("sounds/mixkit-cinematic-laser-swoosh-1467.wav")
    self.create_sprite()


  def update_movement(self, move_direction: np.ndarray, dt: float):
    if move_direction is None:
      move_direction: np.ndarray = np.zeros(2)
    # Rotate the tank
    rotation_direction: float = move_direction[0]
    self.new_rotation: float = self.rotation - rotation_direction * self.rotation_speed * dt
    self.new_rotation: float = np.mod(self.new_rotation, 360.0)
    self.new_turret_rotation: float = self.turret_rotation - rotation_direction * self.rotation_speed * dt
    self.new_turret_rotation: float = np.mod(self.new_turret_rotation, 360.0)
    # Calculate the acceleration vector
    forward_direction: np.ndarray = np.array([np.cos(np.deg2rad(self.rotation)), -np.sin(np.deg2rad(self.rotation))])
    self.new_velocity: np.ndarray = forward_direction * move_direction[1] * self.max_speed


  def aim(self, turret_direction: np.ndarray, dt: float):
    """
    Rotate the turret to aim at the given direction.

    Args:
        turret_direction (np.ndarray): A tuple of x and y components representing the direction to aim at. If None, do not change the turret's rotation.
    """
    if turret_direction is not None:
      # rotate turret
      self.new_turret_rotation: float = np.rad2deg(np.arctan2(-turret_direction[1], turret_direction[0]))
      # rotation_direction: np.ndarray = turret_direction[0]
      # # cannot rotate cannon more than 90° to either side
      # self.new_turret_rotation -= rotation_direction * self.rotation_speed * dt
      # self.new_turret_rotation: float = np.mod(self.new_turret_rotation, 360.0)
      # if abs(self.new_rotation - self.new_turret_rotation) < 70:
      #   self.new_turret_rotation = self.turret_rotation


  def move(self):
    self.last_position = self.position.copy()
    self.last_rotation = self.rotation
    # Update the position and rotation
    self.position += self.new_velocity
    self.velocity: np.ndarray = self.new_velocity
    self.rotation: float = self.new_rotation
    self.turret_rotation: float = self.new_turret_rotation

    self.new_velocity: np.ndarray = np.zeros(2)
    self.new_rotation = self.rotation

  def reset_to_last_position(self):
    if np.any(self.last_position != self.position):
      self.position: np.ndarray = self.last_position
      self.rotation: float = self.last_rotation

      self.new_velocity: np.ndarray = np.zeros(2)
      self.new_rotation: float = self.rotation


  def fire(self) -> Bullet:
    """
    Fire a bullet from the tank's cannon in the direction of the turret's rotation. Update the `last_fired` time to limit the fire rate.

    Returns:
        Bullet: A bullet object if the tank can fire, None otherwise.
    """
    if time.time() - self.last_fired < self.fire_cooldown:
      return None
    self.last_fired: float = time.time()
    # calculate bullet velocity from turret rotation
    cannon_direction = np.array([np.cos(np.deg2rad(self.turret_rotation)), -np.sin(np.deg2rad(self.turret_rotation))])
    bullet_velocity: np.ndarray =  cannon_direction * 300 + self.velocity
    
    bullet_position = self.position + cannon_direction * self.cannon_length
    # play fire sound
    # self.fire_sound.play()
    
    return Bullet(
      position=bullet_position,
      velocity=bullet_velocity,
      parent=self,
      color=self.bullet_color,
      damage=self.bullet_damage
    )


  def damage(self, damage: int):
    """
    Reduce the tank's health by the given amount.

    Args:
        damage (int): The amount of damage to deal.
    """
    self.health = max(0, self.health - damage)


  def detect_tank_collision(self, other_tank: "Tank") -> bool:
    """
    Detects if the tank is colliding with another tank.

    Args:
        other_tank (Tank): The other tank to check for collision.

    Returns:
        bool: True if the tanks are colliding, False otherwise.
    """
    # Get the masks for both tanks
    self_mask = pygame.mask.from_surface(self.image)
    other_mask = pygame.mask.from_surface(other_tank.image)

    # Calculate the offset between the two tanks
    offset = (other_tank.rect.bottomleft[0] - self.rect.bottomleft[0],other_tank.rect.bottomleft[1] - self.rect.bottomleft[1])
    return self_mask.overlap(other_mask, offset) is not None

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
        wall_mask.get_rect().topleft[0] - self.rect.topleft[0],
        wall_mask.get_rect().topleft[1] - self.rect.topleft[1])
    # Check if the masks overlap using the collide_mask method
    return self.mask.overlap(wall_mask, offset) is not None


  def create_sprite(self, turret_color: str = "#222222"):
    """
    Create surfaces for the tank using the given color.
    Also create a surface for the turret (black circle) and the cannon (black rectangle).
    """
    self.rect = pygame.Rect(
        self.position[0] - self.tank_length / 2,
        self.position[1] - self.tank_width / 2,
        self.tank_length,
        self.tank_width)
    self.image = pygame.Surface((self.tank_length, self.tank_width), pygame.SRCALPHA)
    pygame.draw.rect(self.image, pygame.Color(self.color), (0, 0, self.tank_length, self.tank_width))
    self.mask: pygame.mask.Mask = pygame.mask.from_surface(self.image)
    
    self.turret_rect = pygame.Rect(
        self.position[0] - self.turret_radius - self.turret_offset[0],
        self.position[1] - self.turret_radius - self.turret_offset[1],
        self.turret_radius * 2 - self.turret_offset[0],
        self.turret_radius * 2 - self.turret_offset[1])
    self.turret_image = pygame.Surface((self.turret_radius * 2, self.turret_radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(self.turret_image, pygame.Color(turret_color), (self.
    turret_radius, self.turret_radius), self.turret_radius)
    
    self.cannon_rect = pygame.Rect(
        self.position[0],
        self.position[1] - self.cannon_width/2,
        self.cannon_width,
        self.cannon_length)
    self.cannon_image = pygame.Surface((self.cannon_length, self.cannon_width), pygame.SRCALPHA)
    pygame.draw.rect(self.cannon_image, pygame.Color(turret_color), (0, 0, self.cannon_length, self.cannon_width))

    # create a health bar above the tank
    self.health_bar = pygame.Surface((self.tank_length, self.health_bar_height), pygame.SRCALPHA)
    pygame.draw.rect(self.health_bar, pygame.Color("#00aa00"), (0, 0, self.tank_length, 275))
    
    # create player name text
    


  def draw(self, screen: pygame.Surface):
    """
    Draw the tank and its turret onto the game screen.
    """
    # move tank image
    self.rect.center = self.position
    # rotate tank image
    rotated_tank_image = pygame.transform.rotate(self.image, self.rotation)
    # rotate the cannon image
    rotated_cannon_image = pygame.transform.rotate(self.cannon_image, self.turret_rotation)
    
    # move and rotate tank
    rotated_tank_rect = rotated_tank_image.get_rect(center=self.rect.center)
    screen.blit(rotated_tank_image, rotated_tank_rect)
    # move turret
    tank_front = np.array([np.cos(np.deg2rad(self.rotation)), -np.sin(np.deg2rad(self.rotation))])
    turret_offset = - tank_front * self.turret_offset[0]
    turret_rect = self.turret_image.get_rect(center=self.rect.center + turret_offset)
    screen.blit(self.turret_image, turret_rect)
    # move and rotate cannon
    cannon_offset = np.array([np.cos(np.deg2rad(self.turret_rotation)), -np.sin(np.deg2rad(self.turret_rotation))]) * self.turret_radius
    rotated_cannon_rect = rotated_cannon_image.get_rect(center=self.rect.center + cannon_offset + turret_offset)
    screen.blit(rotated_cannon_image, rotated_cannon_rect)

    # calculate health bar position and width
    health_bar_width = int(self.health / self.max_health * self.tank_length)
    health_bar_left = int(self.rect.centerx - self.tank_length / 2)
    
    # create health bar surface
    self.health_bar = pygame.Surface((self.tank_length, self.health_bar_height), pygame.SRCALPHA)

    
    # draw health bar background
    pygame.draw.rect(self.health_bar, pygame.Color("#cccccc"), (0, 0, self.tank_length, self.health_bar_height))
    
    # draw health bar fill
    if self.health / self.max_health < 0.3:
        self.health_bar.fill(pygame.Color("#cc0000"), (0, 0, health_bar_width, self.health_bar_height))
    elif self.health / self.max_health < 0.6:
        self.health_bar.fill(pygame.Color("#cc8800"), (0, 0, health_bar_width, self.health_bar_height))
    else:
        self.health_bar.fill(pygame.Color("#00aa00"), (0, 0, health_bar_width,107))
    
    # draw health bar border
    pygame.draw.rect(self.health_bar, pygame.Color("#000000"), (0, 0, self.tank_length, self.health_bar_height + 2), 2)
    
    # draw health bar
    screen.blit(self.health_bar, (health_bar_left, self.rect.top - self.health_bar_height - self.health_bar_y_offset))