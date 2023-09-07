import pygame
import numpy as np
from typing import List

from tank import Tank
from bullet import Bullet
from controller import Controller

class Game:
  """
  A class representing the game instance.
  """
  def __init__(self):
    # set fullscreen mode
    self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    self.tanks: List[Tank] = []
    self.bullets: List[Bullet] = []
    self.controllers: List[Controller] = []
    self.clock = pygame.time.Clock()
    self.running = False
    self.max_players = 8
    self.player_colors = ["#33dd33", "#dd33dd", "#5588ff", "#dd8833", "#ffdd33", "#33ffdd", "#ff33dd", "#33ddff"]
    self.bullet_colors = ["#22aa22", "#aa22aa", "#2255aa", "#aa5522", "#aa9922", "#22aaaa", "#aa22aa", "#22aaff"]
    self.init_game("map_1.png")


  def init_game(self, map_path: str):
    """
    Initializes the game:
    Create two tank objects, one for each player.
    Create and connect Controller objects to the tanks.
    Start game loop

    Args:
    - map_path (str): The path to the map image
    """
    # check if there are at least two controllers connected
    # if pygame.joystick.get_count() < 2:
    #   raise Exception("Not enough controllers connected!")
    self.map_mask = load_map(map_path)
    # scale map to screen size
    print(f"screen size: {self.screen.get_size()}")
    self.map_mask = self.map_mask.scale(self.screen.get_size())
    map_center: np.ndarray() = np.array(self.map_mask.get_size()) / 2
    self.map_mask.invert()
    self.map_image = self.map_mask.to_surface()
    self.map_mask.invert()
    # reset variables
    self.tanks: List[Tank] = []
    self.bullets: List[Bullet] = []
    self.controllers: List[Controller] = []
    for controller_id in range(min(pygame.joystick.get_count(), self.max_players)):
      # place single placer in the center of the map
      if pygame.joystick.get_count() == 1:
        angle = 0
        position = np.zeros(2) + map_center
      # otherwise distribute players evenly on a circle
      else:
        angle = controller_id * 2 * np.pi / pygame.joystick.get_count()
        position = np.array([np.cos(angle), np.sin(angle)]) * 350 + map_center
      self.tanks.append(
        Tank(
          position=position,
          rotation=-np.rad2deg(angle),
          color=self.player_colors[controller_id],
          bullet_color=self.bullet_colors[controller_id],
          health=100,
          max_health=100,
        )
      )
      self.tanks[-1].draw(self.screen)
      self.tank_sprite_group = pygame.sprite.Group(*self.tanks)
      # create controller
      if controller_id < pygame.joystick.get_count():
        self.controllers.append(Controller(controller_id))


  def handle_inputs(self, dt: float):
    """
    Handle inputs from controllers and keyboard.

    Args:
        dt (float): Time since last frame in seconds
    """
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        self.running = False
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
          self.running = False
    for tank, controller in zip(self.tanks, self.controllers):
      if tank.health <= 0:
        continue
      inputs = controller.get_inputs()
      tank.update_movement(inputs["move_direction"], dt)
      tank.aim(inputs["turret_direction"], dt)
      if inputs["fire"]:
        new_bullet = tank.fire()
        if new_bullet is not None:
          self.bullets.append(new_bullet)


  def update(self, dt: float):
    hit_bullets: List[Bullet] = []
    for bullet_1 in self.bullets:
      if bullet_1.destroyed:
        hit_bullets.append(bullet_1)
        continue
      # check if bullet hits another bullet
      for bullet_2 in self.bullets:
        if bullet_1 is bullet_2:
          break
        if bullet_1 in hit_bullets:
          continue
        if bullet_1.detect_bullet_collision(bullet_2):
          hit_bullets.append(bullet_1)
          hit_bullets.append(bullet_2)
          continue
      # check if bullet hits a tank
      for i, tank in enumerate(self.tanks):
        if bullet_1.detect_tank_collision(tank):
          tank.damage(bullet_1.damage)
          hit_bullets.append(bullet_1)
          if tank.health <= 0:
            self.game_end = True
      # destroy bullet if it hits a wall
      if bullet_1.detect_wall_collision(self.map_mask):
        hit_bullets.append(bullet_1)

    for bullet in hit_bullets:
      if bullet in self.bullets:
        self.bullets.remove(bullet)
        bullet.destroy()
        bullet.draw(self.screen)
        del bullet

    for bullet in self.bullets:
      bullet.move(dt)
    
    if len(self.tanks) == 1:
      tank: Tank = self.tanks[0]
      if tank.detect_wall_collision(self.map_mask):
        tank.reset_to_last_position()
      else:
        tank.move()
    else:
      for tank in self.tanks:
        for tank_2 in self.tanks:
          if tank is tank_2:
            continue
          if tank.detect_tank_collision(tank_2):
            tank.reset_to_last_position()
            tank_2.reset_to_last_position()
            break
          elif tank.detect_wall_collision(self.map_mask):
            tank.reset_to_last_position()
            break
          else:
            tank.move()


  def draw(self):
    for tank in self.tanks:
      tank.draw(self.screen)

    for bullet in self.bullets:
      bullet.draw(self.screen)

    # for wall in self.walls:
    #   pygame.draw.rect(self.screen, (0, 0, 0), wall)
    
    pygame.display.flip()


  def run(self):
    self.running = True
    # bind ESC key to quit
    # pygame.key.set_repeat(1, 1)
    
    while self.running: # main game loop
      dt = self.clock.tick(60) / 1000.0
      
      # draw map
      self.screen.blit(self.map_image, (0, 0))
      self.handle_inputs(dt)
      self.update(dt)
      self.draw()
    
    pygame.quit()


def load_map(map_path: str):
  """
  Loads a map from a file
  """
  map_mask = pygame.mask.from_surface(pygame.image.load(map_path))
  return map_mask


if __name__ == "__main__":
  pygame.init()
  game = Game()
  # game.add_tank(np.array([100, 100]), 0, "#222222")
  # game.add_wall(pygame.Rect(100, 100, 100, 100))
  game.run()