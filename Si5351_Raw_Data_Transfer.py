#!/usr/bin/python -d
# -*- coding: utf-8 -*-
# Designed for Python 2


import sys
import os
import serial # Pyserial
from Tkinter import *      # Permet la création de fenêtres et de widgets
#from tkFileDialog   import askopenfilename
import tkMessageBox
import time
import platform
import base64
import webbrowser

# Variables et Constantes Globales
Arret = False
global img
global thread

# Fonctions diverses
def is_number(s): 
	try:
	  float(s)
	  return True
	except ValueError:
	  return False
		
def ErrMsg(errorString):
	TextMessBox.config(fg="red")
	TextMessBox.insert(END, errorString)			
	TextMessBox.see(END)
	TextMessBox.update()
	ser.close()
	Bouton_Transfert.config(state=NORMAL)


def successMsg(successString):
	TextMessBox.config(fg="blue")
	TextMessBox.insert(END, successString)			
	TextMessBox.see(END)
	TextMessBox.update()


def Bascule_Bouton_About():
	webbrowser.open('file://'+ os.path.realpath('About_Raw.html'),new=1, autoraise=True)

# Fonction de transmission des parametres vers l'Arduino
def Bascule_Bouton_Transfert():
	global ser
	Bouton_Transfert.config(state=DISABLED)
 	time.sleep(0.1)
 	
	# Validation du contenu
	TempText = DataBox.get("1.0",'end-1c').splitlines(1)   # split the lines and removes the "\n"
	for line in TempText:
		if str(line[0]) == ";" or str(line[0]) == "\n": pass
		else: 
			line_params = line.replace(';',',').split(",")	# cree un array de chaines de caracteres en unicodes
			if not(is_number(str(line_params[0])) and is_number(str(line_params[1]))): 				
				ErrMsg("\nError! One or more of the entry fields contain non-numerals or is not preperly formatted. Please correct...")
				return		
	successMsg("\n-----------------------------------------\nConfiguration Transfer Initiated...")

	#Ouverture du port
	port_error = False
	try:
		s = serial.Serial(Serial_Port_Value.get())
		s.close()
	except (OSError, serial.SerialException):
		port_error = True
		ErrMsg("\nError! Serial port is unavailable or not present. Verify port naming")
		return
	if port_error == False:
		ser.baudrate = 1200
		ser.timeout = 10
		ser.port = str(Serial_Port_Value.get())	# 
		ser.open()			# Attention! Génère un Reset de l'Arduino via la broche DTR
		ser.flushInput()
		if ser.read(1) == 'R':	successMsg("\nProcessor reset completed")
		else:
			ErrMsg("\nError! Software did not receive confirmation of the ATmega processor reset completion. Verify \n 1- proper processor board programming \n 2- proper USB connectivity to the processor board")
			return
		# Transmission des donnees
		ser.write("@");		# Signale le début de l'envoi des paramètres raw
		for line in TempText:
			if str(line[0]) == ";" or str(line[0]) == "\n": pass
			else: 
				line_params = line.replace(';',',').split(",")	# cree un array de chaines de caracteres en unicodes
				print(str(line_params[0])+ "," + str(line_params[1]) + ";")
				ser.write(str(line_params[0])+ "," + str(line_params[1]) + ";");		# il faut retirer les unicodes.		
				time.sleep(0.05)			# Pause requise pour que l'Arduino gobe les caractères avant que son Rx buffer soit plein
		ser.write("%")		# Envoyer un caractere de fin d'envoi
		while ser.out_waiting !=0: pass
		if ser.read(1) == 'O':		successMsg("\nConfiguration data received by processor")
		else:
			ErrMsg("\nError! Software did not receive confirmation that the ATmega processor received the configuration data. Try again...")
			return
		if ser.read(1) == 'E':		successMsg("\nConfiguration saved to the ATmega processor EEPROM")
		else:
			ErrMsg("\nError! Software did not receive confirmation that the configuration data was saved to the ATmega processor EEPROM. Try again...")
			return
		if ser.read(1) == 'S':		successMsg("\nConfiguration data transferred from the ATmega processor to the Si5351")
		else:
			ErrMsg("\nError! Software did not receive confirmation that the configuration data transferred from the ATmega processor to the Si5351. Try again...")
			return
		ser.close()
		successMsg("\nConfiguration Success!")
		Bouton_Transfert.config(state=NORMAL)
		
def Bascule_Bouton_Sortie():
	try:
		Datafile = open(os.path.join(os.getcwd(),"Raw_Data.txt"),'w') # Open text file for writing
#		text = DataBox.get("1.0",'end-1c')
		Datafile.write(DataBox.get("1.0",'end-1c')) # Position X de la fenetre
		Datafile.close()
	except IOError:
		ErrMsg("\nError! Software cannot save the raw data. Will revert to default values at next launch. Exiting...")
		time.sleep(5)
		# Saving program settings
	try:
		file = open("./saved_settings_raw.cfg",'w') # Open text file for writing
		file.write(str(Fenetre_Princ.winfo_x()) + "\n") # Position X de la fenetre
		file.write(str(Fenetre_Princ.winfo_y()) + "\n") # Position X de la fenetre
		file.write(Serial_Port_Value.get() + "\n")
		file.close()
	except IOError:
		ErrMsg("\nError! Software cannot save its window settings. Will revert to default values at next launch. Exiting...")
		time.sleep(5)
	sys.exit()

# Création de la fenêtre principale

bgcolor =  'snow3' # 'gray77'   CadetBlue3
Main_Window_Width_x = 800
Main_Window_Width_y = 540

Fenetre_Princ = Tk()
Fenetre_Princ.title("Si5351 Raw Data Transfer")     # Titre donné à la fenêtre
Fenetre_Princ.geometry('{}x{}'.format(Main_Window_Width_x,Main_Window_Width_y))
Fenetre_Princ.resizable(False, False)

canvas = Canvas(Fenetre_Princ, width = Main_Window_Width_x, height = Main_Window_Width_y-61, bd=0)    
#canvas.create_rectangle(0, 0, Main_Window_Width_x, Main_Window_Width_y, fill=bgcolor, width=0)
canvas.pack()

canvas.create_text(270, 5, text="Si5351 Raw Data Transfer", font=("Helvetica", 16), fill="blue", anchor = NW)  

# Positionnement absolu de tous les éléments 
first_element_offset_x = 30
first_element_offset_y = 10

# La boite de texte pour les donnees brutes
DataBoxFrm = Frame(Fenetre_Princ )
DataBoxFrm.place(x =0, y = 50, width = Main_Window_Width_x, height = 350)
DataBox = Text(DataBoxFrm, font=("Monospace", 12),state=NORMAL,bg="light gray",borderwidth=1,  undo=True, wrap='word', relief="sunken") 
DataS = Scrollbar(DataBoxFrm,orient="vertical",command=DataBox.yview)
DataBox.configure(yscrollcommand=DataS.set)
DataS.pack(fill=Y,side=RIGHT)
DataBox.pack(side=TOP, fill=X)
DataBox.config(fg="black")
#DataBox.mark_set("insert", "%d.%d" % (0,0))
DataBox.update()

# Zone de messages
TextMessBoxFrm = Frame(Fenetre_Princ, width = Main_Window_Width_x, height = 60)
TextMessBoxFrm.pack(side=BOTTOM,fill=X)
TextMessBox = Text(TextMessBoxFrm, font=("Helvetica", 10), fg="blue",state=NORMAL,bg="light gray",borderwidth=1,  undo=True, wrap='word') #relief="sunken"
S = Scrollbar(TextMessBoxFrm,orient="vertical",command=TextMessBox.yview)
TextMessBox.configure(yscrollcommand=S.set)
S.pack(fill=Y,side=RIGHT)
TextMessBox.pack(side=BOTTOM, fill=X)

# Creation des boutons

# Bouton de transfert.
canvas.create_text(first_element_offset_x+68, first_element_offset_y+402, text="Serial Port", font=("Helvetica", 10), fill="blue", anchor = NW) 
Serial_Port_Value = StringVar(Fenetre_Princ)      # Créer la variable texte
Serial_Port = Entry(Fenetre_Princ, textvariable=Serial_Port_Value) # values=("1", "2", "3", "4", "5"), 
Serial_Port.place(x=first_element_offset_x+55, y=first_element_offset_y+417)  
if platform.system() == "Windows": 
	Serial_Port_Value.set("COM1")
	Serial_Port.config(width=13,relief="sunken", borderwidth=3)
else: 
	Serial_Port_Value.set("/dev/ttyUSB0")      # Lui donner la valeur initiale    
	Serial_Port.config(width=10,relief="sunken", borderwidth=3)

Bouton_Transfert_Label = StringVar()
Bouton_Transfert_Label.set("Transfer")
Bouton_Transfert = Button(Fenetre_Princ, textvariable=Bouton_Transfert_Label, width=10, relief="raised", border=3, command=Bascule_Bouton_Transfert)     #Créer le bouton à bascule
Bouton_Transfert.place(x=first_element_offset_x+150, y=first_element_offset_y+415)    # Positionner le bouton

#Bouton de Sortie
Bouton_Sortie_Label = StringVar()
Bouton_Sortie_Label.set("Exit")
Bouton_Sortie_Label = Button(Fenetre_Princ, textvariable=Bouton_Sortie_Label, width=10, relief="raised", border=3, command=Bascule_Bouton_Sortie)     #Créer le bouton à bascule
Bouton_Sortie_Label.place(x=first_element_offset_x+550, y=first_element_offset_y+415)    # Positionner le bouton

#Bouton About
Bouton_Sortie_Label = StringVar()
Bouton_Sortie_Label.set("About...")
Bouton_Sortie_Label = Button(Fenetre_Princ, textvariable=Bouton_Sortie_Label, width=10, relief="raised", border=3, command=Bascule_Bouton_About)     #Créer le bouton à bascule
Bouton_Sortie_Label.place(x=first_element_offset_x+350, y=first_element_offset_y+415)    # Positionner le bouton


# Port Serie
global ser 
ser = serial.Serial()

# Lecture du fichier de configuration
try:
	file = open(os.path.join(os.getcwd(),"saved_settings_raw.cfg"),'r') # Open text file for writing
	Fenetre_Princ.geometry('%dx%d+%d+%d' % (Main_Window_Width_x,Main_Window_Width_y, int(file.readline()), int(file.readline())))
	Serial_Port_Value.set(file.readline()[0:-1])
	file.close()
except IOError:
	ErrMsg("\nError! Software cannot retrieve its window settings. Reverting to default values...")
except ValueError: 
	ErrMsg("\nError! Software cannot retrieve its window settings. Reverting to default values...")

# Chargement des donnees dans la fenetre
try:
	Datafile = open(os.path.join(os.getcwd(),"Raw_Data.txt"),'r') # Open text file for writing
	DataBox.insert(END, Datafile.read())			
	DataBox.update()
	Datafile.close()
except IOError:
	ErrMsg("\nError! Software cannot retrieve the raw data. Reverting to default values...")
except ValueError: 
	ErrMsg("\nError! Software cannot retrieve the raw data. Reverting to default values...")


canvas.pack()  # Important pour rafraichir tout le text

successMsg("Welcome to the Si5351A/B/C Raw Data Transfer Software, by by Bert-VE2ZAZ, Version 0.3, April 2019. http://ve2zaz.net")
successMsg("\nPlease note that the settings shown are retrieved from the last session, not from the ATmega processor EEPROM.")

#Fenetre_Princ.protocol("WM_DELETE_WINDOW", Bascule_Bouton_Sortie)

Fenetre_Princ.mainloop()      

	
