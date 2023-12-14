import tkinter as tk
from tkinter import ttk, filedialog
from typing import Dict, List
import canvas
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.path import Path
from matplotlib import patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import serial.tools.list_ports

# Déclaration de la variable globale pour bp play/pause
playing = True
# Déclaration de la variable globale pour ax
ax = None

# Variable des potentiomètre
Resistance_pot = [128, 128, 128, 128, 128, 128, 128, 128]

# Déclaration et initialisation du tableau
tableau = {
        'Capteur 1': [0, 0, 0],
        'Capteur 2': [0, 0, 0],
        'Capteur 3': [0, 0, 0],
        'Capteur 4': [0, 0, 0],
        'Capteur 5': [0, 0, 0],
        'Timecode': [1, 2, 3]
}

max_value = max(max(tableau['Capteur 1']), max(tableau['Capteur 2']), max(tableau['Capteur 3']), max(tableau['Capteur 4']),
                max(tableau['Capteur 5']))


# Trouve le port sur lequel est connecté le portenta
def trouver_port_arduino_portenta():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "portenta" in port.description:
            return port.device
    return None


# Permet l'autocalibration des capteurs
def calib():
    port = trouver_port_arduino_portenta()
    baud_rate = 9600

    ser = serial.Serial(port, baud_rate, timeout=1)
    if port is None:
        calib_messages.insert(tk.END, "Pas d'appareil connecté, calibration annulée\n")
    else:
        calib_messages.insert(tk.END, f"Connexion établie sur {port} à {baud_rate} bps\n")

        # Déclaration et initialisation du tableau
    temp_tab = {
        'Capteur 1': [],
        'Capteur 2': [],
        'Capteur 3': [],
        'Capteur 4': [],
        'Capteur 5': [],
    }

    nb_mesure = 5

    # Envoi du nombre de de cycle
    nb_mesure_string = str(nb_mesure) + '\n'
    ser.write(nb_mesure_string.encode('utf-8'))

    # Envoi des resistance des pot
    for R in Resistance_pot:
        Resistance_pot_string = str(R) + '\n'
        ser.write(Resistance_pot_string.encode('utf-8'))

    ser.write(message.encode())
    ref = 1000
    nb_donnee_reception_tableau = 0
    nb_cycle_reception_tableau = 0
    num_capteurs = 5
    capt = [0] * num_capteurs
    pot = [0] * num_capteurs

# boucle qui permet d'ajuster les valeurs de potentiomètre
# le portenta recoit le numéro du capteur puis doit envoyer la valeur du capt ensuite il recoit la valeur ajuster du potentiometer
    while Val_etape < 8:
        Data = ser.readline().decode('utf-8').strip()
        if Val_etape == 1 and Data == 'Reception données fin':
            Etape = Data
            Data = 0
            print(Etape)
            calib_messages.insert(tk.END, Etape + '\n')
            Val_etape += 1
        elif Val_etape == 2 and Data == 'Reglage pot ok':
            Etape = Data
            Data = 0
            print(Etape)
            calib_messages.insert(tk.END, Etape + '\n')
            Val_etape += 1
        elif Val_etape == 3 and Data == 'Acquisition ok':
            Etape = Data
            Data = 0
            print(Etape)
            calib_messages.insert(tk.END, Etape + '\n')
            Val_etape += 1
        elif Val_etape == 4 and Data == 'Envoi':
            Etape = Data
            Data = 0
            print(Etape)
            calib_messages.insert(tk.END, Etape + '\n')
            Val_etape += 1
        elif Val_etape == 5:
            nombre_cycle_reception = int(Data)
            Data = 0
            print(nombre_cycle_reception)
            Val_etape += 1
        elif Val_etape == 6:
            nombre_donnee_reception = int(Data)
            Data = 0
            print(nombre_donnee_reception)
            Val_etape += 1
        elif Val_etape == 7:
            if (nb_donnee_reception_tableau < nb_cycle_reception_tableau and
                    nb_donnee_reception_tableau < nombre_donnee_reception):
                # Affecter les valeurs reçues aux capteurs correspondants
                temp_tab['Capteur 1'].append(int(Data))
                temp_tab['Capteur 2'].append(int(Data))
                temp_tab['Capteur 3'].append(int(Data))
                temp_tab['Capteur 4'].append(int(Data))
                temp_tab['Capteur 5'].append(int(Data))

                nb_donnee_reception_tableau += 1

                if nb_donnee_reception_tableau == nombre_donnee_reception:
                    nb_cycle_reception_tableau += 1
                    nb_donnee_reception_tableau = 0
            else:
                Val_etape += 1
                ser.close()

    moyennes = {
        'Capteur 1': np.mean(temp_tab['Capteur 1']),
        'Capteur 2': np.mean(temp_tab['Capteur 2']),
        'Capteur 3': np.mean(temp_tab['Capteur 3']),
        'Capteur 4': np.mean(temp_tab['Capteur 4']),
        'Capteur 5': np.mean(temp_tab['Capteur 5']),
    }

    for i in range(num_capteurs):
        while capt[i] != ref:

            if capt[i] < ref and pot[i] < 255:
                Resistance_pot[i] += 1
                ser.write(str(pot[i]).encode())
            elif capt[i] > ref and pot[i] > 0:
                Resistance_pot[i] -= 1
                ser.write(str(pot[i]).encode())
            elif capt[i] < ref and pot[i] == 255:
                calib_messages.insert(tk.END, f"Erreur de calibration sur le capteur {i + 1}\n")
                break
            elif capt[i] > ref and pot[i] == 0:
                calib_messages.insert(tk.END, f"Erreur de calibration sur le capteur {i + 1}\n")
                break


# Envoie les donnée vers le portenta
def serie():
    clear_tableau()
    port = trouver_port_arduino_portenta()
    baud_rate = 9600

    # Connection au port com => A enlever
    ser = serial.Serial(port, baud_rate, timeout=1)
    print(f"Connexion établie sur {port} à {baud_rate} bps")

    Val_etape = 1

    # Envoi du nombre de de cycle
    Nombre_cycle_string = str(Nombre_cycle) + '\n'
    ser.write(Nombre_cycle_string.encode('utf-8'))

    # Envoi des resistance des pot
    for R in Resistance_pot:
        Resistance_pot_string = str(R) + '\n'
        ser.write(Resistance_pot_string.encode('utf-8'))

    nombre_donnee_reception_tableau = 0
    nombre_cycle_reception_tableau = 0
    timestamp = 0

    while Val_etape < 8:
        Data = ser.readline().decode('utf-8').strip()
        if Val_etape == 1 and Data == 'Reception données fin':
            Etape = Data
            Data = 0
            print(Etape)
            calib_messages.insert(tk.END, Etape + '\n')
            Val_etape += 1
        elif Val_etape == 2 and Data == 'Reglage pot ok':
            Etape = Data
            Data = 0
            print(Etape)
            calib_messages.insert(tk.END, Etape + '\n')
            Val_etape += 1
        elif Val_etape == 3 and Data == 'Acquisition ok':
            Etape = Data
            Data = 0
            print(Etape)
            calib_messages.insert(tk.END, Etape + '\n')
            Val_etape += 1
        elif Val_etape == 4 and Data == 'Envoi':
            Etape = Data
            Data = 0
            print(Etape)
            calib_messages.insert(tk.END, Etape + '\n')
            Val_etape += 1
        elif Val_etape == 5:
            nombre_cycle_reception = int(Data)
            Data = 0
            print(nombre_cycle_reception)
            Val_etape += 1
        elif Val_etape == 6:
            nombre_donnee_reception = int(Data)
            Data = 0
            print(nombre_donnee_reception)
            Val_etape += 1
        elif Val_etape == 7:
            if (nombre_cycle_reception_tableau < nombre_cycle_reception and
                    nombre_donnee_reception_tableau < nombre_donnee_reception):
                # Affecter les valeurs reçues aux capteurs correspondants
                tableau['Capteur 1'].append(int(Data))
                tableau['Capteur 2'].append(int(Data))  # Remplacez par la bonne valeur
                tableau['Capteur 3'].append(int(Data))  # Remplacez par la bonne valeur
                tableau['Capteur 4'].append(int(Data))  # Remplacez par la bonne valeur
                tableau['Capteur 5'].append(int(Data))  # Remplacez par la bonne valeur

                # Gérer le timestamp
                if len(tableau['Timecode']) < nombre_cycle_reception_tableau + 1:
                    tableau['Timecode'].append(timestamp)
                    timestamp += 500

                nombre_donnee_reception_tableau += 1

                if nombre_donnee_reception_tableau == nombre_donnee_reception:
                    nombre_cycle_reception_tableau += 1
                    nombre_donnee_reception_tableau = 0
            else:
                print(tableau)
                calib_messages.insert(tk.END, "Mesure finie \n")
                calib_messages.delete(1.0, tk.END)
                Val_etape += 1
                ser.close()

            # Retourner le tableau à la fin de la fonction
        return tableau


def clear_tableau():
    # Vider toutes les listes associées à chaque capteur
    tableau['Capteur 1'] = []
    tableau['Capteur 2'] = []
    tableau['Capteur 3'] = []
    tableau['Capteur 4'] = []
    tableau['Capteur 5'] = []
    tableau['Timecode'] = []


# Fonction pour mettre à jour le graphique en fonction des cases cochées
def update_plot():
    selected_measures = [measure for measure, var in zip(tableau.keys(), measure_checkbuttons) if var.get()]
    if any(selected_measures):
        show_graph(selected_measures)
        canvas3.draw()
    else:
        # Si aucune case n'est cochée, effacez le graphique
        ax3.clear()
        ax3.set_title('Pas de capteur sélectionné')
        canvas3.draw()


# Fonction pour créer et afficher le graphique
def show_graph(selected_measures):
    ax3.clear()

    plotted = False  # Variable pour vérifier si au moins une mesure est tracée

    for measure in selected_measures:
        if measure in tableau and tableau[measure] is not None:
            ax3.plot(tableau['Timecode'], tableau[measure], label=measure)
            plotted = True

    if plotted:
        ax3.legend()
        ax3.set_xlabel('Timecode [ms]')
        ax3.set_ylabel('Pression [N]')
        ax3.set_title('Graphique de mesure')
    else:
        ax3.set_title('Pas de capteur sélectionné')


# Fonction pour afficher le tableau de données avec une barre de défilement
def show_table_with_scrollbar(tableau):
    # Création du cadre pour contenir le tableau et la barre de défilement
    frame = ttk.Frame(tab2)
    frame.pack(fill='both', expand=True)

    # Création du tableau avec les en-têtes
    tree = ttk.Treeview(frame, columns=tuple(tableau.keys()), show='headings')
    for col in tableau.keys():
        tree.heading(col, text=col)
        tree.column(col, width=100)

    # Ajout des données dans le tableau
    for i in range(len(tableau['Timecode'])):
        tree.insert('', 'end', values=tuple([tableau[col][i] for col in tableau.keys()]))

    # Configuration de la barre de défilement
    scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
    tree.configure(yscroll=scrollbar.set)

    # Placement du tableau et de la barre de défilement
    tree.pack(side=tk.LEFT, fill='both', expand=True)
    scrollbar.pack(side=tk.RIGHT, fill='y')


def update_table(tree, tableau):
    # Effacez les anciennes entrées dans le tableau
    for item in tree.get_children():
        tree.delete(item)

    # Ajoutez les nouvelles données dans le tableau
    for i in range(len(tableau['Timecode'])):
        tree.insert('', 'end', values=tuple([tableau[col][i] for col in tableau.keys()]))


# Fonction pour importer les données au format CSV et remplacer les données existantes
def import_from_csv():
    global tableau
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        df = pd.read_csv(file_path, sep=';')  # Assurez-vous de spécifier le bon séparateur
        new_tableau = df.to_dict(orient='list')

        # Mettez à jour le dictionnaire tableau avec les nouvelles données
        for key, value in new_tableau.items():
            tableau[key] = value

        # Mettez à jour le tableau avec les nouvelles données
        update_table(tree, tableau)


# Fonction pour exporter les données au format CSV
def export_to_csv(tableau):
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        df = pd.tableauFrame(tableau)
        df.to_csv(file_path, index=False, sep=';')  # Ajout du paramètre sep=';'


# Fonction appelée lorsque l'onglet est changé
def on_tab_change(event):
    selected_tab = notebook.index(notebook.select())

    # Affichez le contenu de l'onglet actuellement sélectionné
    if 0 <= selected_tab < len(tab_contents):
        tab_contents[selected_tab].pack()


# Fonction pour créer et afficher la heatmap
def show_heatmap_on_tab4(timecode_value, ax4, tableau):
    update_heatmap(timecode_value, ax4, tableau)


# Fonction pour mettre à jour la heatmap en fonction du timecode sélectionné
def update_heatmap(timecode_value, ax4, tableau):
    timecode = int(timecode_value)
    first_values = [tableau['Capteur 1'][timecode - 1], tableau['Capteur 2'][timecode - 1], tableau['Capteur 3'][timecode - 1],
                    tableau['Capteur 4'][timecode - 1], tableau['Capteur 5'][timecode - 1]]

    heatmap_tableau = np.zeros((7, 7))
    heatmap_tableau[1, 1] = first_values[0]
    heatmap_tableau[5, 1] = first_values[1]
    heatmap_tableau[3, 3] = first_values[2]
    heatmap_tableau[1, 5] = first_values[3]
    heatmap_tableau[5, 5] = first_values[4]

    # Define a function to get the average of adjacent points
    def get_average(x, y):
        neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        valid_neighbors = [(i, j) for i, j in neighbors if 0 <= i < 7 and 0 <= j < 7]
        values = [heatmap_tableau[i, j] for i, j in valid_neighbors]
        return np.mean(values) if values else 0

    # Fill in undefined points with the average of adjacent points
    for i in range(7):
        for j in range(7):
            if heatmap_tableau[i, j] == 0:
                heatmap_tableau[i, j] = get_average(i, j)

    ax4.clear()
    im = ax4.imshow(heatmap_tableau, cmap='YlGnBu', interpolation='nearest', vmin=0, vmax=max_value)
    colorbar.update_normal(im)
    canvas4.draw()


# Boutons pour faire défiler les timecodes
def prev_timecode():
    current_value = slider.get()
    if current_value > 1:
        slider.set(current_value - 1)


def next_timecode():
    current_value = slider.get()
    if current_value < len(tableau['Timecode']):
        slider.set(current_value + 1)


# Bouton play/pause
def toggle_play():
    global playing
    current_value = slider.get()

    if playing and current_value < len(tableau['Timecode']):
        slider.set(current_value + 1)
        tab4.after(1000, toggle_play)  # Change timecode every 1000 milliseconds (1 second)
    else:
        playing = False


def toggle_restart():
    slider.set(0)


def toggle_end():
    slider.set(len(tableau['Timecode']))


def show_loading_popup():
    loading_popup = tk.Toplevel(root)
    loading_popup.title("mesure en cours")
    loading_label = tk.Label(loading_popup, text="Veuillez attendre la fin de la mesure avant d'intéragir avec l'interface ...")
    loading_label.pack()

    # Fermez la fenêtre de chargement après un certain temps (par exemple, 3000 millisecondes)
    loading_popup.after(25000, loading_popup.destroy)


# Créez une fenêtre principale
root = tk.Tk()
root.title("Podomat")

# Créez un style personnalisé pour le widget ttk.Notebook
style = ttk.Style()
style.configure("Custom.TNotebook.Tab", font=("Arial", 18))  # Personnalisez la taille de police ici
style.configure("Custom.TNotebook", background="#288BA8")  # Personnalisez la couleur de fond ici

# Créez un widget ttk.Notebook avec le style personnalisé
notebook = ttk.Notebook(root, style="Custom.TNotebook")
notebook.pack(fill="both", expand=True)

# Liste des noms d'onglets
tab_names = ["Connexion", "Tableau de donnée", "Graphique", "heatmap"]

# Créez les onglets
tabs = []
for tab_name in tab_names:
    tab = ttk.Frame(notebook)
    tabs.append(tab)
    notebook.add(tab, text=tab_name)

# Placez les onglets dans la fenêtre principale
notebook.pack(fill="both", expand=True)

# Liste des contenus pour chaque onglet
tab_contents = []

# Contenu de l'onglet 1
tab1 = tabs[0]
connect_messages = tk.Text(tab1, height=1, width=50)
connect_messages.pack(pady=10)
port = trouver_port_arduino_portenta()
if port is not None:
    connect_messages.insert(tk.END, "Votre appareil est bien connecté\n")
else:
    connect_messages.delete('1.0', tk.END)
    connect_messages.insert(tk.END, "Votre appareil est déconnecté\n")

time_slider_label = tk.Label(tab1, text="Nombre de mesure désiré:")
time_slider_label.pack(pady=2)

time_slider = tk.Scale(tab1, from_=1, to=180, orient="horizontal", length=300)
time_slider.pack()
Nombre_cycle = time_slider.get()

weight_label = tk.Label(tab1, text="Poids de l'utilisateur en kg:")
weight_label.pack(pady=10)

weight_entry = tk.Entry(tab1)
weight_entry.pack(pady=10)

start_button = tk.Button(tab1, text="Démarrer la mesure", bg="green", fg="white",
                         font=("Arial", 20, "bold"), command=lambda: [show_loading_popup(), serie()])
start_button.pack(pady=20)

export_button = ttk.Button(tab1, text="Exporter en CSV", command=lambda: export_to_csv(tableau))
export_button.pack(pady=10)

import_button = ttk.Button(tab1, text="Importer depuis CSV", command=lambda: import_from_csv())
import_button.pack(pady=10)

Calib_button = tk.Button(tab1, text="Autocalibration", bg="green", fg="white",
                         font=("Arial", 20, "bold"), command=lambda: [calib()])
Calib_button.pack(pady=20)

calib_messages = tk.Text(tab1, height=6, width=50)
calib_messages.pack(pady=10)

# Contenu pour l'onglet 2
tab2 = tabs[1]
# Création du cadre pour contenir le tableau et la barre de défilement
frame = ttk.Frame(tab2)
frame.pack(fill='both', expand=True)

# Création du tableau avec les en-têtes
tree = ttk.Treeview(frame, columns=tuple(tableau.keys()), show='headings')
for col in tableau.keys():
    tree.heading(col, text=col)
    tree.column(col, width=100)

# Ajout des données dans le tableau
for i in range(len(tableau['Timecode'])):
    tree.insert('', 'end', values=tuple([tableau[col][i] for col in tableau.keys()]))

# Configuration de la barre de défilement
scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
tree.configure(yscroll=scrollbar.set)

# Placement du tableau et de la barre de défilement
tree.pack(side=tk.LEFT, fill='both', expand=True)
scrollbar.pack(side=tk.RIGHT, fill='y')

# Onglet 3 (contenant le graphique)
tab3 = tabs[2]

# Création d'une liste pour stocker les variables des cases à cocher
measure_checkbuttons = []

# Ajout des cases à cocher pour chaque mesure
for i, measure in enumerate(tableau.keys()):
    if measure != 'Timecode':
        var = tk.IntVar()
        check_button = tk.Checkbutton(tab3, text=measure, variable=var, command=update_plot)
        check_button.grid(row=i, column=0, sticky=tk.W)
        measure_checkbuttons.append(var)

# Création du graphique initial (vide)
fig3 = Figure(figsize=(16, 9), dpi=100)
ax3 = fig3.add_subplot(111)
canvas3 = FigureCanvasTkAgg(fig3, master=tab3)
canvas3.get_tk_widget().grid(row=0, column=1, rowspan=len(tableau) - 1, sticky=tk.W + tk.E + tk.N + tk.S)

# Onglet 4 (contenant la heatmap)
tab4 = tabs[3]

fig4 = Figure(figsize=(8, 6), dpi=100)
ax4_heatmap = fig4.add_subplot(111)

# Create canvas
canvas4 = FigureCanvasTkAgg(fig4, master=tab4)
canvas_widget = canvas4.get_tk_widget()
canvas_widget.grid(row=0, column=0, columnspan=5, sticky=tk.NSEW)  # Ensure canvas expands to fill the available space

# Initialisation de la colorbar
heatmap_tableau = np.zeros((50, 50))
im = ax4_heatmap.imshow(heatmap_tableau, cmap='YlGnBu', interpolation='nearest', vmin=0, vmax=max_value)
colorbar = fig4.colorbar(im, ax=ax4_heatmap)
colorbar.ax.set_ylabel('Pression [N]')

# Curseur pour faire défiler les valeurs du timecode
slider = tk.Scale(tab4, from_=1, to=len(tableau['Timecode']), orient="horizontal",
                  command=lambda value: show_heatmap_on_tab4(int(value), ax4_heatmap, tableau))
slider.grid(row=1, column=0, columnspan=5, sticky=tk.NSEW)

# Bp next et prev play pause
restart_button = ttk.Button(tab4, text="<<", command=toggle_restart)
prev_button = ttk.Button(tab4, text="Précédent", command=prev_timecode)
play_button = ttk.Button(tab4, text="Play/Pause", command=toggle_play)
next_button = ttk.Button(tab4, text="Suivant", command=next_timecode)
end_button = ttk.Button(tab4, text=">>", command=toggle_end)

# Grille boutons côte à côte
restart_button.grid(row=2, column=0, sticky=tk.W)
prev_button.grid(row=2, column=1, sticky=tk.W)
play_button.grid(row=2, column=2, sticky=tk.W)
next_button.grid(row=2, column=3, sticky=tk.W)
end_button.grid(row=2, column=4, sticky=tk.W)

# Centrer les boutons
tab4.update_idletasks()
button_width = max(restart_button.winfo_width(), prev_button.winfo_width(), play_button.winfo_width(),
                   next_button.winfo_width(), end_button.winfo_width())
canvas_widget.config(width=button_width)  # Adjust canvas width to match button width

# Configure les lignes et les colonnes
tab4.rowconfigure(0, weight=1)
tab4.rowconfigure(1, weight=1)
tab4.rowconfigure(2, weight=1)
tab4.columnconfigure(0, weight=1)
tab4.columnconfigure(1, weight=1)
tab4.columnconfigure(2, weight=1)
tab4.columnconfigure(3, weight=1)
tab4.columnconfigure(4, weight=1)

# Associez la fonction on_tab_change à l'événement de changement d'onglet
notebook.bind("<<NotebookTabChanged>>", on_tab_change)

# Affichez le contenu initial de l'onglet actuellement sélectionné
on_tab_change(None)  # Utilisez None pour simuler l'appel initial

# Affiche la fenêtre à bonne dimension
root.geometry(f"{1920}x{1080}")

# Démarrez la boucle principale
root.mainloop()
