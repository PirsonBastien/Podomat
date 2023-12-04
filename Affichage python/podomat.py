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

# Déclaration de la variable globale pour bp play/pause
playing = True
# Déclaration de la variable globale pour ax
ax = None
# Déclaration de la variable globale pour tableau de mesure
data = {
        'Timecode': np.arange(1, 101),
        'Mesure 1': np.random.randint(0, 50, 100),
        'Mesure 2': np.random.randint(0, 50, 100),
        'Mesure 3': np.random.randint(0, 50, 100),
        'Mesure 4': np.random.randint(0, 50, 100),
        'Mesure 5': np.random.randint(0, 50, 100)
        }

max_value = max(max(data['Mesure 1']), max(data['Mesure 2']), max(data['Mesure 3']), max(data['Mesure 4']), max(data['Mesure 5']))

# Fonction pour créer et afficher le graphique
def show_graph(data):
    timecode = data['Timecode']
    fig, ax = plt.subplots()

    for key, value in data.items():
        if key != 'Timecode':
            ax.plot(timecode, value, label=key, marker='o')

    ax.set_xlabel('Timecode')
    ax.set_ylabel('Mesures')
    ax.set_title('Graphique de Mesures pour Différents Timecodes')
    ax.legend()

    canvas = FigureCanvasTkAgg(fig, master=tab3)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


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


# Fonction pour importer les données au format CSV
def import_from_csv():
    global data
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        df = pd.read_csv(file_path)
        data = df.to_dict(orient='list')


# Fonction pour exporter les données au format CSV
def export_to_csv(data):
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)


# Fonction appelée lorsque l'onglet est changé
def on_tab_change(event):
    selected_tab = notebook.index(notebook.select())

    # Affichez le contenu de l'onglet actuellement sélectionné
    if 0 <= selected_tab < len(tab_contents):
        tab_contents[selected_tab].pack()


# Fonction pour créer et afficher la heatmap
def show_heatmap_on_tab4(timecode_value, ax, data):
    update_heatmap(timecode_value, ax, data)


# Fonction pour mettre à jour la heatmap en fonction du timecode sélectionné
def update_heatmap(timecode_value, ax, data):
    timecode = int(timecode_value)
    first_values = [data['Mesure 1'][timecode-1], data['Mesure 2'][timecode-1], data['Mesure 3'][timecode-1],
                    data['Mesure 4'][timecode-1], data['Mesure 5'][timecode-1]]

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

    ax.clear()
    im = ax.imshow(heatmap_data, cmap='YlGnBu', interpolation='nearest', vmin=0, vmax=max_value)
    colorbar.update_normal(im)
    canvas.draw()


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
# Bouton d'exportation
export_button = ttk.Button(tab1, text="Exporter en CSV", command=export_to_csv)
export_button.pack(pady=10)

# Bouton d'importation
import_button = ttk.Button(tab1, text="Importer depuis CSV", command=import_from_csv)
import_button.pack(pady=10)

# Ajout du slider pour régler le temps de mesure
time_slider_label = tk.Label(tab1, text="Réglage temps de mesure")
time_slider_label.pack(pady=10)

time_slider = tk.Scale(tab1, from_=1, to=180, orient="horizontal", length=300)
time_slider.pack()

# Ajout du bouton pour démarrer la mesure Ajouter la logique dedans
start_button = tk.Button(tab1, text="Démarrer la mesure", bg="green", fg="white", font=("Arial", 20, "bold"))
start_button.pack(pady=20)
# Ajout nécessaire de connexion pour le portenta dans l'onglet 1


# Contenu pour l'onglet 2
tab2 = tabs[1]
show_table_with_scrollbar(data)  # Affichez le graphique dans l'onglet 2


# Onglet 3 (contenant le graphique)
tab3 = tabs[2]

# Create canvas
canvas2 = FigureCanvasTkAgg(show_graph(data), master=tab3)
canvas_widget = canvas2.get_tk_widget()
canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)  # Ensure canvas expands to fill the available space


# Onglet 4 (contenant la heatmap)
tab4 = tabs[3]

fig = Figure(figsize=(8, 6), dpi=100)
ax = fig.add_subplot(111)

# Create canvas
canvas = FigureCanvasTkAgg(fig, master=tab4)
canvas_widget = canvas.get_tk_widget()
canvas_widget.grid(row=0, column=0, columnspan=5, sticky=tk.NSEW)  # Ensure canvas expands to fill the available space

# Initialisation de la colorbar
heatmap_data = np.zeros((50, 50))
im = ax.imshow(heatmap_data, cmap='YlGnBu', interpolation='nearest', vmin=0, vmax=max_value)
colorbar = fig.colorbar(im, ax=ax)
colorbar.ax.set_ylabel('Mesures')

# Curseur pour faire défiler les valeurs du timecode
slider = tk.Scale(tab4, from_=1, to=len(data['Timecode']), orient="horizontal", command=lambda value: show_heatmap_on_tab4(int(value), ax, data))
slider.grid(row=1, column=0, columnspan=5, sticky=tk.NSEW)

# Bp next et prev play pause
restart_button = ttk.Button(tab4, text="<<", command=toggle_restart)
prev_button = ttk.Button(tab4, text="Précédent", command=prev_timecode)
play_button = ttk.Button(tab4, text="Play/Pause", command=toggle_play)
next_button = ttk.Button(tab4, text="Suivant", command=next_timecode)
end_button = ttk.Button(tab4, text=">>", command=toggle_end)

# Grid buttons side by side
restart_button.grid(row=2, column=0, sticky=tk.W)
prev_button.grid(row=2, column=1, sticky=tk.W)
play_button.grid(row=2, column=2, sticky=tk.W)
next_button.grid(row=2, column=3, sticky=tk.W)
end_button.grid(row=2, column=4, sticky=tk.W)

# Center the buttons
tab4.update_idletasks()
button_width = max(restart_button.winfo_width(), prev_button.winfo_width(), play_button.winfo_width(), next_button.winfo_width(), end_button.winfo_width())
canvas_widget.config(width=button_width)  # Adjust canvas width to match button width

# Configure row and column weights
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
