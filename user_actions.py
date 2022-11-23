from kivy.uix.relativelayout import RelativeLayout

def _keyboard_closed(self):
    self._keyboard.unbind(on_key_down=self._on_keyboard_down)
    self._keyboard.unbind(on_key_up=self._on_keyboard_up)
    self._keyboard = None

def on_touch_down(self, touch):
    if not self.game_over and self.game_started:
        if touch.x < self.width/2:
            self.current_speed_x = self.SPEED_X
        else:
            self.current_speed_x = -self.SPEED_X
    return super(RelativeLayout, self).on_touch_down(touch)

def on_touch_move(self, touch): 
    if not self.game_over and self.game_started:
        if touch.x < self.width/2:
            self.current_speed_x = self.SPEED_X
        else:
            self.current_speed_x = -self.SPEED_X

def on_touch_up(self, touch):
    self.current_speed_x = 0

def on_keyboard_down(self, keyboard, keycode, text, modififiers):
    if keycode[1] == "left" and self.current_speed_x <= 0:
        self.current_speed_x += self.SPEED_X
    elif keycode[1] == "right" and self.current_speed_x >= 0:
        self.current_speed_x -= self.SPEED_X
    return True

def on_keyboard_up(self, keyboard, keycode):
    if keycode[1] == "left":
        self.current_speed_x -= self.SPEED_X
    elif keycode[1] == "right":
        self.current_speed_x += self.SPEED_X
    return True