
#-------------------------------- Dependencies ------------------------------------------

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog

import pygame.mixer as mixer # needs installation

import pyttsx3 as ptts # needs installation

from random import random
import re, os

#-------------------------------- Global Constants --------------------------------------

# Appearance
WIDTH = 800
HEIGHT = 600

# File Handling
AudioDir = "./Audio/"

#------------------------------- Basic Util Funcs ---------------------------------------

def makeRandomName():
    return str(int(random()*(10**7)))

def chopStringIntoSentences(txt):
    chopped = list()
    i = 0
    for j in range(len(txt)):
        char = txt[j]
        if char == "!" or char == "?" or char == ".":
            j += 1
            chopped.append(txt[i:j])
            i = j
    return chopped

#-------------------------------- Text to Speech ----------------------------------------

def makeAudioOnDisk(txt, filename = None):
    if filename == None: filename = makeRandomName()
    if not os.path.exists(AudioDir): os.mkdir(AudioDir)
    fileaddr = AudioDir + filename + ".wav"
    tts.save_to_file(txt, fileaddr)
    tts.runAndWait()
    return fileaddr

#--------------------------------- GUI Functions ----------------------------------------

def displayWaitingState():
    txtbox.configure(text = "Reading stopped. Load a file")
    btn_back.configure(state = "disabled")
    btn_togg.configure(state = "disabled")
    btn_next.configure(state = "disabled")
    btn_load.configure(state = "normal")
    btn_stop.configure(state = "disabled")

def displayLoadingState():
    txtbox.configure(text = "Loading....")

def displayReadingState():
    btn_back.configure(state = "normal")
    btn_togg.configure(state = "normal")
    btn_togg.configure(text = "Pause")
    btn_next.configure(state = "normal")
    btn_load.configure(state = "disabled")
    btn_stop.configure(state = "normal")

def loadBtn():
    file = filedialog.askopenfile("r", title = "Choose a file to read", initialdir = "./", filetypes = {("Text Files", "*.txt")})
    if file != None: 
        displayLoadingState()
        window.update()
        txt = file.read()
        txt = re.sub("\s+", " ", re.sub("\n", " ", txt))
        controller.init(chopStringIntoSentences(txt))
        displayReadingState()

def stopBtn():
    controller.terminateReading()
    displayWaitingState()

def toggBtn():
    if btn_togg["text"] == "Pause":
        btn_togg.configure(text = "Play")
        controller.pauseReading()
    elif btn_togg["text"] == "Play":
        btn_togg.configure(text = "Pause")
        controller.resumeReading()

def backBtn(): controller.goBack()

def nextBtn(): controller.goNext()

#----------------------------------- GUI Markup -----------------------------------------

# Creating a Window
window = tk.Tk()
window.title("Text to Speech")
window.minsize(WIDTH, HEIGHT)

# Setting Theme
window.tk.call("source", "scidthemes/scidthemes.tcl")
mainStyle = ttk.Style()
mainStyle.theme_use("scidpurple")
mainStyle.configure("TButton", font = ("helvetica", 14))
mainStyle.configure("TLabel", font = ("helvetica", 20))

# Setting Grid
window.rowconfigure([0,1,2,3,4,5,6,7], weight = 1)
window.columnconfigure(0, weight = 1)

# Textbox
txtbox = ttk.Label(master = window, text = "Load a file", wraplength = 700, justify = tk.CENTER, anchor="center")
txtbox.grid(row = 0, column = 0, rowspan = 7, columnspan = 1, sticky = "nsew")

# Buttons
control_frame = ttk.Frame(master = window)
control_frame.grid(row = 7, column = 0, rowspan = 1, columnspan = 1, sticky = "nsew")

control_frame.rowconfigure(0, weight = 1)
control_frame.columnconfigure([0,1,2,3,4,5,6,7], weight = 1)

btn_back = ttk.Button(master = control_frame, text = "Back", state = "disabled", command = backBtn) 
btn_togg = ttk.Button(master = control_frame, text = "Play", state = "disabled", command = toggBtn) 
btn_next = ttk.Button(master = control_frame, text = "Next", state = "disabled", command = nextBtn) 
btn_load = ttk.Button(master = control_frame, text = "Load", command = loadBtn) 
btn_stop = ttk.Button(master = control_frame, text = "Stop", state = "disabled", command = stopBtn) 
btn_back.grid(row = 0, column = 0, padx = 30, ipady = 10, sticky = "ew")
btn_togg.grid(row = 0, column = 1, padx = 30, ipady = 10, sticky = "ew")
btn_next.grid(row = 0, column = 2, padx = 30, ipady = 10, sticky = "ew")
btn_load.grid(row = 0, column = 6, padx = 30, ipady = 10, sticky = "ew")
btn_stop.grid(row = 0, column = 7, padx = 30, ipady = 10, sticky = "ew")

#----------------------------------- Controller -------------------------------------------

class Controller:
    def __init__(self):
        self.__voicelines = list()
        self.__nextLine = -1
        self.__reading = False

    def init(self, sentences):
        self.__sentences = sentences
        self.__rootName = makeRandomName()
        self.createVoicelines()
        self.__nextLine = 0
        self.__reading = True
        
    def createVoicelines(self):
        for i in range(len(self.__sentences)):
            self.__voicelines.append(makeAudioOnDisk(self.__sentences[i], str(int(self.__rootName) + i)))
            
    def readNextLine(self):
        mixer.music.load(self.__voicelines[self.__nextLine])
        mixer.music.play()

    def cleanup(self):
        self.__reading = False
        self.__voicelines.clear() 
        self.__sentences.clear() 
        txtbox.configure(text = "End of File Reached. Load another one.")

    def pauseReading(self):
        mixer.music.pause()
        self.__reading = False
    
    def resumeReading(self):
        mixer.music.unpause()
        self.__reading = True

    def goNext(self):
        if self.__reading and self.__nextLine < len(self.__voicelines):
            mixer.music.stop()
            mixer.music.unload()

    def goBack(self):
        if self.__reading and self.__nextLine > 1:
            mixer.music.stop()
            mixer.music.unload()
            self.__nextLine -= 2

    def terminateReading(self):
        mixer.music.stop()
        mixer.music.unload()
        self.cleanup()
        displayWaitingState()

    def main(self):
        window.after(10, controller.main)
        if self.__reading:
            if not mixer.music.get_busy():
                if self.__nextLine >= len(self.__voicelines):
                    self.terminateReading()
                else: 
                    self.readNextLine()
                    txtbox.configure(text = self.__sentences[self.__nextLine])
                    self.__nextLine += 1
        
#--------------------------------------------- STARTUP -----------------------------------------------------

tts = ptts.init()
tts.setProperty("rate", 150)

mixer.init()
controller = Controller()

def destroy():
    for file in os.scandir(AudioDir):
        os.remove(file.path)
    window.destroy()

window.protocol("WM_DELETE_WINDOW", destroy)
window.after(10, controller.main)
window.mainloop()
