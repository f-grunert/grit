#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import requests

# Check Internet-Verbindung
RequestCheck = requests.get('http://schueler:zabelhaft@fgrunert.tk/schule/check.php')
if RequestCheck.text == 'ok':
 Webconnection = True
else:
 Webconnection = False

LocalIP = subprocess.check_output('hostname -I', shell=True)
if Webconnection == True:
 PublicIP = subprocess.check_output('curl ifconfig.me', shell=True)
 text = 'Das System wird gestartet. Die lokale IP lautet: ' + LocalIP + '; ich wiederhole: Die lokale IP lautet: ' + LocalIP + '; die öffentliche IP lautet: ' + PublicIP
else:
 text = 'Das System wird gestartet. Die lokale IP lautet: ' + LocalIP + '; ich wiederhole: Die lokale IP lautet: ' + LocalIP + '; das Gerät ist nicht mit dem Internet verbunden und wird nicht öffentlich auffindbar sein.'
subprocess.call('aplay /home/pi/Documents/Scripts/notify.wav && pico2wave --lang de-DE --wave /tmp/audio.wav "' + text + '" && aplay /tmp/audio.wav && rm /tmp/audio.wav', shell=True)
