import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Fonction pour créer et afficher le graphique
def show_graph():
    x = np.linspace(0, 2 * np.pi, 100)
    y = np.sin(x)

    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_xlabel("X-Axis")
    ax.set_ylabel("Y-Axis")
    ax.set_title("Graphique Sinus")

    canvas = FigureCanvasTkAgg(fig, master=tab1)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

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
tab_names = ["Onglet 1", "Onglet 2", "Onglet 3"]

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
content2 = tk.Label(tabs[1], text="Contenu de l'Onglet 2")
tab_contents.append(content2)

# Contenu pour l'onglet 3
content3 = tk.Label(tabs[2], text="Contenu de l'Onglet 3")
tab_contents.append(content3)

# Associez la fonction on_tab_change à l'événement de changement d'onglet
notebook.bind("<<NotebookTabChanged>>", on_tab_change)

# Affichez le contenu initial de l'onglet actuellement sélectionné
on_tab_change(None)  # Utilisez None pour simuler l'appel initial

# Affiche la fenêtre à bonne dimension
root.geometry(f"{1366}x{720}")

# Démarrez la boucle principale
root.mainloop()
