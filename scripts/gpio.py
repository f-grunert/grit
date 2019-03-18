#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import RPi.GPIO as GPIO

GPIO.cleanup()

GPIO.setmode(GPIO.BOARD)

pins_out = [16,15,33]

for pin in pins_out:
 GPIO.setup(pin, GPIO.OUT)

for pin in pins_out:
 GPIO.output(pin, GPIO.HIGH)
 time.sleep(0.2)

time.sleep(0.5)

for pin in pins_out:
 GPIO.output(pin, GPIO.LOW)
 time.sleep(0.2)

time.sleep(0.5)

GPIO.output(15, GPIO.HIGH)