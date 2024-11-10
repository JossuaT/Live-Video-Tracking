import tkinter as tk

def show_exit_popup(message):
    popup = tk.Tk()
    popup.title("Information")
    popup.geometry("250x80+1000+50")
    label = tk.Label(popup, text=message, font=("Arial", 8))
    label.pack(pady=10)
    
    # Auto-destruction de la fenêtre après 7.5 secondes
    popup.after(5000, popup.destroy)
    popup.mainloop()

show_exit_popup("Appuyer sur ECHAP pour quitter la fenêtre.")