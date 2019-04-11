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

GPIO.setmode(GPIO.BOARD)

for pin in pins_out:
 GPIO.setup(pin, GPIO.OUT)

GPIO.output(15, GPIO.HIGH)

tempfiles = ['stream.tmp', 'lock.tmp', "usblink"]

for tempfile in tempfiles:
 if os.path.exists('/var/www/html/interaction/' + tempfile) == True:
  os.unlink('/var/www/html/interaction/' + tempfile)

# Check Internet-Verbindung
RequestCheck = requests.get('http://schueler:zabelhaft@fgrunert.lima-city.de/schule/check.php')
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

# Deaktivierung Einstellungsmenü
def AbortSettings():
 global settings
 settings.destroy()

# Speichern Einstellungen
def SaveSettings():
 print "null"

# Aktivierung Einstellungsmenü
def ShowSettings():
 global settings
 settings = tk.Tk()
 settings.attributes("-fullscreen", True)
 
 # Label
 LabelSettings = tk.Label(settings, font=("TkDefaultFont", 45, "bold"), text="Einstellungen")
 LabelSettings.place(x=12, y=12)
 LabelSettingsRecording = tk.Label(settings, font=("TkDefaultFont", 25), text="Aufzeichnung speichern?")
 LabelSettingsRecording.place(x=12, y=100)
 LabelSettingsRecordingDefault = tk.Label(settings, font=("TkDefaultFont", 15, 'italic'), text="default: nein")
 LabelSettingsRecordingDefault.place(x=12, y=145)
 LabelSettingsVideobit = tk.Label(settings, font=("TkDefaultFont", 25), text="Videobitrate in MBit/s")
 LabelSettingsVideobit.place(x=12, y=200)
 LabelSettingsVideobitDefault = tk.Label(settings, font=("TkDefaultFont", 15, 'italic'), text="default: 1,8 MBit/s")
 LabelSettingsVideobitDefault.place(x=12, y=245)
 LabelSettingsAudiobit = tk.Label(settings, font=("TkDefaultFont", 25), text="Audiobitrate in MBit/s")
 LabelSettingsAudiobit.place(x=12, y=300)
 LabelSettingsAudiobitDefault = tk.Label(settings, font=("TkDefaultFont", 15, 'italic'), text="default: 0,4 MBit/s")
 LabelSettingsAudiobitDefault.place(x=12, y=345)
 
 # Inputs
 InputSettingsRecording = tk.Checkbutton(settings,  font=("TkDefaultFont", 25), bd=0)
 InputSettingsRecording.place(x=475, y=100)
 InputSettingsVideobit = tk.Spinbox(settings,  font=("TkDefaultFont", 25), width=5, bd=0, from_=0.1, to=10, increment=0.01)
 InputSettingsVideobit.place(x=475, y=200)
 InputSettingsAudiobit = tk.Spinbox(settings,  font=("TkDefaultFont", 25), width=5, bd=0, from_=0.1, to=5, increment=0.01)
 InputSettingsAudiobit.place(x=475, y=300)
 
 # Buttons
 ButtonSettingsQuit = tk.Button(settings, font=("TkDefaultFont", 35), width=15, bg='red', activebackground='red', text='Abbrechen', command=AbortSettings)
 ButtonSettingsQuit.place(x=530, y=516)
 ButtonSettingsSave = tk.Button(settings, font=("TkDefaultFont", 35), width=15, bg='green', activebackground='green', text='Speichern', command=SaveSettings)
 ButtonSettingsSave.place(x=12, y=516)
 
 settings.mainloop

# Blinken des dazugehörigen Buttons bei neuen Fragen
def BlinkButtonQuestion():
 global StopBlinkButtonQuestion
 subprocess.Popen('aplay ~/Documents/Scripts/message_notifier.wav', shell=True)
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
 subprocess.Popen('aplay ~/Documents/Scripts/message_notifier.wav', shell=True)
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
  ButtonQuestion.config(text='Beiträge (' + str(len(Questions)) + ')')
  ButtonQuestion.update()
  subprocess.call('aplay ~/Documents/Scripts/message_start.wav && pico2wave --lang de-DE --wave /tmp/audio.wav "' + question[1] + '"; aplay /tmp/audio.wav; rm /tmp/audio.wav', shell=True)
  if len(Questions) == 0:
   StopBlinkButtonQuestion = True
  if question[2] != "":
   subprocess.call('pcmanfm ' + question[2], shell=True)
   time.sleep(5)
   os.remove(question[2])

# Serviceanfrage anzeigen
def ShowService():
 global Services, StopBlinkButtonService
 if len(Services) != 0:
  service = Services.pop(0)
  LabelNews.config(text=service[0])
  LabelNews.update()
  ButtonService.config(text='Serviceanfragen (' + str(len(Services)) + ')')
  ButtonService.update()
  subprocess.call('aplay ~/Documents/Scripts/message_start.wav && pico2wave --lang de-DE --wave /tmp/audio.wav "' + service[1] + '"; aplay /tmp/audio.wav; rm /tmp/audio.wav', shell=True)
  if len(Services) == 0:
   StopBlinkButtonService = True


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
     if content.find(">>") != -1:
      content, file = content.split(">>")
      filepath = file
     else:
      filepath = ""
     if operator == 'question':
      operator = ' hat folgenden Beitrag '
      Questions.append([name + ' > ' + content, name + operator + content, filepath])
      ButtonQuestion.config(text='Beiträge (' + str(len(Questions)) + ')', command=ShowQuestion)
      threading.Thread(target=BlinkButtonQuestion).start()
     elif operator == 'service':
      operator = ' bittet um eine '
      Services.append([name + ' > ' + content, name + operator + content])
      ButtonService.config(text='Serviceanfragen (' + str(len(Services)) + ')', command=ShowService)
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
 ButtonSettings.config(state='disabled')
 ButtonSettings.update()

def EnableButtons():
 ButtonStream.config(state='normal')
 ButtonQuit.config(state='normal')
 ButtonQuestion.config(state='normal')
 ButtonService.config(state='normal')
 ButtonSettings.config(state='normal')

def TellWeb(status):
 if Webconnection == True:
  if status == True:
   LocalIP = subprocess.check_output('curl ifconfig.me', shell=True)
   requests.get('https://schueler:zabelhaft@fgrunert.lima-city.de/schule/index.php?sendip=' + LocalIP)
  else:
   requests.get('https://schueler:zabelhaft@fgrunert.lima-city.de/schule/index.php?sendip=null')

def StartStream():
 global Preview
 DisableButtons()
 Preview = False
 time.sleep(1.5)
 TellWeb(True)
 os.mknod('/var/www/html/interaction/stream.tmp')
 threading.Thread(target=CheckLog).start()
 subprocess.Popen('sudo /home/pi/picam/picam -o /run/shm/hls - --channels 1 -w 1280 -h 720 --audiobitrate 40000 --videobitrate 1800000 --vfr --avclevel 3.1 --autoex --alsadev hw:1,0', shell=True)
 ButtonStream.config(text="Stream beenden")
 ButtonStream.config(command=StopStream)
 LabelStatus.config(text="Stream aktiv")
 LabelStatus.config(fg="green")
 subprocess.call('aplay ~/Documents/Scripts/message_start.wav && pico2wave --lang de-DE --wave /tmp/audio.wav "Stream gestartet"; aplay /tmp/audio.wav; rm /tmp/audio.wav', shell=True)
 EnableButtons()
 GPIO.output(33, GPIO.HIGH)

def StopStream():
 global StopBlinkButtonQuestion, StopBlinkButtonService, Preview
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
 Preview = True
 threading.Thread(target=ImageUpdate).start()
 subprocess.call('aplay ~/Documents/Scripts/message_start.wav && pico2wave --lang de-DE --wave /tmp/audio.wav "Stream beendet"; aplay /tmp/audio.wav; rm /tmp/audio.wav', shell=True)
 EnableButtons()
 GPIO.output(33, GPIO.LOW)

def QuitSystem():
 global Preview
 DisableButtons()
 subprocess.call('aplay ~/Documents/Scripts/message_start.wav && pico2wave --lang de-DE --wave /tmp/audio.wav "System wird beendet"; aplay /tmp/audio.wav; rm /tmp/audio.wav', shell=True)
 GPIO.output(16, GPIO.LOW)
 GPIO.output(33, GPIO.LOW)
 if os.path.exists('/var/www/html/interaction/stream.tmp'):
  StopStream()
  Preview = False
  time.sleep(1.5)
  proc_python = os.getpid()
  subprocess.Popen('sudo kill ' + str(proc_python), shell=True)
 else:
  Preview = False
  time.sleep(1.5)
  proc_python = os.getpid()
  subprocess.Popen('sudo kill ' + str(proc_python), shell=True)

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
ButtonQuit.place(x=502, y=87)
ButtonQuestion = tk.Button(root, font=("TkDefaultFont", 35), width=16, text='Beiträge (' + str(len(Questions)) + ')', command=ShowQuestion)
ButtonQuestion.place(x=502, y=162)
ButtonService = tk.Button(root, font=("TkDefaultFont", 35), width=16, text='Serviceanfragen (' + str(len(Services)) + ')', command=ShowService)
ButtonService.place(x=502, y=237)
ButtonSettings = tk.Button(root, font=("TkDefaultFont", 35), width=16, text='Einstellungen ⚙', command=ShowSettings)
ButtonSettings.place(x=502, y=312)

StandardColor = ButtonStream.cget('bg')
StandardColorActive = ButtonStream.cget('activebackground')

root.mainloop()
