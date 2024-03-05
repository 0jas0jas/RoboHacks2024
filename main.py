import pygame
from gui import Controller, AnalogStick, DigitalButton, createUserConfig

controller = Controller() #Main Controller for GUI

###### CONTROLLER MAPPING ######

## UNUSED (No available controllers)
controller_input_map = {
    "leftStick": AnalogStick(None,(300,400), 0, 1),
    "rightStick": AnalogStick(None,(500,400), 2, 3),
    "UP" : DigitalButton(pygame.image.load('sprites/controller/dir_up.png'), (125,200), 11),
    "DOWN" : DigitalButton(pygame.image.load('sprites/controller/dir_down.png'), (125,300), 12),
    "LEFT" : DigitalButton(pygame.image.load('sprites/controller/dir_left.png'), (75,250), 13),
    "RIGHT" : DigitalButton(pygame.image.load('sprites/controller/dir_right.png'), (175,250), 14),
    "Y" : DigitalButton(pygame.image.load('sprites/controller/btn_y.png'), (675,200), 3),
    "A" : DigitalButton(pygame.image.load('sprites/controller/btn_a.png'), (675,300), 0),
    "X" : DigitalButton(pygame.image.load('sprites/controller/btn_x.png'), (625,250), 2),
    "B" : DigitalButton(pygame.image.load('sprites/controller/btn_b.png'), (725,250), 1)
}

################################

###### MOUSE/KEYBOARD MAPPING ######

# TO ADD MORE KEYS/STICKS
# COPY A LINE AND CHANGE THE PARAMETERS
# EXAMPLE (changes needed to make are underlined):
# "U" : DigitalButton(pygame.image.load('sprites/keyboard/key_u.png'), (350, 400), pygame.K_u)
#  _                                                          _         ___  ___            _
# 
# "U" is the name of the variable associated with this key. Arduino code will use this to get the value.
# pygame.image.load('sprites/keyboard/key_u.png') is the image shown. All keyboard keys are available (change letter)
# (350, 400) are the coordinates in the GUI. Change these to display the key at a new location
#  pygame.K_u is the mapping to the key you want associated with it. Change the "_u" to your chosen letter
#
# For adding an Analog Stick, only changing the variable name and coordinates is necessary

keyboard_input_map = {
    "mouseStick1": AnalogStick(None,(500,200)),
    "mouseStick2": AnalogStick(None,(700,200)),
    "UP" : DigitalButton(pygame.image.load('sprites/keyboard/key_up.png'), (600,390), pygame.K_UP),
    "DOWN" : DigitalButton(pygame.image.load('sprites/keyboard/key_down.png'), (600,450), pygame.K_DOWN),
    "LEFT" : DigitalButton(pygame.image.load('sprites/keyboard/key_left.png'), (480,450), pygame.K_LEFT),
    "RIGHT" : DigitalButton(pygame.image.load('sprites/keyboard/key_right.png'), (720,450), pygame.K_RIGHT),
    "W" : DigitalButton(pygame.image.load('sprites/keyboard/key_w.png'), (100,200), pygame.K_w),
    "A" : DigitalButton(pygame.image.load('sprites/keyboard/key_a.png'), (100,400), pygame.K_a),
    "S" : DigitalButton(pygame.image.load('sprites/keyboard/key_s.png'), (250,200), pygame.K_s),
    "D" : DigitalButton(pygame.image.load('sprites/keyboard/key_d.png'), (250,400), pygame.K_d)
}

####################################

createUserConfig(controller_input_map, keyboard_input_map) #generates JSON file

controller.startCommunications() #starts controller's communications

controller.getMaps(controller_input_map, keyboard_input_map) #links mapping to controller

while True:

    controller.run() #runs the controller