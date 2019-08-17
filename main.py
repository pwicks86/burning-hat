import board
import random
import neopixel
import time
from touchio import TouchIn
from math import floor
from digitalio import DigitalInOut, Direction, Pull


numpix = 54
strip = neopixel.NeoPixel(board.D1, numpix, brightness=1, auto_write=False)

blue = (0,0,5)
green = (0,5,0)
red = (5,0,0)
white = (5,5,5)
black = (0,0,0)

def set_all(c):
    for i in range(numpix):
        strip[i] = c

def clear():
    set_all((0,0,0))

def rand_color():
    return tuple(sorted((0, 0xFF, random.randrange(0,5)), key = lambda x: random.random()))

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
        strip.write()
        self.cycle_num += 1

# Random every time
class RandomJunk():
    def run(self):
        for i in range(numpix):
            strip[i] = rand_color()
        strip.write()

# Single pixels fall to the end and stack
class Falling():
    def __init__(self):
        clear()
        self.led_pos = 0
        self.end = numpix
        self.color = rand_color()

    def run(self):
        if (self.led_pos >= self.end):
            self.led_pos = 0
            self.end -= 1
        strip[self.led_pos] = self.color
        strip.write()
        if self.led_pos < self.end - 1:
            strip[self.led_pos] = (0,0,0)
        self.led_pos += 1
        if self.end == 0:
            self.led_pos = 0
            self.end = numpix
            self.color = rand_color()

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
            self.color = rand_color()

        strip.write()

class Sparkle():
    def __init__(self):
        clear()
        self.clear_list = []
    def run(self):
        for i in self.clear_list:
            strip[i] = black
        self.clear_list.clear()
        for i in range(numpix/3):
            idx = random.randrange(0,numpix - 1)
            strip[idx] = white
            self.clear_list.append(idx)
        strip.write()

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
        strip.write()
        self.fades = list(filter(lambda f: f[1][2] > 0, self.fades))

class RWTwinkle():
    def __init__(self):
        clear()
        self.offset = 0
    def run(self):
        self.offset += 1
        for i in range(numpix):
            strip[(i + self.offset) % numpix] = red if i % 2 == 0 else white
        strip.write()

class RWMarch():
    def __init__(self):
        clear()
        self.offset = 0
    def run(self):
        self.offset += 1
        for i in range(numpix):
            strip[(i + self.offset) % numpix] = red if i % 4 <=1 else white
        strip.write()

modes = [RWMarch, RWTwinkle, BWFade, Sparkle, FunFill, Falling, RandomJunk, ColorFlash]
num_modes = len(modes)
mode_index = 0
active_mode = modes[mode_index]()

print(board)
button = DigitalInOut(board.D0)
button.direction = Direction.INPUT
button.pull = Pull.DOWN
last_button = button.value

while True:
    if (button.value and button.value != last_button):
        print("changing")
        mode_index = (mode_index + 1) % num_modes
        active_mode = modes[mode_index]()
    last_button = button.value
    active_mode.run()