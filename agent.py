import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np
import pygame
import csv
import os
from collections import deque
from env import TetrisEnv
from settings import *

class DQN(nn.Module):
    def __init__(self, input_size):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_size, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 1)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

class Agent:
    def __init__(self, state_size):
        self.state_size = state_size
        self.memory = deque(maxlen=20000)
        self.gamma = 0.99 # CHANGEMENT: 0.99 pour une vision sur le long terme (100 coups d'avance)
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.998
        self.learning_rate = 0.0005
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.model = DQN(state_size).to(self.device)
        self.target_model = DQN(state_size).to(self.device)
        self.update_target_network() 

        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        # CHANGEMENT: Huber Loss (amortisseur pour les grosses récompenses comme +300)
        self.criterion = nn.SmoothL1Loss() 

    def update_target_network(self):
        self.target_model.load_state_dict(self.model.state_dict())

    def save(self, filename):
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'epsilon': self.epsilon
        }, filename)

    def load(self, filename):
        if os.path.isfile(filename):
            checkpoint = torch.load(filename, weights_only=True)
            try:
                self.model.load_state_dict(checkpoint['model_state_dict'])
                self.epsilon = checkpoint['epsilon']
                self.update_target_network()
                print(f"✅ Mémoire restaurée ! Epsilon actuel : {self.epsilon:.2f}")
            except RuntimeError:
                print("⚠️ Architecture du réseau modifiée. Nouvel apprentissage !")
        else:
            print("⚠️ Aucun fichier de sauvegarde trouvé. Nouvel apprentissage !")

    def act(self, possible_states):
        if not possible_states:
            return None
            
        if np.random.rand() <= self.epsilon:
            return random.choice(list(possible_states.keys()))
            
        best_value = -float('inf')
        best_action = None
        
        with torch.no_grad():
            for action, state in possible_states.items():
                state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
                value = self.model(state_tensor).item()
                
                if value > best_value:
                    best_value = value
                    best_action = action
                    
        return best_action

    def remember(self, state, reward, next_state, done):
        self.memory.append((state, reward, next_state, done))

    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return
        minibatch = random.sample(self.memory, batch_size)
        
        states = torch.FloatTensor(np.array([t[0] for t in minibatch])).to(self.device)
        rewards = torch.FloatTensor(np.array([t[1] for t in minibatch], dtype=np.float32)).unsqueeze(1).to(self.device)
        next_states = torch.FloatTensor(np.array([t[2] for t in minibatch])).to(self.device)
        dones = torch.FloatTensor(np.array([t[3] for t in minibatch], dtype=np.float32)).unsqueeze(1).to(self.device)
        
        current_q_values = self.model(states)
        
        with torch.no_grad():
            next_q_values = self.target_model(next_states)
            
        targets = rewards + (self.gamma * next_q_values * (1 - dones))
        
        self.optimizer.zero_grad()
        loss = self.criterion(current_q_values, targets)
        loss.backward()
        self.optimizer.step()
            

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("IA Tetris")
    
    env = TetrisEnv()
    state_size = 12 
    agent = Agent(state_size)
    batch_size = 512
    episodes = 500000
    
    model_file = "tetris_ai_model.pth"
    best_model_file = "tetris_ai_model_BEST.pth" # Le coffre-fort !
    agent.load(model_file)
    
    best_score = 0
    
    MODE_TEST = False 
    if MODE_TEST:
        agent.epsilon = 0.00
        print("🚨 MODE TEST ACTIVÉ : L'IA joue sérieusement, aucune sauvegarde ne sera faite.")
    
    log_file = "training_log.csv"
    file_exists = os.path.isfile(log_file)
    with open(log_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Episode", "Score", "Total_Reward", "Pieces_Placed", "Epsilon"])



    for e in range(episodes):
        env.reset()
        done = False
        total_reward = 0
        
        possible_states = env.get_possible_states()
        
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if not MODE_TEST: 
                        agent.save(model_file)
                    pygame.quit()
                    exit()

            if not possible_states:
                break 

            # 1. On choisit l'action et on enregistre l'état *avec* ses lignes visibles !
            action = agent.act(possible_states)
            current_state_features = possible_states[action]
            
            # 2. On exécute l'action dans le jeu
            _, reward, done = env.step(action)
            total_reward += reward
            
            # 3. Double DQN : On anticipe le prochain état en utilisant notre cerveau actuel
            if not done:
                next_possible_states = env.get_possible_states()
                if next_possible_states:
                    next_action = agent.act(next_possible_states)
                    next_state_features = next_possible_states[next_action]
                else:
                    next_state_features = np.zeros(agent.state_size, dtype=np.float32)
            else:
                next_state_features = np.zeros(agent.state_size, dtype=np.float32)
                next_possible_states = None
            
            # 4. On stocke la transition parfaite
            agent.remember(current_state_features, reward, next_state_features, done)
            
            if e % 20 == 0:
                env.render(screen)
                
            agent.replay(batch_size) 
            possible_states = next_possible_states
            
        if done:
            if agent.epsilon > agent.epsilon_min:
                agent.epsilon *= agent.epsilon_decay
            
            print(f"Episode: {e}/{episodes}, Score: {env.game.score}, Pieces: {env.pieces_placed}, Reward: {total_reward:.1f}, Epsilon: {agent.epsilon:.2f}")
            
            with open(log_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([e, env.game.score, round(total_reward, 1), env.pieces_placed, round(agent.epsilon, 3)])

            if env.game.score > best_score:
                    best_score = env.game.score
                    # On sauvegarde cette version précise dans un fichier à part !
                    agent.save(best_model_file)
                    print(f"🏆 NOUVEAU RECORD ABSOLU : {best_score} points ! Modèle champion sauvegardé !")
                
            # (Ton ancienne sauvegarde régulière tous les 50 épisodes peut rester pour l'historique)
            if e % 50 == 0:
                agent.update_target_network()
                if not MODE_TEST:
                    agent.save(model_file)
            break