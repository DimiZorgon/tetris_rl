import os
import numpy as np
import pygame
import onnxruntime as ort
from env import TetrisEnv
from settings import *

# On importe PyTorch et la classe DQN uniquement pour la conversion initiale
import torch
from agent import DQN

def convert_pth_to_onnx(pth_path, onnx_path, state_size):
    """
    Charge le modèle PyTorch et le convertit au format ONNX s'il n'existe pas déjà.
    """
    if os.path.exists(onnx_path):
        print(f"✅ Le fichier {onnx_path} existe déjà. Conversion ignorée.")
        return

    print(f"🔄 Conversion de {pth_path} vers {onnx_path} en cours...")
    
    # 1. Initialiser le modèle (toujours sur CPU pour l'export)
    model = DQN(state_size)
    
    # 2. Charger les poids (en s'assurant qu'on mappe sur le CPU)
    checkpoint = torch.load(pth_path, map_location=torch.device('cpu'), weights_only=True)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval() # Mode évaluation (très important pour l'inférence)

    # 3. Créer un tenseur "factice" de la bonne taille pour tracer le graphe du réseau
    dummy_input = torch.randn(1, state_size)

    # 4. Exporter le modèle
    torch.onnx.export(
        model, 
        dummy_input, 
        onnx_path, 
        export_params=True,
        opset_version=14, # Version standard stable
        do_constant_folding=True, 
        input_names=['state_input'], 
        output_names=['q_value']
    )
    print("✅ Modèle converti avec succès au format ONNX !")

def get_best_action_onnx(session, possible_states):
    """
    Évalue les états possibles via le NPU (ONNX) et retourne la meilleure action.
    """
    if not possible_states:
        return None
        
    best_value = -float('inf')
    best_action = None
    input_name = session.get_inputs()[0].name
    
    # Évaluation de chaque état possible généré par l'environnement
    for action, state in possible_states.items():
        # Formatage de l'état pour ONNX : Tableau Numpy 2D (1, state_size) en Float32
        state_array = np.array(state, dtype=np.float32).reshape(1, -1)
        
        # Exécution du modèle via ONNX Runtime
        ort_outputs = session.run(None, {input_name: state_array})
        value = ort_outputs[0][0][0] # On extrait la Q-value (un seul nombre)
        
        if value > best_value:
            best_value = value
            best_action = action
            
    return best_action

def play_game(onnx_path):
    """
    Lance le jeu Tetris en utilisant le modèle ONNX.
    """
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Tetris NPU Champion")
    
    env = TetrisEnv()
    
    # Configuration de la session ONNX Runtime
    # L'ordre de la liste est important : il tente d'abord le NPU (QNN), puis le CPU en secours
    providers = ['QNNExecutionProvider', 'CPUExecutionProvider']
    
    print("🚀 Démarrage de la session ONNX Runtime...")
    try:
        session = ort.InferenceSession(onnx_path, providers=providers)
        active_provider = session.get_providers()[0]
        print(f"🧠 Exécution propulsée par : {active_provider}")
    except Exception as e:
        print(f"❌ Erreur lors du chargement de la session ONNX : {e}")
        return

    # Boucle de jeu (similaire au mode RENDER_GAME de ton main)
    clock = pygame.time.Clock()
    fps = 60 # Ajuste pour voir le jeu plus ou moins vite
    
    env.reset()
    done = False
    
    print("🎮 Début de la partie !")
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        possible_states = env.get_possible_states()
        if not possible_states:
            break

        # Demander au NPU la meilleure action
        action = get_best_action_onnx(session, possible_states)
        
        # Appliquer l'action dans l'environnement
        _, _, done = env.step(action)
        
        # Affichage
        env.render(screen)
        clock.tick(fps)
        
    print(f"🏁 Partie terminée ! Score final : {env.game.score} | Pièces placées : {env.pieces_placed}")
    pygame.quit()

if __name__ == "__main__":
    STATE_SIZE = 12
    # Utilise ton meilleur modèle sauvegardé
    PTH_MODEL_FILE = "tetris_ai_model_BEST.pth" 
    ONNX_MODEL_FILE = "tetris_agent_optimized.onnx"

    # Étape 1 : Conversion automatique si nécessaire
    if os.path.exists(PTH_MODEL_FILE):
        convert_pth_to_onnx(PTH_MODEL_FILE, ONNX_MODEL_FILE, STATE_SIZE)
        # Étape 2 : Lancer le jeu avec le NPU
        play_game(ONNX_MODEL_FILE)
    else:
        print(f"⚠️ Fichier introuvable : {PTH_MODEL_FILE}. Entraîne d'abord ton agent !")