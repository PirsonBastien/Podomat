import time

import serial
import tkinter as tk

def Serial():
    port = 'COM5'
    baud_rate = 9600  # Assurez-vous que le débit binaire correspond à celui de votre appareil Bluetooth

    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        print(f"Connexion établie sur {port} à {baud_rate} bps")
        message='80'
        ser.write(message.encode())
        nombre_données=0
        while nombre_données==0:
                # Lire les données depuis le port COM
                nombre_données = ser.readline().decode('utf-8').rstrip()
                nombre=int(nombre_données)
                print(f"NB ligne: {nombre}")
                tk.Label(fenetre, text=nombre).grid(column=20, row=10)

                while nombre!=0:




                     valeur=ser.readline().decode('utf-8').rstrip()
                     print(f"Données reçues: {valeur}")
                     tk.Label(fenetre,text=valeur).grid(column=10, row=8)
                     nombre=nombre-1

                break

    except serial.SerialException as e:
        print(f"Erreur lors de l'ouverture du port série : {e}")










#code fenetre
fenetre = tk.Tk()
fenetre.title('Podomat')
fenetre.geometry("1366x768")
fenetre.resizable(width=True,height=True)
fenetre.config(background='#CCCCCC')

tk.Label(fenetre,text="Valeur actuelle : 0").grid(column=0, row=0)
tk.Button (fenetre,text='Reception données', command=Serial).grid(column=2, row=1)


fenetre.mainloop()
