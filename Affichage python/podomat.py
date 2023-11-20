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

# Déclaration de la variable globale pour ax
ax = None
data = {
            'Timecode': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'Mesure 1': [2, 4, 6, 8, 10, 14, 25, 49, 34, 24],
            'Mesure 2': [1, 3, 5, 7, 9, 32, 14, 25, 49, 34],
            'Mesure 3': [3, 6, 9, 12, 15, 2, 14, 25, 49, 34],
            'Mesure 4': [4, 8, 12, 16, 20, 18, 14, 25, 49, 34],
            'Mesure 5': [5, 10, 15, 20, 25, 42, 14, 25, 49, 34]
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


# Fonction pour afficher le tableau de données
def show_table(data):

    tree = ttk.Treeview(tab2, columns=tuple(data.keys()), show='headings')
    for col in data.keys():
        tree.heading(col, text=col)
        tree.column(col, width=100)
    for i in range(len(data['Timecode'])):
        tree.insert('', 'end', values=tuple([data[col][i] for col in data.keys()]))
    tree.pack(fill='both', expand=True)


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

    heatmap_data = np.zeros((50, 50))
    heatmap_data[5, 5] = first_values[0]
    heatmap_data[5, 45] = first_values[1]
    heatmap_data[25, 25] = first_values[2]
    heatmap_data[45, 5] = first_values[3]
    heatmap_data[45, 45] = first_values[4]

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
    current_value = slider.get()
    if current_value < len(data['Timecode']):
        slider.set(current_value + 1)
        tab4.after(1000, toggle_play)  # Change timecode every 1000 milliseconds (1 second)


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

# Onglet 3 (contenant le graphique)
tab3 = tabs[2]

show_graph(data)  # Affichez le graphique dans l'onglet 1

# Contenu pour l'onglet 2
tab2 = tabs[1]
show_table(data)  # Affichez le graphique dans l'onglet 1

# Contenu pour l'onglet 1
tab1 = tabs[0]
# Bouton d'exportation dans l'onglet 1
export_button = ttk.Button(tab1, text="Exporter en CSV", command=export_to_csv)
export_button.pack(pady=10)

# Bouton d'importation dans l'onglet 3
import_button = ttk.Button(tab1, text="Importer depuis CSV", command=import_from_csv)
import_button.pack(pady=10)

# Ajout du slider pour régler le temps de mesure
time_slider_label = tk.Label(tab1, text="Réglage temps de mesure")
time_slider_label.pack(pady=10)

time_slider = tk.Scale(tab1, from_=1, to=180, orient="horizontal", length=300)
time_slider.pack()

# Ajout du bouton pour démarrer la mesure
start_button = tk.Button(tab1, text="Démarrer la mesure", bg="green", fg="white", font=("Arial", 20, "bold"))
start_button.pack(pady=20)

# Ajout nécessaire de connexion pour le portenta dans l'onglet 1


# Onglet 4 (contenant la heatmap)
tab4 = tabs[3]

fig = Figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot(111)

canvas = FigureCanvasTkAgg(fig, master=tab4)
canvas.get_tk_widget().pack()

# Initialisation de la colorbar
heatmap_data = np.zeros((3, 3))
im = ax.imshow(heatmap_data, cmap='YlGnBu', interpolation='nearest', vmin=0, vmax=max_value)
colorbar = fig.colorbar(im, ax=ax)
colorbar.ax.set_ylabel('Mesures')

# Curseur pour faire défiler les valeurs du timecode
slider = tk.Scale(tab4, from_=1, to=len(data['Timecode']), orient="horizontal", command=lambda value: show_heatmap_on_tab4(int(value), ax, data))
slider.pack(side=tk.TOP)

# Bp next et prev play pause
restart_button = ttk.Button(tab4, text="<<", command=toggle_restart)
restart_button.pack(side=tk.LEFT)

prev_button = ttk.Button(tab4, text="Précédent", command=prev_timecode)
prev_button.pack(side=tk.LEFT)

play_button = ttk.Button(tab4, text="Play", command=toggle_play)
play_button.pack(side=tk.LEFT)

next_button = ttk.Button(tab4, text="Suivant", command=next_timecode)
next_button.pack(side=tk.LEFT)

end_button = ttk.Button(tab4, text=">>", command=toggle_end)
end_button.pack(side=tk.LEFT)

# Associez la fonction on_tab_change à l'événement de changement d'onglet
notebook.bind("<<NotebookTabChanged>>", on_tab_change)

# Affichez le contenu initial de l'onglet actuellement sélectionné
on_tab_change(None)  # Utilisez None pour simuler l'appel initial

# Affiche la fenêtre à bonne dimension
root.geometry(f"{1920}x{1080}")

# Démarrez la boucle principale
root.mainloop()
