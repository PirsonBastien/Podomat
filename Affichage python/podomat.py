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
# Déclaration de la variable globale pour tableau de mesure
data = {
    'Capteur 1': np.random.randint(0, 50, 100),
    'Capteur 2': np.random.randint(0, 50, 100),
    'Capteur 3': np.random.randint(0, 50, 100),
    'Capteur 4': np.random.randint(0, 50, 100),
    'Capteur 5': np.random.randint(0, 50, 100),
    'Timecode': np.arange(1, 101)
}

max_value = max(max(data['Capteur 1']), max(data['Capteur 2']), max(data['Capteur 3']), max(data['Capteur 4']),
                max(data['Capteur 5']))


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
    # Quand le portenta reçoit le signal c passe en calibration
    message = "c"
    ser.write(message.encode())
    ref = 1000

    num_capteurs = 5
    capt = [0] * num_capteurs
    pot = [0] * num_capteurs

# boucle qui permet d'ajuster les valeurs de potentiomètre
# le portenta recoit le numéro du capteur puis doit envoyer la valeur du capt ensuite il recoit la valeur ajuster du potentiometer
    for i in range(num_capteurs):
        while capt[i] != ref:
            ser.write(str(i).encode())
            capt[i] = int(ser.readline().decode('utf-8').strip())

            if capt[i] < ref and pot[i] < 255:
                pot[i] += 1
                ser.write(str(pot[i]).encode())
            elif capt[i] > ref and pot[i] > 0:
                pot[i] -= 1
                ser.write(str(pot[i]).encode())
            elif capt[i] < ref and pot[i] == 255:
                calib_messages.insert(tk.END, f"Erreur de calibration sur le capteur {i + 1}\n")
                break
            elif capt[i] > ref and pot[i] == 0:
                calib_messages.insert(tk.END, f"Erreur de calibration sur le capteur {i + 1}\n")
                break


# Envoie les donnée vers le portenta
def serie():
    port = trouver_port_arduino_portenta()
    baud_rate = 9600
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        print(f"Connexion établie sur {port} à {baud_rate} bps")
        message = "1"
        ser.write(message.encode())
        nombre_ligne = 0
        while nombre_ligne == 0:

            nombre_ligne = ser.readline().decode('utf-8').strip()
            nombre_colonne = ser.readline().decode('utf-8').strip()
            print(f"NB ligne: {nombre_ligne}")
            print(f"NB colonne: {nombre_colonne}")
            ligne = int(nombre_ligne)
            colonne = int(nombre_colonne)

            while ligne != 0:
                for i in range(colonne):
                    valeur = ser.readline().decode('utf-8').rstrip()
                    print(f"Données reçues: {valeur}")
                    tk.Label(fenetre, text=valeur).grid(column=10, row=8)
                ligne = ligne - 1
            ser.close()
            break


    except serial.SerialException as e:
        print(f"Erreur lors de l'ouverture du port série : {e}")


# Fonction pour mettre à jour le graphique en fonction des cases cochées
def update_plot():
    selected_measures = [measure for measure, var in zip(data.keys(), measure_checkbuttons) if var.get()]
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
        if measure in data and data[measure] is not None:
            ax3.plot(data['Timecode'], data[measure], label=measure)
            plotted = True

    if plotted:
        ax3.legend()
        ax3.set_xlabel('Timecode [ms]')
        ax3.set_ylabel('Pression [N]')
        ax3.set_title('Graphique de mesure')
    else:
        ax3.set_title('Pas de capteur sélectionné')


# Fonction pour afficher le tableau de données avec une barre de défilement
def show_table_with_scrollbar(data):
    # Création du cadre pour contenir le tableau et la barre de défilement
    frame = ttk.Frame(tab2)
    frame.pack(fill='both', expand=True)

    # Création du tableau avec les en-têtes
    tree = ttk.Treeview(frame, columns=tuple(data.keys()), show='headings')
    for col in data.keys():
        tree.heading(col, text=col)
        tree.column(col, width=100)

    # Ajout des données dans le tableau
    for i in range(len(data['Timecode'])):
        tree.insert('', 'end', values=tuple([data[col][i] for col in data.keys()]))

    # Configuration de la barre de défilement
    scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
    tree.configure(yscroll=scrollbar.set)

    # Placement du tableau et de la barre de défilement
    tree.pack(side=tk.LEFT, fill='both', expand=True)
    scrollbar.pack(side=tk.RIGHT, fill='y')


def update_table(tree, data):
    # Effacez les anciennes entrées dans le tableau
    for item in tree.get_children():
        tree.delete(item)

    # Ajoutez les nouvelles données dans le tableau
    for i in range(len(data['Timecode'])):
        tree.insert('', 'end', values=tuple([data[col][i] for col in data.keys()]))


# Fonction pour importer les données au format CSV et remplacer les données existantes
def import_from_csv():
    global data
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        df = pd.read_csv(file_path, sep=';')  # Assurez-vous de spécifier le bon séparateur
        new_data = df.to_dict(orient='list')

        # Mettez à jour le dictionnaire data avec les nouvelles données
        for key, value in new_data.items():
            data[key] = value

        # Mettez à jour le tableau avec les nouvelles données
        update_table(tree, data)


# Fonction pour exporter les données au format CSV
def export_to_csv(data):
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False, sep=';')  # Ajout du paramètre sep=';'


# Fonction appelée lorsque l'onglet est changé
def on_tab_change(event):
    selected_tab = notebook.index(notebook.select())

    # Affichez le contenu de l'onglet actuellement sélectionné
    if 0 <= selected_tab < len(tab_contents):
        tab_contents[selected_tab].pack()


# Fonction pour créer et afficher la heatmap
def show_heatmap_on_tab4(timecode_value, ax4, data):
    update_heatmap(timecode_value, ax4, data)


# Fonction pour mettre à jour la heatmap en fonction du timecode sélectionné
def update_heatmap(timecode_value, ax4, data):
    timecode = int(timecode_value)
    first_values = [data['Capteur 1'][timecode - 1], data['Capteur 2'][timecode - 1], data['Capteur 3'][timecode - 1],
                    data['Capteur 4'][timecode - 1], data['Capteur 5'][timecode - 1]]

    heatmap_data = np.zeros((7, 7))
    heatmap_data[1, 1] = first_values[0]
    heatmap_data[5, 1] = first_values[1]
    heatmap_data[3, 3] = first_values[2]
    heatmap_data[1, 5] = first_values[3]
    heatmap_data[5, 5] = first_values[4]

    # Define a function to get the average of adjacent points
    def get_average(x, y):
        neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        valid_neighbors = [(i, j) for i, j in neighbors if 0 <= i < 7 and 0 <= j < 7]
        values = [heatmap_data[i, j] for i, j in valid_neighbors]
        return np.mean(values) if values else 0

    # Fill in undefined points with the average of adjacent points
    for i in range(7):
        for j in range(7):
            if heatmap_data[i, j] == 0:
                heatmap_data[i, j] = get_average(i, j)

    ax4.clear()
    im = ax4.imshow(heatmap_data, cmap='YlGnBu', interpolation='nearest', vmin=0, vmax=max_value)
    colorbar.update_normal(im)
    canvas4.draw()


# Boutons pour faire défiler les timecodes
def prev_timecode():
    current_value = slider.get()
    if current_value > 1:
        slider.set(current_value - 1)


def next_timecode():
    current_value = slider.get()
    if current_value < len(data['Timecode']):
        slider.set(current_value + 1)


# Bouton play/pause
def toggle_play():
    global playing
    current_value = slider.get()

    if playing and current_value < len(data['Timecode']):
        slider.set(current_value + 1)
        tab4.after(1000, toggle_play)  # Change timecode every 1000 milliseconds (1 second)
    else:
        playing = False


def toggle_restart():
    slider.set(0)


def toggle_end():
    slider.set(len(data['Timecode']))


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

# Contenu pour l'onglet 1
tab1 = tabs[0]

# Création de la zone pour afficher les messages de la console
connect_messages = tk.Text(tab1, height=1, width=50)
connect_messages.pack(pady=10)
port = trouver_port_arduino_portenta()
if port != None:
    connect_messages.insert(tk.END, "Votre appareil est bien connecté\n")
else:
    connect_messages.delete('1.0', tk.END)
    connect_messages.insert(tk.END, "Votre appareil est déconnecté\n")

# Ajout du slider pour régler le temps de mesure
time_slider_label = tk.Label(tab1, text="Nombre de mesure désiré :")
time_slider_label.pack(pady=2)

time_slider = tk.Scale(tab1, from_=1, to=180, orient="horizontal", length=300)
time_slider.pack()
valeur_du_curseur = time_slider.get()

# Ajout de la zone pour le poids de l'utilisateur
weight_label = tk.Label(tab1, text="Poids de l'utilisateur en kg:")
weight_label.pack(pady=10)

weight_entry = tk.Entry(tab1)
weight_entry.pack(pady=10)

start_button = tk.Button(tab1, text="Démarrer la mesure", bg="green", fg="white", font=("Arial", 20, "bold"),command=lambda: [show_loading_popup(), serie()])
start_button.pack(pady=20)
# Ajout nécessaire de connexion pour le portenta dans l'onglet 1

# Bouton d'exportation
export_button = ttk.Button(tab1, text="Exporter en CSV", command=lambda: export_to_csv(data))
export_button.pack(pady=10)

# Bouton d'importation
import_button = ttk.Button(tab1, text="Importer depuis CSV",  command=lambda: import_from_csv())
import_button.pack(pady=10)
Calib_button = tk.Button(tab1, text="Autocalibration", bg="green", fg="white", font=("Arial", 20, "bold"),command=lambda: [calib()])
Calib_button.pack(pady=20)

calib_messages = tk.Text(tab1, height=6, width=50)
calib_messages.pack(pady=10)

# Contenu pour l'onglet 2
tab2 = tabs[1]
# Création du cadre pour contenir le tableau et la barre de défilement
frame = ttk.Frame(tab2)
frame.pack(fill='both', expand=True)

# Création du tableau avec les en-têtes
tree = ttk.Treeview(frame, columns=tuple(data.keys()), show='headings')
for col in data.keys():
    tree.heading(col, text=col)
    tree.column(col, width=100)

# Ajout des données dans le tableau
for i in range(len(data['Timecode'])):
    tree.insert('', 'end', values=tuple([data[col][i] for col in data.keys()]))

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
for i, measure in enumerate(data.keys()):
    if measure != 'Timecode':
        var = tk.IntVar()
        check_button = tk.Checkbutton(tab3, text=measure, variable=var, command=update_plot)
        check_button.grid(row=i, column=0, sticky=tk.W)
        measure_checkbuttons.append(var)

# Création du graphique initial (vide)
fig3 = Figure(figsize=(16, 9), dpi=100)
ax3 = fig3.add_subplot(111)
canvas3 = FigureCanvasTkAgg(fig3, master=tab3)
canvas3.get_tk_widget().grid(row=0, column=1, rowspan=len(data) - 1, sticky=tk.W + tk.E + tk.N + tk.S)

# Onglet 4 (contenant la heatmap)
tab4 = tabs[3]

fig4 = Figure(figsize=(8, 6), dpi=100)
ax4_heatmap = fig4.add_subplot(111)

# Create canvas
canvas4 = FigureCanvasTkAgg(fig4, master=tab4)
canvas_widget = canvas4.get_tk_widget()
canvas_widget.grid(row=0, column=0, columnspan=5, sticky=tk.NSEW)  # Ensure canvas expands to fill the available space

# Initialisation de la colorbar
heatmap_data = np.zeros((50, 50))
im = ax4_heatmap.imshow(heatmap_data, cmap='YlGnBu', interpolation='nearest', vmin=0, vmax=max_value)
colorbar = fig4.colorbar(im, ax=ax4_heatmap)
colorbar.ax.set_ylabel('Pression [N]')

# Curseur pour faire défiler les valeurs du timecode
slider = tk.Scale(tab4, from_=1, to=len(data['Timecode']), orient="horizontal",
                  command=lambda value: show_heatmap_on_tab4(int(value), ax4_heatmap, data))
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
