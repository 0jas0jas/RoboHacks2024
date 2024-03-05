import pygame
import pygame_gui
import json
from communication import CommunicationInterface

class DigitalButton(pygame.sprite.Sprite):
    def __init__(self, image, position, key):
        super().__init__()
        self.original_image = image
        self.image = image
        self.rect = image.get_rect(center=position)
        self.pressed_image = pygame.transform.scale(self.original_image, (int(self.rect.width * 0.9), int(self.rect.height * 0.9)))
        self.key = key
        self.is_pressed = False

    def update(self, pressed):
        self.is_pressed = pressed
        self.image = self.pressed_image if self.is_pressed else self.original_image  # Change image based on pressed state
        

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class AnalogStick(pygame.sprite.Sprite):
    def __init__(self, image, position, axis1=-1, axis2=-1):
        super().__init__()
        self.img_static = pygame.image.load('sprites/controller/analog_stick.png')
        self.img_dynamic = pygame.image.load('sprites/controller/analog_stick_moving.png')
        self.rect_static = self.img_static.get_rect()
        self.rect_dynamic = self.img_dynamic.get_rect()
        self.rect_static.center = position
        self.rect_dynamic.center = position
        self.value_x = 0.0
        self.value_y = 0.0
        self.axis1 = axis1
        self.axis2 = axis2
        self.dragging = False

    def update(self, value_x, value_y):
        self.value_x = value_x
        self.value_y = value_y
        self.rect_dynamic.centerx = self.rect_static.centerx + value_x*50
        self.rect_dynamic.centery = self.rect_static.centery + value_y*50

    def draw(self, surface):

        surface.blit(self.img_static, self.rect_static)
        surface.blit(self.img_dynamic, self.rect_dynamic)


class Controller():

    analog_keyboard_keys = []

    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        pygame.display.set_caption("Robohacks Controls")
        self.window_surface = pygame.display.set_mode((800, 600))
        self.background = pygame.Surface((800, 600))
        self.background.fill(pygame.Color('#000000'))
        self.manager = pygame_gui.UIManager((800, 600))
        self.ip_text_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((10, 10), (140, 50)), manager=self.manager)
        self.connect_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((160, 10), (100, 50)), text='Connect', manager=self.manager)
        self.status_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((300, 10), (300, 50)), text='Status: Disconnected', manager=self.manager)
        self.controller_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((300, 250), (200, 50)), text='Controller Not Found', manager=self.manager)
        self.controller_text.hide()
        self.status_led = pygame.Rect(275, 25, 20, 20)
        self.input_mode_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((650, 10), (140, 50)),text='Mouse/Keyboard',manager=self.manager)
        self.clock = pygame.time.Clock()
        self.keyboard_input_map = None
        self.controller_input_map = None
        self.input_mode = True # Variable to track input mode (True for Mouse/Keyboard, False for Controller)
        self.comms_interface = None
        self.joystick = None

    def quit(self):
        self.comms_interface.closeSocket()
        pygame.quit()

    def handleEvent(self, event):
        if event.type == pygame.QUIT:
            self.quit()
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.connect_button:
                        if self.comms_interface.getSockConnection():
                            self.connect_button.set_text('Connect')
                            self.comms_interface.closeSocket()
                            self.status_text.set_text('Status: Disconnected')
                        else:
                            self.ip_input = self.ip_text_entry.get_text()
                            self.status_text.set_text(f"Status: Connecting to {self.ip_input}")
                            success = self.comms_interface.connectSocket(self.ip_input, 80)
                            if not success:
                                self.status_text.set_text(f"Problem with Connection")
                            else:
                                self.status_text.set_text(f"Status: Connected to {self.ip_input}")
                                self.connect_button.set_text('Disconnect')
                elif event.ui_element == self.input_mode_button:
                    # Toggle input mode
                    self.input_mode = not self.input_mode
                    self.input_mode_button.set_text('Controller' if not self.input_mode else 'Mouse/Keyboard')
                    if not self.input_mode:
                        self.comms_interface.updateData("controlType", "Keyboard", 0)
                        self.comms_interface.updateData("controlType", "Controller", 1)
                        if self.joystick == None and pygame.joystick.get_count() > 0:
                            self.joystick = pygame.joystick.Joystick(0)
                            self.joystick.init()
                        if self.joystick != None and pygame.joystick.get_count() == 0:
                            self.joystick = None
                        
                        if self.joystick == None:
                            self.controller_text.show()
                    else:
                        self.comms_interface.updateData("controlType", "Keyboard", 1)
                        self.comms_interface.updateData("controlType", "Controller", 0)
                        self.controller_text.hide()
        if event.type == pygame.MOUSEBUTTONDOWN and self.input_mode:
            for key in self.analog_keyboard_keys:
                obj = self.keyboard_input_map[key]
                if obj.rect_dynamic.collidepoint(event.pos):
                    obj.dragging = True

        if event.type == pygame.MOUSEBUTTONUP and self.input_mode:
            for key in self.analog_keyboard_keys:
                obj = self.keyboard_input_map[key]
                obj.dragging = False

        mouse_x, mouse_y = pygame.mouse.get_pos()
        for key in self.analog_keyboard_keys:
            obj = self.keyboard_input_map[key]
            if obj.dragging:
                offset_x = mouse_x - obj.rect_static.centerx
                offset_y = mouse_y - obj.rect_static.centery
                distance = (offset_x ** 2 + offset_y ** 2) ** 0.5
                if distance > 50:
                    normalized_x = offset_x / distance
                    normalized_y = offset_y / distance
                else:
                    normalized_x = offset_x / 50  
                    normalized_y = offset_y / 50
                obj.update(normalized_x, normalized_y)

        self.manager.process_events(event)

    def run(self):
        time_delta = self.clock.tick(60)/1000.0

        for event in pygame.event.get():
            self.handleEvent(event)

        self.window_surface.blit(self.background, (0, 0))
        self.manager.update(time_delta)
        self.manager.draw_ui(self.window_surface)

        if self.input_mode:
            keys = pygame.key.get_pressed()
            # Update button_map based on keyboard inputs

            for key, elem in self.keyboard_input_map.items():
                if isinstance(elem, AnalogStick):
                    self.comms_interface.updateData(key, "x", elem.axis1)
                    self.comms_interface.updateData(key, "y", elem.axis2)
                else:
                    elem.update(keys[elem.key])
                    self.comms_interface.updateData("keys", key, keys[elem.key])
                elem.draw(self.window_surface)
        else:
            # Update joystick/button states
            if self.joystick:
                for key, elem in self.controller_input_map.items():
                    if isinstance(elem, AnalogStick):
                        elem.update(self.joystick.get_axis(elem.axis1), self.joystick.get_axis(elem.axis2))
                        self.comms_interface.updateData(key, "x", self.joystick.get_axis(elem.axis1))
                        self.comms_interface.updateData(key, "y", self.joystick.get_axis(elem.axis2))
                    else:
                        elem.update(self.joystick.get_button(elem.key))
                        self.comms_interface.updateData("buttons", key, self.joystick.get_button(elem.key))
                    elem.draw(self.window_surface)
        
        if self.comms_interface.getSockConnection():
            err = self.comms_interface.sendUpdates()
            if (err):
                self.comms_interface.closeSocket()
                self.status_text.set_text('Status: Send Failed')
                self.connect_button.set_text('Connect')

        # Update the status LED color
        if 'Connected' in self.status_text.text:
            pygame.draw.rect(self.window_surface, (0, 255, 0), self.status_led)  # Green LED
        else:
            pygame.draw.rect(self.window_surface, (255, 0, 0), self.status_led)  # Red LED

        
        pygame.display.update()

    def getMaps(self, controller_map, keyboard_map):
        self.controller_input_map = controller_map
        self.keyboard_input_map = keyboard_map
        for key, value in keyboard_map.items():
            if isinstance(value, AnalogStick):
                self.analog_keyboard_keys.append(key)

    def startCommunications(self):
        self.comms_interface = CommunicationInterface()

def createUserConfig(controller_map, keyboard_map, config_path = "user_config.json"):
    data = {
        "controlType": {
            "Controller": 0,
            "Keyboard": 1
        }
    }
    for key, value in controller_map.items():
        if isinstance(value, AnalogStick):
            if key not in data:
                data[key] = {}
            data[key]["x"] = 0.0
            data[key]["y"] = 0.0
        else:
            if "buttons" not in data:
                data["buttons"] = {}
            data["buttons"][key] = 0

    for key, value in keyboard_map.items():
        if isinstance(value, AnalogStick):
            if key not in data:
                data[key] = {}
            data[key]["x"] = 0.0
            data[key]["y"] = 0.0
        else:
            if "keys" not in data:
                data["keys"] = {}
            data["keys"][key] = 0

    with open(config_path, 'w') as outfile:
        json.dump(data, outfile, indent=4)