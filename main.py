# ////////////////////////////////////////////////////////////////
# //                     IMPORT STATEMENTS                      //
# ////////////////////////////////////////////////////////////////

import math
import sys
import time

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import *
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.animation import Animation
from functools import partial
from kivy.config import Config
from kivy.core.window import Window
from pidev.kivy import DPEAButton
from pidev.kivy import PauseScreen
from time import sleep
import RPi.GPIO as GPIO 
from pidev.stepper import stepper
from pidev.Cyprus_Commands import Cyprus_Commands_RPi as cyprus
from threading import Thread



# ////////////////////////////////////////////////////////////////
# //                      GLOBAL VARIABLES                      //
# //                         CONSTANTS                          //
# ////////////////////////////////////////////////////////////////
START = True
STOP = False
UP = False
DOWN = True
ON = True
OFF = False
YELLOW = .180, 0.188, 0.980, 1
BLUE = 0.917, 0.796, 0.380, 1
CLOCKWISE = 0
COUNTERCLOCKWISE = 1
ARM_SLEEP = 2.5
DEBOUNCE = 0.10

lowerTowerPosition = 60
upperTowerPosition = 76


# ////////////////////////////////////////////////////////////////
# //            DECLARE APP CLASS AND SCREENMANAGER             //
# //                     LOAD KIVY FILE                         //
# ////////////////////////////////////////////////////////////////
class MyApp(App):

    def build(self):
        self.title = "Robotic Arm"
        return sm

Builder.load_file('main.kv')
Window.clearcolor = (.1, .1,.1, 1) # (WHITE)

cyprus.open_spi()

# ////////////////////////////////////////////////////////////////
# //                    SLUSH/HARDWARE SETUP                    //
# ////////////////////////////////////////////////////////////////

sm = ScreenManager()
s0 = stepper(port=0, micro_steps=32, hold_current=20, run_current=20, accel_current=20, deaccel_current=20,
             steps_per_unit=200, speed=1)

# ////////////////////////////////////////////////////////////////
# //                       MAIN FUNCTIONS                       //
# //             SHOULD INTERACT DIRECTLY WITH HARDWARE         //
# ////////////////////////////////////////////////////////////////
	
class MainScreen(Screen):
    version = cyprus.read_firmware_version()
    armPosition = 0
    lastClick = time.clock()
    sus = False
    imposter = False

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.initialize()

    def debounce(self):
        processInput = False
        currentTime = time.clock()
        if ((currentTime - self.lastClick) > DEBOUNCE):
            processInput = True
        self.lastClick = currentTime
        return processInput

    def toggleArm(self):
        if self.sus == False:
            cyprus.set_pwm_values(1, period_value=100000, compare_value=100000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            self.sus = True
        else:
            cyprus.set_pwm_values(1, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            self.sus = False
        print("Process arm movement here")


    def toggleMagnet(self):
        if self.imposter == False:
            cyprus.set_servo_position(2, 1)
            self.imposter = True
        else:
            cyprus.set_servo_position(2, .5)
            self.imposter = False
        print("Process magnet here")

    def auto(self):
        self.auto_button.disabled = True
        self.armControl.disabled = True
        self.magnetControl.disabled = True
        self.moveArm.disabled = True
        if self.isBallOnTallTower():
            s0.go_until_press(1, 6400)
            cyprus.set_pwm_values(1, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            while s0.isBusy():
                sleep(1)
            s0.set_speed(.8)
            s0.start_relative_move(-.5)
            while s0.isBusy():
                sleep(1)
            cyprus.set_pwm_values(1, period_value=100000, compare_value=100000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            sleep(.5)
            cyprus.set_servo_position(2, 1)
            sleep(.5)
            cyprus.set_pwm_values(1, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            sleep(1)
            s0.set_speed(.8)
            s0.start_relative_move(-.32)
            while s0.isBusy():
                sleep(1)
            cyprus.set_pwm_values(1, period_value=100000, compare_value=100000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            sleep(1)
            cyprus.set_servo_position(2, .5)
            sleep(.5)
            cyprus.set_pwm_values(1, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            sleep(.5)
            s0.go_until_press(1, 6400)
            self.auto_button.disabled = False
            self.armControl.disabled = False
            self.magnetControl.disabled = False
            self.moveArm.disabled = False
        else:
            s0.go_until_press(1, 6400)
            cyprus.set_pwm_values(1, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            while s0.isBusy():
                sleep(1)
            s0.set_speed(.8)
            s0.start_relative_move(-.8)
            while s0.isBusy():
                sleep(1)
            cyprus.set_pwm_values(1, period_value=100000, compare_value=100000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            sleep(.5)
            cyprus.set_servo_position(2, 1)
            sleep(.5)
            cyprus.set_pwm_values(1, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            sleep(1)
            s0.set_speed(.8)
            s0.start_relative_move(.3)
            while s0.isBusy():
                sleep(1)
            cyprus.set_pwm_values(1, period_value=100000, compare_value=100000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            sleep(1)
            cyprus.set_servo_position(2, .5)
            sleep(1)
            cyprus.set_pwm_values(1, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            sleep(.5)
            s0.go_until_press(1, 6400)
            self.auto_button.disabled = False
            self.armControl.disabled = False
            self.magnetControl.disabled = False
            self.moveArm.disabled = False

        print("Run the arm automatically here")

    def auto_thread(self):
        Thread(target=self.auto, daemon=True).start()

    def setArmPosition(self, position):
        s0.go_to_position(-position)
        print("Move arm here")

    def homeArm(self):
        arm.home(self.homeDirection)

    def isBallOnTallTower(self):
        if (cyprus.read_gpio() & 0b0001):
            sleep(.1)
            if (cyprus.read_gpio() & 0b0001):
                return False
        else:
            return True
        print("Determine if ball is on the top tower")

    def isBallOnShortTower(self):
        if (cyprus.read_gpio() & 0b0010):
            sleep(.1)
            if (cyprus.read_gpio() & 0b0010):
                return False
        else:
            return True
        print("Determine if ball is on the bottom tower")

    def initialize(self):
        cyprus.initialize()
        cyprus.setup_servo(2)
        cyprus.set_servo_position(2, 0.5)
        s0.go_until_press(1, 6400)
        cyprus.set_pwm_values(1, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
        print("Home arm and turn off magnet")

    def resetColors(self):
        self.ids.armControl.color = YELLOW
        self.ids.magnetControl.color = YELLOW
        self.ids.auto.color = BLUE

    def quit(self):
        MyApp().stop()


sm.add_widget(MainScreen(name='main'))

# ////////////////////////////////////////////////////////////////
# //                          RUN APP                           //
# ////////////////////////////////////////////////////////////////

MyApp().run()
cyprus.close_spi()

# makes arm go down all the way- cyprus.set_pwm_values(1, period_value=100000, compare_value=100000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
# Makes arm go up all the way- cyprus.set_pwm_values(1, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
