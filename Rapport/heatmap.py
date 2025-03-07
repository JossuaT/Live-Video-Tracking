# Rapport/heatmap.py
import matplotlib.pyplot as plt

def generate_heatmap(positions, title="Heatmap", bins=50, field_size=None):
    """
    Génère et affiche une heatmap des positions.
    
    :param positions: Liste de tuples (x, y) représentant les positions.
    :param title: Titre de la heatmap.
    :param bins: Nombre de bins pour l'histogramme 2D.
    :param field_size: Optionnel, tuple (largeur, hauteur) pour fixer l'étendue de l'axe.
    """
    if not positions:
        print("Aucune position à afficher pour", title)
        return

    x_coords, y_coords = zip(*positions)
    plt.figure(figsize=(8,6))
    if field_size:
        plt.xlim(0, field_size[0])
        plt.ylim(0, field_size[1])
    plt.hist2d(x_coords, y_coords, bins=bins, cmap='hot')
    plt.title(title)
    plt.xlabel("Position X")
    plt.ylabel("Position Y")
    plt.colorbar(label='Nombre de détections')
    plt.show()