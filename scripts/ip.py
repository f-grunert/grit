#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import requests

# Check Internet-Verbindung
try:
 RequestCheck = requests.get('http://schueler:zabelhaft@fgrunert.lima-city.de/schule/check.php')
 if RequestCheck.text == 'ok':
  Webconnection = True
 else:
  Webconnection = False
except:
 Webconnection = False

LocalIP = subprocess.check_output('hostname -I', shell=True)
LocalIP = LocalIP.replace(".", " Punkt ")
if LocalIP == "\n":
 LocalIP = "wegen Nichtverbindung zum Netzwerk unbekannt"

if Webconnection == True:
 PublicIP = subprocess.check_output('curl ifconfig.me', shell=True)
 text = 'Das System wird gestartet. Die lokale IP ist: ' + LocalIP + '; die öffentliche IP ist: ' + PublicIP
else:
 text = 'Das System wird gestartet. Die lokale IP ist: ' + LocalIP + '; das Gerät ist nicht mit dem Internet verbunden und wird nicht öffentlich auffindbar sein.'
subprocess.call('aplay /home/pi/Documents/Scripts/message_start.wav && pico2wave --lang de-DE --wave /tmp/audio.wav "' + text + '" && aplay /tmp/audio.wav && rm /tmp/audio.wav', shell=True)
