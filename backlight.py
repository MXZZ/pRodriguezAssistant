# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# project: pRodriguezAssistant

import board
import neopixel
import sys
import getopt
import time
import random

eyes_pin = board.D21
teeth_pin = board.D18

eyes_num = 1 # two eyes in parallel
teeth_num = 18

ORDER = neopixel.GRB

default_color = (243, 253, 0)
no_color = (0, 0, 0)

def switch_pixels(pixels, on, color):
    if on:
        pixels.fill(color)
    else:
        pixels.fill((0, 0, 0))
    pixels.show()

def music(pixels, num):
    while True:
        for i in range(num):
            r = random.randrange(255)
            g = random.randrange(255)
            b = random.randrange(255)
            pixels[i] = (r, g, b)
        pixels.show()
        time.sleep(0.1)

def talk(pixels, num):
    talk_phase_0 = {2: default_color, 3: default_color, 6: default_color, 7: default_color, 8: default_color,
                    9: default_color, 10: default_color, 11: default_color, 13: no_color, 14: no_color, 15: no_color,
                    16: no_color}

    talk_phase_1 = {2: no_color, 3: no_color, 6: no_color, 7: default_color, 8: default_color, 9: default_color,
                    10: default_color, 11: no_color, 13: default_color, 14: default_color, 15: default_color,
                    16: default_color}

    while True:
        for key in talk_phase_0.keys():
            pixels[key] = talk_phase_0[key]
        pixels.show()
        time.sleep(0.25)

        for key in talk_phase_1.keys():
            pixels[key] = talk_phase_1[key]
        pixels.show()
        time.sleep(0.25)

def main(argv):
    #print ('Argument List:', str(sys.argv))
    pixels = None
    on = False
    music_on = False
    talk_on = False
    red = 243
    green = 253
    blue = 0
    if len(argv) < 2:
        print ('backlight.py -l <eyes|teeth> -s <on|off|music|talk> -r <val> -g <val> -b <val>')
    try:
        opts, args = getopt.getopt(argv, "hl:s:r:g:b:", ["light=", "switch=", "red=", "green=", "blue="])
    except getopt.GetoptError:
        print ('backlight.py -l <eyes|teeth> -s <on|off> -r <val> -g <val> -b <val>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('backlight.py -l <eyes|teeth> -s <on|off> -r <val> -g <val> -b <val>')
            sys.exit()
        elif opt in ("-l", "--light"):
            if (arg == 'eyes'):
                pixels = neopixel.NeoPixel(eyes_pin, eyes_num, brightness=1, auto_write=False,
                                pixel_order=ORDER)
                num = eyes_num
            elif (arg == 'teeth'):
                pixels = neopixel.NeoPixel(teeth_pin, teeth_num, brightness=0.5, auto_write=False,
                                     pixel_order=ORDER)
                num = teeth_num
        elif opt in ("-s", "--switch"):
            if (arg == 'on'):
                on = True
            elif (arg == 'music'):
                music_on = True
            elif (arg == 'talk'):
                talk_on = True
        elif opt in ("-r", "--red"):
            red = int(arg)
        elif opt in ("-g", "--green"):
            green = int(arg)
        elif opt in ("-b", "--blue"):
            blue = int(arg)

    if (pixels):
        switch_pixels(pixels, on, (red, green, blue))

    if (music_on):
        music(pixels, num)

    if (talk_on):
        talk(pixels, num)

if __name__ == "__main__":
   main(sys.argv[1:])