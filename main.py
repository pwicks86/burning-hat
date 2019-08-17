import board
import random
import neopixel
import time
from math import floor
from digitalio import DigitalInOut, Direction, Pull

numpix = 54
strip = neopixel.NeoPixel(board.D1, numpix, brightness=1, auto_write=False)

blue = (0,0,5)
red = (5,0,0)
white = (5,5,5)
black = (0,0,0)

def set_all(c):
    for i in range(numpix):
        strip[i] = c

def clear():
    set_all((0,0,0))

def rand_color():
    return tuple(sorted((0, 64, random.randrange(0,5)), key = lambda x: random.random()))

def rand_led():
    return random.randrange(0, numpix)

# Flash and fade
class ColorFlash():
    def __init__(self):
        self.cycles_to_black = 30
        self.cycle_num = 30
        self.color = None
    def run(self):
        if (self.cycle_num >= self.cycles_to_black):
            self.color = rand_color()
            self.cycle_num = 0
        mult = (self.cycles_to_black - self.cycle_num) / self.cycles_to_black
        set_all(tuple([int(mult * x) for x in self.color]))
        self.cycle_num += 1

# Random every time
class RandomJunk():
    def run(self):
        for i in range(numpix):
            strip[i] = rand_color()

# similar to Falling
class FunFill():
    def __init__(self):
        clear()
        self.i = 0
        self.color = rand_color()

    def run(self):
        strip[self.i] = self.color
        self.i += 1
        if (self.i >= numpix):
            self.i = 0
            clear()
            self.color = rand_color()

class Sparkle():
    def __init__(self):
        clear()
        self.clear_list = []
    def run(self):
        for i in self.clear_list:
            strip[i] = black
        self.clear_list.clear()
        for i in range(numpix/3):
            idx = rand_led()
            strip[idx] = white
            self.clear_list.append(idx)

class BWFade():
    def __init__(self):
        clear()
        self.fades = []
    def run(self):
        while len(self.fades) < 20:
            l = rand_led()
            skip = False
            for f in self.fades:
                if l == f[0]:
                    skip = True
            if skip:
                continue
            self.fades.append([l, random.choice([white, blue]),random.randrange(5, 20)])
        for f in self.fades:
            strip[f[0]] = f[1]
            f[1] = (max(f[1][0] - f[2], 0), max(f[1][1] - f[2], 0), max(f[1][2] - f[2], 0))
        self.fades = list(filter(lambda f: f[1][2] > 0, self.fades))

class RWTwinkle():
    def __init__(self):
        clear()
        self.offset = 0
    def run(self):
        self.offset += 1
        for i in range(numpix):
            strip[(i + self.offset) % numpix] = red if i % 2 == 0 else white

class RWMarch():
    def __init__(self):
        clear()
        self.offset = 0
    def run(self):
        self.offset += 1
        for i in range(numpix):
            strip[(i + self.offset) % numpix] = red if i % 4 <=1 else white

class WhiteHead():
    def __init__(self, level):
        clear()
        self.c = (level,level,level)
    def run(self):
        for i in range(12, 43):
            strip[i] = self.c

class RedHead():
    def __init__(self):
        clear()
    def run(self):
        blue = [13, 17, 21, 25, 29, 33, 37, 41]
        for i in blue:
            strip[i] = (0,255,0)

HiLamp = lambda: WhiteHead(255)
MedLamp = lambda: WhiteHead(64)
LowLamp = lambda: WhiteHead(16)
modes = [RWMarch, RWTwinkle, BWFade, Sparkle, FunFill, RandomJunk, ColorFlash, HiLamp, MedLamp, LowLamp, RedHead]

num_modes = len(modes)
mode_index = 0
active_mode = modes[mode_index]()

button = DigitalInOut(board.D0)
button.direction = Direction.INPUT
button.pull = Pull.DOWN
button_valid = True

while True:
    active_mode.run()
    strip.write()
    sleep_time = 0
    while sleep_time < .1:
        time.sleep(.01)
        sleep_time += .01
        if (button.value and button_valid):
            button_valid = False
            print("changing")
            mode_index = (mode_index + 1) % num_modes
            active_mode = modes[mode_index]()
            print(mode_index)
        if (not button.value and not button_valid):
            button_valid = True
