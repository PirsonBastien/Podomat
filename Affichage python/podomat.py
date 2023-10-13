import tkinter as tk
from tkinter import ttk, filedialog
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Fonction pour créer et afficher le graphique
def show_graph():
    timecode = [1, 2, 3, 4, 5]
    mesure1 = [2, 4, 6, 8, 10]
    mesure2 = [1, 3, 5, 7, 9]
    mesure3 = [3, 6, 9, 12, 15]
    mesure4 = [4, 8, 12, 16, 20]
    mesure5 = [5, 10, 15, 20, 25]

    fig, ax = plt.subplots()
    ax.plot(timecode, mesure1, label='Mesure 1', marker='o')
    ax.plot(timecode, mesure2, label='Mesure 2', marker='o')
    ax.plot(timecode, mesure3, label='Mesure 3', marker='o')
    ax.plot(timecode, mesure4, label='Mesure 4', marker='o')
    ax.plot(timecode, mesure5, label='Mesure 5', marker='o')

    ax.set_xlabel('Timecode')
    ax.set_ylabel('Mesures')
    ax.set_title('Graphique de Mesures pour Différents Timecodes')
    ax.legend()

    canvas = FigureCanvasTkAgg(fig, master=tab1)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


# Fonction pour afficher le tableau de données
def show_table():
    data = {
        'Timecode': [1, 2, 3, 4, 5],
        'Mesure 1': [2, 4, 6, 8, 10],
        'Mesure 2': [1, 3, 5, 7, 9],
        'Mesure 3': [3, 6, 9, 12, 15],
        'Mesure 4': [4, 8, 12, 16, 20],
        'Mesure 5': [5, 10, 15, 20, 25]
    }

    tree = ttk.Treeview(tab2, columns=tuple(data.keys()), show='headings')
    for col in data.keys():
        tree.heading(col, text=col)
        tree.column(col, width=100)
    for i in range(len(data['Timecode'])):
        tree.insert('', 'end', values=tuple([data[col][i] for col in data.keys()]))
    tree.pack(fill='both', expand=True)


# Fonction pour importer les données au format CSV
def import_from_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        df = pd.read_csv(file_path)
        # Utilisez les données de df pour vos besoins


# Fonction pour exporter les données au format CSV
def export_to_csv():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        data = {
            'Timecode': [1, 2, 3, 4, 5],
            'Mesure 1': [2, 4, 6, 8, 10],
            'Mesure 2': [1, 3, 5, 7, 9],
            'Mesure 3': [3, 6, 9, 12, 15],
            'Mesure 4': [4, 8, 12, 16, 20],
            'Mesure 5': [5, 10, 15, 20, 25]
        }
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)


# Fonction appelée lorsque l'onglet est changé
def on_tab_change(event):
    selected_tab = notebook.index(notebook.select())

    # Affichez le contenu de l'onglet actuellement sélectionné
    if 0 <= selected_tab < len(tab_contents):
        tab_contents[selected_tab].pack()


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
tab_names = ["Graphique", "Tableau de donnée", "Connexion", "paramètres"]

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

# Onglet 1 (contenant le graphique)
tab1 = tabs[0]
show_graph()  # Affichez le graphique dans l'onglet 1

# Contenu pour l'onglet 2
tab2 = tabs[1]
show_table()  # Affichez le graphique dans l'onglet 1

# Contenu pour l'onglet 3
tab3 = tabs[2]
# Bouton d'exportation dans l'onglet 3
export_button = ttk.Button(tab3, text="Exporter en CSV", command=export_to_csv)
export_button.pack()

# Bouton d'importation dans l'onglet 3
import_button = ttk.Button(tab3, text="Importer depuis CSV", command=import_from_csv)
import_button.pack()

# Associez la fonction on_tab_change à l'événement de changement d'onglet
notebook.bind("<<NotebookTabChanged>>", on_tab_change)

# Affichez le contenu initial de l'onglet actuellement sélectionné
on_tab_change(None)  # Utilisez None pour simuler l'appel initial

# Affiche la fenêtre à bonne dimension
root.geometry(f"{1920}x{1080}")

# Démarrez la boucle principale
root.mainloop()
