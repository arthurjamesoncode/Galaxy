from kivy.config import Config
Config.set('graphics', 'width', '1800')
Config.set("graphics", "height", "800")

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.properties import NumericProperty, StringProperty, ObjectProperty, Clock
from kivy.graphics.vertex_instructions import Line, Quad, Triangle
from kivy.graphics.context_instructions import Color
from kivy import platform

import random

Builder.load_file("menu.kv")

class MainWidget(RelativeLayout):
    from transforms import transform, transform_2D, transform_perspective
    from user_actions import _keyboard_closed, on_keyboard_down, on_keyboard_up, on_touch_down, on_touch_up, on_touch_move, adjust_x_speed

    menu_widget = ObjectProperty()
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)
    
    V_NB_LINES = 8
    V_LINES_SPACING = 0.4
    vertical_lines = []

    H_NB_LINES = 10
    H_LINES_SPACING = 0.2
    horizontal_lines = []

    SPEED_Y = 0.5
    SPEED_X = 2

    NB_TILES = 10
    tiles = []

    SHIP_WIDTH = 0.1
    SHIP_HEIGHT = 0.035
    SHIP_BASE_Y = 0.04
    ship = None
    ship_coordinates = [(0,0), (0,0), (0,0)]

    game_started = False

    menu_text = StringProperty("G   A   L   A   X   Y")
    menu_button_text = StringProperty("Start")
    score_text = StringProperty("")

    sound_begin = None
    sound_galaxy = None
    sound_game_over_impact = None
    sound_game_over_voice = None
    sound_music1 = None
    sound_restart = None

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)

        self.init_audio()
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_ship()
        self.reset_game()

        if self.is_desktop():
            self.init_keyboard_controls()

        Clock.schedule_interval(self.update, 1/60)
        self.sound_galaxy.play()

    def init_audio(self):
        self.sound_begin = SoundLoader.load("audio/begin.wav")
        self.sound_galaxy = SoundLoader.load("audio/galaxy.wav")
        self.sound_game_over_impact = SoundLoader.load("audio/gameover_impact.wav")
        self.sound_game_over_voice = SoundLoader.load("audio/gameover_voice.wav")
        self.sound_music1 = SoundLoader.load("audio/music1.wav")
        self.sound_restart = SoundLoader.load("audio/restart.wav")

        self.sound_music1.volume = 1
        self.sound_begin.volume = 0.25
        self.sound_galaxy.volume = 0.25
        self.sound_game_over_voice.volume = 0.25
        self.sound_restart.volume = 0.25
        self.sound_game_over_impact.volume = 0.25
    
    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)

            for i in range(0, self.V_NB_LINES):
                self.vertical_lines.append(Line(points=[]))

    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)

            for i in range(0, self.H_NB_LINES):
                self.horizontal_lines.append(Line(points=[]))

    def init_tiles(self):
        with self.canvas:
            Color(1, 1, 1)

            for i in range(0, self.NB_TILES):
                self.tiles.append(Quad())

    def init_ship(self):
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()

    def reset_game(self):
        self.current_offset_y = 0
        self.current_y_loop = 0

        self.current_offset_x = 0
        self.current_speed_x = 0

        self.tiles_coordinates = []
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_cordinates()

        self.score_text = "SCORE: 0"

        self.game_over = False
    
    def is_desktop(self):
        if platform in ("linux", "win", "macosx"):
            return True
        return False 
    
    def init_keyboard_controls(self):
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self.on_keyboard_down)
        self._keyboard.bind(on_key_up=self.on_keyboard_up)

    def get_line_x_from_index(self, index):
        center_x = self.perspective_point_x
        spacing_x = self.V_LINES_SPACING * self.width
        offset = index - 0.5

        line_x = center_x + offset * spacing_x + self.current_offset_x
        return line_x
    
    def get_line_y_from_index(self, index):
        spacing_y = self.H_LINES_SPACING * self.height
        offset = index

        line_y = spacing_y * offset - self.current_offset_y
        return line_y

    def pre_fill_tiles_coordinates(self):
        for i in range(10):
            self.tiles_coordinates.append((0,i))
    
    def generate_tiles_cordinates(self):
        last_x = 0
        last_y = 0
        random_start = -1
        random_end = 1
        border = self.V_NB_LINES/2 - 1

        for i in range(len(self.tiles_coordinates)-1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]
        
        if len(self.tiles_coordinates) > 0:
            last_x, last_y = self.get_last_ti_coordinates()
                
        for i in range(len(self.tiles_coordinates), self.NB_TILES):
            if last_x == border:
                random_end = 0
            else:
                random_end = 1
            if last_x == -border:
                random_start = 0
            else:
                random_start = -1

            r = random.randint(random_start,random_end)
            self.tiles_coordinates.append((last_x, last_y+1))
            if r != 0:
                self.tiles_coordinates.append((last_x+r, last_y+1))
                self.tiles_coordinates.append((last_x+r, last_y+2))
            
            last_x, last_y = self.get_last_ti_coordinates()

    def get_tile_cordinate(self, ti_x, ti_y):
        ti_y -= self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y
    
    def get_last_ti_coordinates(self):
        last_coordinates = self.tiles_coordinates[-1]
        last_x = last_coordinates[0]
        last_y = last_coordinates[1]
        return last_x, last_y
    
    def check_ship_collision_with_tile(self, ti_x, ti_y):
        min_x, min_y = self.get_tile_cordinate(ti_x, ti_y)
        max_x, max_y = self.get_tile_cordinate(ti_x+1, ti_y+1)

        for i in range(0, 3):
            px, py = self.ship_coordinates[i]
            if min_x <= px <= max_x and  min_y <= py <= max_y:
                return True
        return False

    def check_ship_collision(self):
        for i in range(0, len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            if ti_y > self.current_y_loop + 1:
                return False
            if self.check_ship_collision_with_tile(ti_x, ti_y):
                return True
        return False

    def update_vertical_lines(self):
        start_index = -int(self.V_NB_LINES/2)+1
        end_index = start_index + self.V_NB_LINES

        for i in range(start_index, end_index):
            line_x = self.get_line_x_from_index(i)

            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1,y1, x2,y2]

    def update_horizontal_lines(self):
        start_index = -int(self.V_NB_LINES/2) +1
        end_index = start_index + self.V_NB_LINES-1
        
        min_x = self.get_line_x_from_index(start_index)
        max_x = self.get_line_x_from_index(end_index)

        for i in range(0, self.H_NB_LINES):
            line_y = self.get_line_y_from_index(i) 

            x1, y1 = self.transform(min_x, line_y)
            x2, y2 = self.transform(max_x, line_y)
            self.horizontal_lines[i].points = [x1,y1, x2,y2]

    def update_tiles(self):
        
        for i in range(0, self.NB_TILES):
            coordinates = self.tiles_coordinates[i]
            min_x, min_y = self.get_tile_cordinate(coordinates[0], coordinates[1])
            max_x, max_y = self.get_tile_cordinate(coordinates[0]+1, coordinates[1]+1)

            x1, y1 = self.transform(min_x, min_y)
            x2, y2 = self.transform(min_x, max_y)
            x3, y3 = self.transform(max_x, max_y)
            x4, y4 = self.transform(max_x, min_y)

            self.tiles[i].points = [x1,y1, x2,y2, x3,y3, x4,y4]

    def update_ship(self):
        center_x = self.perspective_point_x
        ship_width = self.SHIP_WIDTH*self.width

        ship_height = self.SHIP_HEIGHT * self.height
        ship_base_y = self.SHIP_BASE_Y * self.height

        self.ship_coordinates[0] = (int(center_x - ship_width/2), ship_base_y)
        self.ship_coordinates[1] = (center_x, ship_base_y + ship_height)
        self.ship_coordinates[2] = (int(center_x + ship_width/2), ship_base_y)

        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])

        self.ship.points = [x1,y1, x2,y2, x3,y3]

    def update_graphics(self):
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()
 
    def vertical_move_board(self, time_factor):
        speed_multiplier = 1 + self.current_y_loop / 100
        speed_y = self.SPEED_Y * speed_multiplier * self.height / 100 
        self.current_offset_y += speed_y * time_factor 
    
    def horizontal_move_board(self, time_factor):
        speed_x = self.current_speed_x * self.width /100
        self.current_offset_x +=  speed_x * time_factor

    def increment_y_loop(self, spacing_y):
        self.current_offset_y -= spacing_y
        self.current_y_loop += 1
        self.score_text = "SCORE: " + str(self.current_y_loop)
        self.generate_tiles_cordinates()

    def run_game_over_process(self):
        self.menu_widget.opacity = 1
        self.game_over = True
        self.sound_game_over_impact.play()
        Clock.schedule_once(self.play_game_over_voice_sound, 1)
        self.sound_music1.stop()

    def play_game_over_voice_sound(self, dt):
        if self.game_over:
            self.sound_game_over_voice.play()
        
    def update(self, dt):
        time_factor = dt*60
        
        self.update_graphics()

        if self.game_started and not self.game_over:
            if self.sound_music1.state == "stop":
                self.sound_music1.play()
            
            self.vertical_move_board(time_factor)
            self.horizontal_move_board(time_factor)

            spacing_y = self.H_LINES_SPACING * self.height
            while self.current_offset_y >= spacing_y:
                self.increment_y_loop(spacing_y)

        if not self.game_over and not self.check_ship_collision():
            self.run_game_over_process()

    def on_menu_button_pressed(self):
        if not self.game_started:
            self.game_started = True
            self.menu_text = "G  A  M  E   O  V  E  R"
            self.menu_button_text = "Try Again?"
            self.sound_begin.play()
        else:
            self.reset_game()
            self.sound_restart.play()

        self.sound_music1.play()
        self.menu_widget.opacity = 0

class GalaxyApp(App):
    pass

GalaxyApp().run()