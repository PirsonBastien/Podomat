import time

import serial
import tkinter as tk

def Serial():
    port = 'COM5'
    baud_rate = 9600

    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        print(f"Connexion établie sur {port} à {baud_rate} bps")
        message='80'
        ser.write(message.encode())
        nombre_ligne=0
        while nombre_ligne==0:

                nombre_ligne = ser.readline().decode('utf-8').rstrip()
                nombre_colonne=ser.readline().decode('utf-8').rstrip()
                print(f"NB ligne: {nombre_ligne}")
                print(f"NB colonne: {nombre_colonne}")
                ligne=int(nombre_ligne)
                colonne=int(nombre_colonne)

                while ligne!=0:
                     for i in range(colonne):
                         valeur=ser.readline().decode('utf-8').rstrip()
                         print(f"Données reçues: {valeur}")
                         tk.Label(fenetre,text=valeur).grid(column=10, row=8)
                     ligne=ligne-1
                ser.close()
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
