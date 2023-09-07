# Tanks pygame

This program is a recreation of a game I originally made in scratch between 2010 and 2014. Each player controls a tank and tries to shoot the other players.

The game only works with controllers, there is currently no keyboard/ mouse support.
The number of players is determined by the number of controllers connected when launching the program.

## Controls
- Aim with right stick (turret instantly points in the direction of the stick)
- shoot with right trigger
- move with left stick:
    - up/ down = forward/ backward
    - right/ left = turn right/ left

## Known issues
- With some player counts, players start out on walls and cannot move at all. Workaround: change the map. (`map_1.png`)
- Collision detection is based on bounding boxes of objects, not on the actual shape of the objects.
- driving into a wall sometimes causes the tank to get stuck in the wall.
- There is no keyboard/ mouse support.
- There is no disadvantage to always shooting.
