import numpy as np
import pygame

from tank import Tank

class Controller:
    """
    A class representing a game controller. Supports analog joystick input.
    """
    def __init__(self, controller_id: int):
        """
        Creates a new controller object with the given ID.

        Args:
        - controller_id: An integer representing the ID of the controller (e.g. 0 for the first connected controller)
        """
        pygame.init()
        pygame.joystick.init()

        self.controller = pygame.joystick.Joystick(controller_id)
        self.controller.init()

    def get_inputs(self):
        """
        Returns a dictionary containing the current input from the controller.

        Returns:
        - A dictionary with the following keys:
            - move_direction: A numpy array with two floats in range [-1,1] representing the movement direction (left joystick)
            - turret_direction: A numpy array with two floats in range [-1,1] representing the turret direction (right joystick)
            - fire: A boolean indicating whether the fire button is currently pressed
        """
        pygame.event.get()

        # Get joystick input
        move_direction = np.array([self.controller.get_axis(0), self.controller.get_axis(1)])
        turret_direction = np.array([self.controller.get_axis(2), self.controller.get_axis(3)])

        # Apply deadzone to joystick input
        move_direction = self.apply_deadzone(move_direction)
        turret_direction = self.apply_deadzone(turret_direction)

        # # Normalize joystick input
        # move_direction = move_direction / np.linalg.norm(move_direction)
        # turret_direction = turret_direction / np.linalg.norm(turret_direction)

        # Get fire button input (right analog trigger or right shoulder button)
        fire: bool = self.controller.get_axis(5) > -0.9 or \
						self.controller.get_button(5)

        # Return input dictionary
        return {"move_direction": move_direction, "turret_direction": turret_direction, "fire": fire}

    def apply_deadzone(self, value, deadzone=0.1):
        """
        Applies a deadzone to the given input value.

        Args:
        - value: A numpy array representing the input value
        - deadzone: A float representing the deadzone threshold (default: 0.05)

        Returns:
        - A numpy array with the same shape as the input value, with values below the deadzone threshold set to zero.
        """
        if np.linalg.norm(value) < deadzone:
            return None
        else:
            return value
