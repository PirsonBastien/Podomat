import tkinter as tk
from tkinter import ttk, filedialog
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial.tools.list_ports
from scipy.signal import savgol_filter
import time
import threading
import mplcursors

# Déclaration de la variable globale pour bp play/pause
playing = True
# Déclaration de la variable globale pour ax
ax = None

# Variable des potentiomètre
Resistance_pot = [128, 128, 128, 128, 128, 128, 128, 128]

# force associée aux masses de calibration de 1, 5 kg
masse = [9.81, 49.05]

Nombre_cycle = 1
switch_calib = 1

# Déclaration et initialisation du tableau
global tableau
tableau = {
    'Capteur 1': [0],
    'Capteur 2': [0],
    'Capteur 3': [0],
    'Capteur 4': [0],
    'Capteur 5': [0],
    'Timecode': [0]
}
max_value = max(max(tableau['Capteur 1']), max(tableau['Capteur 2']), max(tableau['Capteur 3']),
                max(tableau['Capteur 4']), max(tableau['Capteur 5']))


# Trouve le port sur lequel est connecté le portenta
def trouver_port_arduino_portenta():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "Périphérique série USB" in port.description:
            return port.device
    return None


def update_connection_status():
    while True:
        # Liste des ports série actuellement disponibles
        liste_ports = serial.tools.list_ports.comports()
        ports = [port.device for port in liste_ports]

        # Vérifier si le port Arduino Portenta est dans la liste
        port_arduino_portenta = trouver_port_arduino_portenta()

        if port_arduino_portenta in ports:
            connect_messages.delete('1.0', tk.END)
            connect_messages.insert(tk.END, "Votre appareil est bien connecté\n")
        else:
            connect_messages.delete('1.0', tk.END)
            connect_messages.insert(tk.END, "Votre appareil est déconnecté\n")

        # Pause d'une seconde avant la prochaine mise à jour
        time.sleep(1)


# Envoie les donnée vers le portenta
def mesure():
    clear_tableau()
    print(tableau)
    port = trouver_port_arduino_portenta()
    baud_rate = 115200
    ser = serial.Serial(port, baud_rate, timeout=1)
    print(f"Connexion établie sur {port} à {baud_rate} bps")
    print(Nombre_cycle)
    Val_etape = 1

    # Envoi du nombre de de cycle
    Nombre_cycle_string = str(Nombre_cycle) + '\n'
    ser.write(Nombre_cycle_string.encode('utf-8'))

    # Envoi des resistance des pot
    for R in Resistance_pot:
        print(R)
        Resistance_pot_string = str(R) + '\n'
        ser.write(Resistance_pot_string.encode('utf-8'))

    nombre_donnee_reception_tableau = 0
    nombre_cycle_reception_tableau = 0
    timestamp = 0
    z = 1

    while Val_etape < 8:
        donnee = ser.readline().decode('utf-8').strip()
        if Val_etape == 1 and donnee == 'Reception données fin':
            etape = donnee
            print(etape)
            calib_messages.insert(tk.END, etape + '\n')
            Val_etape += 1
        elif Val_etape == 2 and donnee == 'Reglage pot ok':
            etape = donnee
            print(etape)
            calib_messages.insert(tk.END, etape + '\n')
            Val_etape += 1
        elif Val_etape == 3 and donnee == 'Acquisition ok':
            etape = donnee
            print(etape)
            calib_messages.insert(tk.END, etape + '\n')
            Val_etape += 1
        elif Val_etape == 4 and donnee == 'Envoi':
            etape = donnee
            print(etape)
            calib_messages.insert(tk.END, etape + '\n')
            Val_etape += 1
        elif Val_etape == 5:
            nombre_cycle_reception = int(donnee)
            print(nombre_cycle_reception)
            Val_etape += 1
        elif Val_etape == 6:
            nombre_donnee_reception = int(donnee)
            Val_etape += 1
        elif Val_etape == 7:
            if nombre_cycle_reception_tableau < nombre_cycle_reception and nombre_donnee_reception_tableau < nombre_donnee_reception:
                # Affecter les valeurs reçues aux capteurs correspondants

                tableau['Capteur ' + str(z)].append(int(donnee))
                z += 1
                # Gérer le timestamp
                if nombre_donnee_reception_tableau == nombre_donnee_reception - 1:
                    tableau['Timecode'].append(timestamp)
                    timestamp += 0.5
                    z = 1
                nombre_donnee_reception_tableau += 1

                if nombre_donnee_reception_tableau == nombre_donnee_reception:
                    nombre_cycle_reception_tableau += 1
                    nombre_donnee_reception_tableau = 0
            else:
                calib_messages.insert(tk.END, "Mesure finie \n")
                Val_etape += 1
                ser.close()

                for capteur, valeurs in tableau.items():
                    if capteur != 'Timecode':
                        # Multiplication par 2 des valeurs des capteurs et remplacement des valeurs négatives par 0
                        index_capteur = int(capteur.split()[-1]) - 1  # Récupérer le numéro du capteur
                        correction = meancapt_resultats[index_capteur]  # Utiliser la valeur associée depuis meancapt
                        pentecourbe = pente_resultats[index_capteur]
                        tableau[capteur] = [(valeur - correction) / pentecourbe for valeur in valeurs]

                        print(correction)
                        print(pentecourbe)

                # Retourner le tableau à la fin de la fonction
                print('fin')
                update_table(tree, tableau)
                update_plot()


def meanCapteur():
    meancapt = [np.mean(tableau[f'Capteur {i+1}']) for i in range(5)]
    pente = [(65536 - mean) / 4448 for mean in meancapt]

    return meancapt, pente


def calib():
    global switch_calib
    if switch_calib == 1:
        clear_tableau()
        print(tableau)
        port = trouver_port_arduino_portenta()
        baud_rate = 115200
        ser = serial.Serial(port, baud_rate, timeout=1)
        print(f"Connexion établie sur {port} à {baud_rate} bps")
        Val_etape = 1
        nombre_calib = 20000
        # Envoi du nombre de de cycle
        nombre_calib_string = str(nombre_calib) + '\n'
        ser.write(nombre_calib_string.encode('utf-8'))

        # Envoi des resistance des pot
        for R in Resistance_pot:
            Resistance_pot_string = str(R) + '\n'
            ser.write(Resistance_pot_string.encode('utf-8'))

        nombre_donnee_reception_tableau = 0
        nombre_cycle_reception_tableau = 0
        timestamp = 0
        z = 1

        while Val_etape < 8:
            donnee = ser.readline().decode('utf-8').strip()
            if Val_etape == 1 and donnee == 'Reception données fin':
                etape = donnee
                print(etape)
                Val_etape += 1
            elif Val_etape == 2 and donnee == 'Reglage pot ok':
                etape = donnee
                print(etape)
                Val_etape += 1
            elif Val_etape == 3 and donnee == 'Acquisition ok':
                etape = donnee
                print(etape)
                Val_etape += 1
            elif Val_etape == 4 and donnee == 'Envoi':
                etape = donnee
                print(etape)
                Val_etape += 1
            elif Val_etape == 5:
                nombre_cycle_reception = int(donnee)
                print(nombre_cycle_reception)
                Val_etape += 1
            elif Val_etape == 6:
                nombre_donnee_reception = int(donnee)
                Val_etape += 1
            elif Val_etape == 7:
                if (nombre_cycle_reception_tableau < nombre_cycle_reception and
                        nombre_donnee_reception_tableau < nombre_donnee_reception):
                    # Affecter les valeurs reçues aux capteurs correspondants

                    tableau['Capteur ' + str(z)].append(int(donnee))
                    z += 1
                    # Gérer le timestamp
                    if nombre_donnee_reception_tableau == nombre_donnee_reception - 1:
                        tableau['Timecode'].append(timestamp)
                        timestamp += 0.5
                        z = 1
                    nombre_donnee_reception_tableau += 1

                    if nombre_donnee_reception_tableau == nombre_donnee_reception:
                        nombre_cycle_reception_tableau += 1
                        nombre_donnee_reception_tableau = 0
                else:
                    Val_etape += 1
                    ser.close()

                    for capteur, valeurs in tableau.items():
                        tableau[capteur].extend(valeurs)

                    # Retourner le tableau à la fin de la fonction
                    print('fin')

        # Récupération des résultats
        global meancapt_resultats
        global pente_resultats
        meancapt_resultats, pente_resultats = meanCapteur()
        print(meancapt_resultats)
        print(pente_resultats)
        switch_calib += 1
        print(switch_calib)
        calib_messages.insert(tk.END, 'Calibration à vide effectuée, posez le poids 1 et réappyuez sur le bouton\n')
    elif switch_calib == 2:
        u = 0
        for i in range(len(meancapt_resultats)):
            while (
                    meancapt_resultats[i] < masse[0] - (3 / 100) * masse[0] or
                    meancapt_resultats[i] > masse[0] + (3 / 100) * masse[0] or u < 2
            ):
                mesure()
                print(u)
                meanCapteur()
                print(meancapt_resultats[i])
                meancapt_resultats, pente_resultats = meanCapteur()
                if meancapt_resultats[i] < masse[0] - (3 / 100) * masse[0]:
                    Resistance_pot[i] += 1
                    u += 1
                elif meancapt_resultats[i] > masse[0] + (3 / 100) * masse[0]:
                    Resistance_pot[i] -= 1
                    u += 1
                elif u == 2:
                    break

        switch_calib += 1
        calib_messages.insert(tk.END, 'Calibration avec poids 1 effectuée, posez le poids 2 et réappyuez sur le bouton\n')
    elif switch_calib == 3:
        u = 0
        for i in range(len(meancapt_resultats)):
            while (
                    meancapt_resultats[i] < masse[1] - (3 / 100) * masse[1] or
                    meancapt_resultats[i] > masse[1] + (3 / 100) * masse[1]
            ):
                mesure()
                meanCapteur()
                meancapt_resultats, pente_resultats = meanCapteur()
                print(meancapt_resultats[i])
                if meancapt_resultats[i] < masse[1] - (3 / 100) * masse[1]:
                    Resistance_pot[i] += 1
                    u += 1
                    print(u)
                elif meancapt_resultats[i] > masse[0] + (3 / 100) * masse[1]:
                    Resistance_pot[i] -= 1
                    u += 1
                    print(u)
                elif u == 2:
                    break

        switch_calib += 1
        calib_messages.insert(tk.END, 'Calibration avec poids 2 effectuée\n')
        calib_messages.insert(tk.END, 'Calibration terminée\n')


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
def show_graph(selected_measures, window_size=100, order=2):
    ax3.clear()

    plotted = False  # Variable pour vérifier si au moins une mesure est tracée

    for measure in selected_measures:
        if measure in tableau and tableau[measure] is not None:
            # Lissage des données avec le filtre de Savitzky-Golay
            y_values = tableau[measure]
            y_smooth2 = savgol_filter(savgol_filter(y_values, window_size, order), window_size, order)
            # ax3.plot(tableau['Timecode'], y_values, label=f'{measure} (pas lissé)')
            # ax3.plot(tableau['Timecode'], y_smooth, label=f'{measure} (lissé)')
            ax3.plot(tableau['Timecode'], y_smooth2, label=f'{measure} (Lissé)')
            plotted = True

    if plotted:
        ax3.legend()
        ax3.set_xlabel('Timecode [ms]')
        ax3.set_ylabel('Force [N]')
        ax3.set_title('Graphique de mesure (avec lissage)')

        # Ajout du curseur
        cursor = mplcursors.cursor(ax3, hover=True)
        cursor.connect("add", lambda sel: sel.annotation.set_text(f"X={sel.target[0]:.2f}, Y={sel.target[1]:.2f}"))

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
        df = pd.DataFrame(tableau)
        df.to_csv(file_path, index=False, sep=';')  # Ajout du paramètre sep=';'


# Fonction appelée lorsque l'onglet est changé
def on_tab_change(event):
    selected_tab = notebook.index(notebook.select())

    # Affichez le contenu de l'onglet actuellement sélectionné
    if 0 <= selected_tab < len(tab_contents):
        tab_contents[selected_tab].pack()


# Fonction pour mettre à jour la heatmap en fonction du timecode sélectionné
def show_heatmap_on_tab4(timecode_value, ax4, tableau):
    timecode = int(timecode_value)
    first_values = [tableau['Capteur 1'][timecode - 1], tableau['Capteur 2'][timecode - 1],
                    tableau['Capteur 3'][timecode - 1],
                    tableau['Capteur 4'][timecode - 1], tableau['Capteur 5'][timecode - 1]]

    heatmap_tableau = np.zeros((7, 7))
    heatmap_tableau[1, 1] = first_values[4]
    heatmap_tableau[5, 1] = first_values[2]
    heatmap_tableau[3, 3] = first_values[3]
    heatmap_tableau[1, 5] = first_values[1]
    heatmap_tableau[5, 5] = first_values[0]

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
    loading_label = tk.Label(loading_popup,
                             text="Veuillez attendre la fin de la mesure avant d'intéragir avec l'interface ...")
    loading_label.pack()

    # Fermez la fenêtre de chargement après un certain temps (par exemple, 3000 millisecondes)
    loading_popup.after(25000, loading_popup.destroy)


def update_time_slider(event):
    global Nombre_cycle
    Nombre_cycle = 2000 * time_slider.get()


def update_weight_entry(event):
    global var
    global Resistance_pot
    var = weight_entry.get()    #TERMINER EQUATION AVEC CALIB
    Resistance_pot = [var, var, var, var, var, var, var, var]
    print(var)

def on_tab_enter(event):
    slider.configure(to=len(tableau['Timecode']))


# Fonction appelée lors du mouvement du curseur
def on_slider_move(value):
    show_heatmap_on_tab4(value, ax4_heatmap, tableau)
    global max_value
    max_value = max(max(tableau['Capteur 1']), max(tableau['Capteur 2']), max(tableau['Capteur 3']),
                    max(tableau['Capteur 4']),
                    max(tableau['Capteur 5']))




# Créer un thread pour la mise à jour de l'interface
update_thread = threading.Thread(target=update_connection_status, daemon=True)

# Démarrer le thread
update_thread.start()

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

# Définir une largeur commune
common_width = 50

connect_messages = tk.Text(tab1, height=1, width=common_width)
connect_messages.pack(pady=10)

port = trouver_port_arduino_portenta()

time_slider_label = tk.Label(tab1, text="Temps d'acquisition en seconde :", width=70)
time_slider_label.pack(pady=2)

time_slider = tk.Scale(tab1, from_=1, to=250, orient="horizontal", length=300, width=common_width)
time_slider.pack()
time_slider.bind("<Motion>", update_time_slider)

weight_label = tk.Label(tab1, text="Poids de l'utilisateur en kg:", width=common_width)
weight_label.pack(pady=10)

weight_entry = tk.Entry(tab1, width=common_width)
weight_entry.pack(pady=10)
weight_entry.bind("<Motion>", update_weight_entry)

start_button = tk.Button(tab1, text="Démarrer la mesure", bg="green", fg="white",
                         font=("Arial", 14, "bold"), command=lambda: mesure(), width=30)
start_button.pack(pady=20)

export_button = ttk.Button(tab1, text="Exporter en CSV", command=lambda: export_to_csv(tableau), width=common_width)
export_button.pack(pady=10)

import_button = ttk.Button(tab1, text="Importer depuis CSV", command=lambda: import_from_csv(), width=common_width)
import_button.pack(pady=10)

Calib_button = tk.Button(tab1, text="Autocalibration", bg="green", fg="white",
                         font=("Arial", 14, "bold"), command=lambda: calib(), width=30)
Calib_button.pack(pady=20)

# Ajouter une barre de défilement verticale
calib_scrollbar = tk.Scrollbar(tab1)
calib_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Ajouter la zone de texte avec la barre de défilement
calib_messages = tk.Text(tab1, height=6, width=common_width, yscrollcommand=calib_scrollbar.set)
calib_messages.pack(pady=10)

# Configurer la barre de défilement pour fonctionner avec la zone de texte
calib_scrollbar.config(command=calib_messages.yview)

# Ajouter un bouton pour effacer le contenu de la zone de texte
clear_button = tk.Button(tab1, text="Effacer le contenu", command=lambda: calib_messages.delete(1.0, tk.END))
clear_button.pack(pady=10)


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
tab4.bind("<Enter>", on_tab_enter)
# Utilisation de l'événement <Motion> pour mettre à jour la heatmap pendant le mouvement du curseur
tab4.bind("<Motion>", lambda event: on_slider_move(slider.get()))

slider = tk.Scale(tab4, from_=0, to=len(tableau['Timecode']), orient="horizontal",
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
