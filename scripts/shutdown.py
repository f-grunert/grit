#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN)

while True:
 GPIO.wait_for_edge(11, GPIO.RISING)
 subprocess.Popen('lxde-pi-shutdown-helper')
 time.sleep(2)