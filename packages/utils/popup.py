import tkinter as tk
from tkinter import messagebox

def ask_question2():
    root = tk.Tk()
    root.withdraw()  # Masquer la fenêtre principale

    reponse = messagebox.askyesno("Question", "Voulez-vous charger l'analyse existante ? \n(Non = suppression de la sauvegarde)")

    return reponse



def ask_question():
    """Affiche une pop-up demandant à l'utilisateur de cliquer sur Oui ou Non.
       Retourne True si Oui, False si Non."""
    
    popup = tk.Tk()
    popup.title("Confirmation")
    popup.resizable(False, False)
    popup.attributes('-topmost', True)

    popup.update_idletasks()  # Met à jour les dimensions
    screen_width, screen_height = popup.winfo_screenwidth(), popup.winfo_screenheight()
    window_width, window_height = 300, 125
    x_position, y_position = (screen_width - window_width) // 2, (screen_height - window_height) // 2
    popup.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    
    result = tk.BooleanVar(value=None)

    # Fonction pour enregistrer la réponse et fermer la fenêtre
    def on_yes():
        result.set(True)
        popup.destroy()
    def on_no():
        result.set(False)
        popup.destroy()

    # Texte principal (grand)
    question_label = tk.Label(popup, text="Voulez-vous charger l'analyse existante ?", font=("Arial", 10, "bold"), )
    question_label.pack(pady=(12, 5))
    # Texte d'information (petit)
    info_label = tk.Label(popup, text="Oui - chargement de l'analyse existante\nNon - suppression de la sauvegarde", font=("Arial", 8))
    info_label.pack(pady=(0, 15))

    # Boutons Oui / Non
    button_frame = tk.Frame(popup)
    button_frame.pack()
    yes_button = tk.Button(button_frame, text="Oui", font=("Arial", 8), width=12, command=on_yes)
    yes_button.pack(side=tk.LEFT, padx=10)
    no_button = tk.Button(button_frame, text="Non", font=("Arial", 8), width=12, command=on_no)
    no_button.pack(side=tk.RIGHT, padx=10)

    popup.mainloop()  # Affichage de la fenêtre

    return result.get()  # Retourne la réponse après la fermeture de la fenêtre