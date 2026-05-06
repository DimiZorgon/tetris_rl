import pandas as pd
import matplotlib.pyplot as plt

# Lecture du fichier CSV
try:
    data = pd.read_csv("training_log.csv")
except FileNotFoundError:
    print("Le fichier training_log.csv n'existe pas encore. Lance l'entraînement d'abord !")
    exit()

# Création d'une figure avec 3 sous-graphiques
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))

# Graphique 1 : L'évolution du Score (On ajoute une moyenne lissante sur 10 épisodes pour y voir plus clair)
ax1.plot(data["Episode"], data["Score"], alpha=0.3, color='blue', label='Score Brut')
ax1.plot(data["Episode"], data["Score"].rolling(window=10).mean(), color='darkblue', linewidth=2, label='Moyenne (10 épisodes)')
ax1.set_title("Évolution du Score")
ax1.set_ylabel("Score")
ax1.legend()
ax1.grid(True)

# Graphique 2 : L'évolution de la Récompense Totale
ax2.plot(data["Episode"], data["Total_Reward"], alpha=0.3, color='green', label='Reward Brute')
ax2.plot(data["Episode"], data["Total_Reward"].rolling(window=10).mean(), color='darkgreen', linewidth=2, label='Moyenne (10 épisodes)')
ax2.set_title("Évolution de la Récompense Totale")
ax2.set_ylabel("Total Reward")
ax2.legend()
ax2.grid(True)

# Graphique 3 : Nombre de pièces placées vs Epsilon
ax3.plot(data["Episode"], data["Pieces_Placed"], color='purple', label='Pièces placées')
ax3.set_ylabel("Nombre de pièces", color='purple')
ax3.tick_params(axis='y', labelcolor='purple')

ax3_twin = ax3.twinx() # Ajoute un 2ème axe Y à droite
ax3_twin.plot(data["Episode"], data["Epsilon"], color='red', linestyle='--', label='Epsilon (Exploration)')
ax3_twin.set_ylabel("Epsilon", color='red')
ax3_twin.tick_params(axis='y', labelcolor='red')

ax3.set_title("Durée de survie (Pièces) vs Taux d'exploration (Epsilon)")
ax3.set_xlabel("Épisodes")
ax3.grid(True)

plt.tight_layout()
plt.show()