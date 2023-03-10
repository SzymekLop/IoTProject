#!/usr/bin/env python3
# developed by Filip Strózik 2023

import time
from datetime import datetime, timedelta
import neopixel
import board
import busio
import w1thermsensor
import adafruit_bme280.advanced as adafruit_bme280
from mfrc522 import MFRC522
from config import *
import RPi.GPIO as GPIO
import lib.oled.SSD1331 as SSD1331
from PIL import Image, ImageDraw, ImageFont

ARIAL = ImageFont.truetype('fonts/arial.ttf',13)


def formated_print(mytime):
    return f'{mytime.hour}:{mytime.minute}:{mytime.second},{mytime.microsecond}'


class RFID:
    def __init__(self):
        self.MIFAREReader = MFRC522()
        self.initial_time = datetime.now() - timedelta(seconds=5)
        self.is_being_read = False

    def read(self):
        (status, TagType) = self.MIFAREReader.MFRC522_Request(self.MIFAREReader.PICC_REQIDL)
        if status == self.MIFAREReader.MI_OK:
            (status, uid) = self.MIFAREReader.MFRC522_Anticoll()
            if status == self.MIFAREReader.MI_OK:
                curr_time = datetime.now()
                if self.initial_time + timedelta(seconds=5) < curr_time and not self.is_being_read:
                    self.is_being_read = True
                    self.initial_time = curr_time
                    num = 0
                    for i in range(0, len(uid)):
                        num += uid[i] << (i * 8)
                    return num
                else:  # this is after sth called nesting
                    self.is_being_read = False
                    return None
        else:
            self.is_being_read = False
        return None

    def print_read_rfid(self):
        print(f'card readed: {self.is_being_read} Last read time: {formated_print(self.initial_time)}')


# clas from lab9
class Color:
    white = (255, 255, 255)
    black = (0, 0, 0)
    red = (255, 0, 0)
    green = (0, 255, 0)


class LedController:
    def __init__(self):
        self.pixels = neopixel.NeoPixel(board.D18, 8, brightness=1.0 / 32, auto_write=False)
        self.animation_speed = 0.2

    def animate_read(self):
        for i in range(0, 3):
            self.pixels.fill(Color.black)
            self.pixels.show()
            time.sleep(self.animation_speed)

            self.pixels.fill(Color.green)
            self.pixels.show()
            time.sleep(self.animation_speed)


class Oled:
    def __init__(self):
        self.display = SSD1331.SSD1331()
        self.display.Init()
        self.display.clear()
        self.background = Image.new("RGB", (self.display.width, self.display.height), "GREEN")
        self.printer = ImageDraw.Draw(self.background)

    def show(self):
        self.display.ShowImage(self.background, 0, 0)

    def clear(self):
        self.display.clear()

    def reset(self):
        self.display.reset()

    def get_width(self):
        return self.display.width

    def get_height(self):
        return self.display.height

    def print_text(self, coordinates, text, color="WHITE", font=ARIAL):  # color="WHITE"
        print(text)
        self.printer.text(coordinates, text, fill=color, font=font)

    def clear_xy(self, coordinates):
        self.printer.rectangle(coordinates, fill="GREEN")

    def place_image(self, path, x, y):
        image = Image.open(path)
        # image = image.resize((16, 16))
        self.background.paste(image, (x, y))
        # probably below wont work but try it
        # self.display.ShowImage(self.background, 0, 0)


class MainController:
    def __init__(self):
        self.rfid = RFID()
        self.led = LedController()
        self.buzzer = None
        self.oled = Oled()
        self.time_period = timedelta(seconds=2)

    def run(self):
        read_val = self.rfid.read()

        if read_val is not None:
            self.oled.clear_xy(((0,0),(128,128)))
            self.rfid.print_read_rfid()
            self.oled.print_text((4, 20), str(read_val))
            self.oled.show()
            GPIO.output(buzzerPin, False)
            self.led.animate_read()

        if self.rfid.initial_time + self.time_period < datetime.now():
            GPIO.output(buzzerPin, True)
            # self.oled.clear()

        if not self.rfid.is_being_read:
            self.led.pixels.fill(Color.black)
            self.led.pixels.show()
        return read_val
