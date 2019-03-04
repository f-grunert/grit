#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Tkinter as tk
from thread import start_new_thread
import subprocess
import os
import time
import threading
import requests
import RPi.GPIO as GPIO
import time

root = tk.Tk()
root.attributes("-fullscreen", True)

StopBlinkButtonQuestion = True
StopBlinkButtonService = True
NumberServices = 0
Questions = []
Services = []
Preview = True
pins_out = [16,15,33]

GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)

for pin in pins_out:
 GPIO.setup(pin, GPIO.OUT)

GPIO.output(15, GPIO.HIGH)

tempfiles = ['stream.tmp', 'lock.tmp', 'interaction.log']

for tempfile in tempfiles:
 if os.path.exists('/var/www/html/interaction/' + tempfile) == True:
  os.unlink('/var/www/html/interaction/' + tempfile)

os.mknod('/var/www/html/interaction/interaction.log')

# Check Internet-Verbindung
RequestCheck = requests.get('http://schueler:zabelhaft@fgrunert.tk/schule/check.php')
if RequestCheck.text == 'ok':
 Webconnection = True
else:
 Webconnection = False

# Zeige Live-Bild-Vorschau
def ImageUpdate():
 global Preview
 while Preview == True:
  subprocess.call('raspistill --nopreview --width 480 --height 360 -o /home/pi/Documents/Scripts/capture.gif -e gif -t 1', shell=True)
  img2 = tk.PhotoImage(file="/home/pi/Documents/Scripts/capture.gif")
  LabelImage.config(image=img2)
  LabelImage.image = img2
  time.sleep(0.75)

threading.Thread(target=ImageUpdate).start()

# Blinken des dazugehörigen Buttons bei neuen Fragen
def BlinkButtonQuestion():
 global StopBlinkButtonQuestion
 if StopBlinkButtonQuestion != False:
  StopBlinkButtonQuestion = False
  while StopBlinkButtonQuestion == False:
   ButtonQuestion.config(bg='red', activebackground='red')
   ButtonQuestion.update()
   time.sleep(0.5)
   ButtonQuestion.config(bg=StandardColor, activebackground=StandardColorActive)
   ButtonQuestion.update()
   time.sleep(0.5)

# Blinken des dazugehörigen Buttons bei neuen Serviceanfragen
def BlinkButtonService():
 global StopBlinkButtonService
 if StopBlinkButtonService != False:
  StopBlinkButtonService = False
  while StopBlinkButtonService == False:
   ButtonService.config(bg='gold', activebackground='gold')
   ButtonService.update()
   time.sleep(0.5)
   ButtonService.config(bg=StandardColor, activebackground=StandardColorActive)
   ButtonService.update()
   time.sleep(0.5)

# Frage anzeigen
def ShowQuestion():
 global Questions, StopBlinkButtonQuestion
 if len(Questions) != 0:
  question = Questions.pop(0)
  LabelNews.config(text=question[0])
  LabelNews.update()
  subprocess.call('aplay ~/Documents/Scripts/notify.wav && pico2wave --lang de-DE --wave /tmp/audio.wav "' + question[1] + '"; aplay /tmp/audio.wav; rm /tmp/audio.wav', shell=True)
  if len(Questions) == 0:
   StopBlinkButtonQuestion = True
  ButtonQuestion.config(text='Fragen (' + str(len(Questions)) + ')')
  ButtonQuestion.update()

# Serviceanfrage anzeigen
def ShowService():
 global Services, StopBlinkButtonService
 if len(Services) != 0:
  service = Services.pop(0)
  LabelNews.config(text=service[0])
  LabelNews.update()
  subprocess.call('aplay ~/Documents/Scripts/notify.wav && pico2wave --lang de-DE --wave /tmp/audio.wav "' + service[1] + '"; aplay /tmp/audio.wav; rm /tmp/audio.wav', shell=True)
  if len(Services) == 0:
   StopBlinkButtonService = True
  ButtonService.config(text='Serviceanfragen (' + str(len(Services)) + ')')
  ButtonService.update()


# Regelmäßiges Überprüfen auf Änderungen im LOG, als thread parallel aufgerufen
def CheckLog():
 global Questions, Services
 FileLog = open('/var/www/html/interaction/interaction.log', 'r')
 ContentFileLog = FileLog.readlines()[-1]
 FileLog.close()
 while os.path.exists('/var/www/html/interaction/stream.tmp'):
  if os.path.exists('/var/www/html/interaction/lock.tmp') != True:
   os.mknod('/var/www/html/interaction/lock.tmp')
   FileLog = open('/var/www/html/interaction/interaction.log', 'r')
   NewContentFileLog = FileLog.readlines()[-1]
   FileLog.close()
   if NewContentFileLog != ContentFileLog:
    if NewContentFileLog.split(':')[0] == 'server':
     ContentFileLog = NewContentFileLog
    else:
     name = NewContentFileLog.split(':')[2]
     name = name.split(']')[0]
     operator = NewContentFileLog.split(':')[1]
     content = NewContentFileLog.split("\t")[1]
     if operator == 'question':
      operator = ' hat folgende Frage '
      Questions.append([name + ' > ' + content, name + operator + content])
      ButtonQuestion.config(text='Fragen (' + str(len(Questions)) + ')', command=ShowQuestion)
      threading.Thread(target=BlinkButtonQuestion).start()
     elif operator == 'service':
      operator = ' bittet um eine '
      Services.append([name + ' > ' + content, name + operator + content])
      ButtonService.config(text='Fragen (' + str(len(Services)) + ')', command=ShowService)
      threading.Thread(target=BlinkButtonService).start()
     FileLog = open('/var/www/html/interaction/interaction.log', 'a')
     FileLog.write("\n[server]\tdone")
     FileLog.close()
     ContentFileLog = "[server]\tdone"
   os.remove('/var/www/html/interaction/lock.tmp')
  time.sleep(0.5)

def DisableButtons():
 ButtonStream.config(state='disabled')
 ButtonStream.update()
 ButtonQuit.config(state='disabled')
 ButtonQuit.update()
 ButtonQuestion.config(state='disabled')
 ButtonQuestion.update()
 ButtonService.config(state='disabled')
 ButtonService.update()

def EnableButtons():
 ButtonStream.config(state='normal')
 ButtonQuit.config(state='normal')
 ButtonQuestion.config(state='normal')
 ButtonService.config(state='normal')

def TellWeb(status):
 if Webconnection == True:
  if status == True:
   LocalIP = subprocess.check_output('curl ifconfig.me', shell=True)
   requests.get('https://schueler:zabelhaft@fgrunert.tk/schule/index.php?sendip=' + LocalIP)
  else:
   requests.get('https://schueler:zabelhaft@fgrunert.tk/schule/index.php?sendip=null')

def StartStream():
 DisableButtons()
 TellWeb(True)
 os.mknod('/var/www/html/interaction/stream.tmp')
 threading.Thread(target=CheckLog).start()
 subprocess.Popen('sudo /home/pi/picam/picam -o /run/shm/hls - --channels 1 -w 1280 -h 720 --audiobitrate 40000 --videobitrate 1800000 --vfr --avclevel 3.1 --autoex --alsadev hw:1,0', shell=True)
 ButtonStream.config(text="Stream beenden")
 ButtonStream.config(command=StopStream)
 LabelStatus.config(text="Stream aktiv")
 LabelStatus.config(fg="green")
 subprocess.call('aplay ~/Documents/Scripts/notify.wav && pico2wave --lang de-DE --wave /tmp/audio.wav "Stream gestartet"; aplay /tmp/audio.wav; rm /tmp/audio.wav', shell=True)
 EnableButtons()
 GPIO.output(33, GPIO.HIGH)

def StopStream():
 global StopBlinkButtonQuestion, StopBlinkButtonService
 DisableButtons()
 TellWeb(False)
 StopBlinkButtonQuestion = True
 StopBlinkButtonService = True
 os.remove('/var/www/html/interaction/stream.tmp')
 proc_picam = subprocess.check_output('ps -A | grep picam', shell=True)
 proc_picam = proc_picam.split(' ')[1]
 subprocess.Popen('sudo kill ' + proc_picam, shell=True)
 ButtonStream.config(text="Stream starten")
 ButtonStream.config(command=StartStream) 
 LabelStatus.config(text="Stream inaktiv")
 LabelStatus.config(fg="red")
 subprocess.call('aplay ~/Documents/Scripts/notify.wav && pico2wave --lang de-DE --wave /tmp/audio.wav "Stream beendet"; aplay /tmp/audio.wav; rm /tmp/audio.wav', shell=True)
 EnableButtons()
 GPIO.output(33, GPIO.LOW)

def QuitSystem():
 global Preview
 DisableButtons()
 Preview = False
 subprocess.call('aplay ~/Documents/Scripts/notify.wav && pico2wave --lang de-DE --wave /tmp/audio.wav "System wird beendet"; aplay /tmp/audio.wav; rm /tmp/audio.wav', shell=True)
 GPIO.output(16, GPIO.LOW)
 GPIO.output(33, GPIO.LOW)
 print "GPIOs done"
 if os.path.exists('/var/www/html/interaction/stream.tmp'):
  StopStream()
  root.quit()
 else:
  root.quit()

#def SetBalance():

# Labels
if Webconnection == True:
 LabelSystem = tk.Label(root, font=("TkDefaultFont", 25), fg="green", text="System läuft fehlerfrei")
else:
 LabelSystem = tk.Label(root, font=("TkDefaultFont", 25), fg="gold", text="keine Webverbindung")
 GPIO.output(16, GPIO.HIGH)
LabelSystem.place(x=370, y=415)
LabelStatus = tk.Label(root, font=("TkDefaultFont", 25), fg="red", text="Stream inaktiv")
LabelStatus.place(x=770, y=415)
LabelHeadingNews = tk.Label(root, font=("TkDefaultFont", 35), text="Interaktionen:")
LabelHeadingNews.place(x=12, y=400)
LabelNews = tk.Label(root, font=("TkDefaultFont", 25, "italic"), wraplength=1000, justify='left', text="-")
LabelNews.place(x=12, y=465)

# Bild
ImageCapture = tk.PhotoImage(file="/home/pi/Documents/Scripts/capture.gif")
LabelImage = tk.Label(root, image=ImageCapture)
LabelImage.place(x=12, y=12)

# Buttons
ButtonStream = tk.Button(root, font=("TkDefaultFont", 35), width=16, text='Stream starten', command=StartStream)
ButtonStream.place(x=502, y=12)
ButtonQuit = tk.Button(root, font=("TkDefaultFont", 35), width=16, text='Schließen', command=QuitSystem)
ButtonQuit.place(x=502, y=92)
ButtonQuestion = tk.Button(root, font=("TkDefaultFont", 35), width=16, text='Fragen (' + str(len(Questions)) + ')', command=ShowQuestion)
ButtonQuestion.place(x=502, y=172)
ButtonService = tk.Button(root, font=("TkDefaultFont", 35), width=16, text='Serviceanfragen (' + str(len(Services)) + ')', command=ShowService)
ButtonService.place(x=502, y=262)

StandardColor = ButtonStream.cget('bg')
StandardColorActive = ButtonStream.cget('activebackground')

root.mainloop()
