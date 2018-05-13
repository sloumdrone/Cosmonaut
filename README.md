# Cosmonaut

A SHMUP for the terminal! 


## Design and Implementation

Cosmonaut is written in Python 2.7. This was a deliberate choice due to its ubiquity on modern Apple OSX systems (among many others). Cosmonaut only utilizes the Python standard library so that it can be acquired and run by many systems without installing dependencies (shell script "installer" for moving it to the path coming soon).

## Gameplay

At present, gameplay is basic SHMUP territory: Move around and shoot the things that are shooting at you!
The player opperates on a rail with only left and right movement. Due to the way the terminal/curses handles keypresses movement opperates based on a left/right toggle, rather than the more common hold to move and release to stop moving. 

#### Controls
  | Key           | Action        |
  |:-------------:|:-------------:|
  | LEFT          | Move left     |
  | RIGHT         | Move right    |
  | SPACE         | Fire/Shoot    |
  | UP            | Fire/Shoot    |
  | DOWN          | Brakes/Stop   |
  | Q             | Quit/Exit     |
  

  
  
