import os
import random
from collections import deque

import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from Gridworld import Gridworld

class GridWorldWrapper:
    """
    Wrapper for Gridworld environment, provides standardized interface for RL interface.
    """
    def __init__(self, size=4, mode='static'):
        self.game = Gridworld(size=size, mode=mode)
        self.size = size
        self.action_map = {0: 'u' , 1: 'd', 2: 'l', 3: 'r'} # 0=up, 1=down, 2=left, 3=right

    def reset(self):
        """ Reset the environment to an initial state """
        self.game = Gridworld(size=self.size, mode="static")
        return self.get_state()

    def get_state(self):
        """ Turn player staet to state index """
        pos = self.game.board.components['Player'].pos
        return pos[0] * self.size + pos[1]
        
    def step(self, action):
        """ Take an action in the environment and return the next state, reward, and done flag """
        # Do Action
        self.game.makeMove(self.action_map[action])
        
        # Get reward
        reward = self.game.reward()

        # Get next state
        next_state = self.get_state()

        # Check if done
        done = (reward == 10 or reward == -10) # Reach goal or fall in pit

        return next_state, reward, done

    def render(self):
        """ Render the current state of the environment """
        print(self.game.display())

class QNetwork(nn.Module):
    """Fully connected Q-network for approximating Q(s, a)."""
    def __init__(self, state_size: int, action_size: int):
        super(QNetwork, self).__init__()
        self.layers = nn.Sequential(
            nn.Linear(state_size, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, action_size)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.layers(x)


class ReplayBuffer:
    """Fixed-capacity experience replay buffer."""
    def __init__(self, capacity: int):
        self.buffer = deque(maxlen=capacity)

    def push(self, state: np.ndarray, action: int, reward: float,
             next_state: np.ndarray, done: bool) -> None:
        """Store a transition."""
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size: int):
        """Randomly sample a batch of transitions."""
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        return (np.array(states), np.array(actions), np.array(rewards),
                np.array(next_states), np.array(dones))

    def __len__(self) -> int:
        return len(self.buffer)


class DQNAgent:
    """Deep Q-Network agent with experience replay and a target network."""
    def __init__(self, state_size: int, action_size: int,
                 learning_rate: float = 0.001,
                 discount_factor: float = 0.95,
                 epsilon: float = 1.0,
                 epsilon_decay: float = 0.995,
                 epsilon_min: float = 0.01,
                 buffer_size: int = 10000,
                 batch_size: int = 32,
                 target_update_freq: int = 100):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Main network (trained every step) and frozen target network
        self.q_network = QNetwork(state_size, action_size).to(self.device)
        self.target_network = QNetwork(state_size, action_size).to(self.device)
        self.target_network.load_state_dict(self.q_network.state_dict())
        self.target_network.eval()

        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)
        self.memory = ReplayBuffer(buffer_size)
        self.step_count = 0  # tracks when to sync target network

    def encode_state(self, state: int) -> np.ndarray:
        """Convert a state index to a one-hot vector."""
        vec = np.zeros(self.state_size, dtype=np.float32)
        vec[state] = 1.0
        return vec

    def select_action(self, state: int) -> int:
        """Epsilon-greedy action selection."""
        if random.random() < self.epsilon:
            return random.randrange(self.action_size)
        state_vec = self.encode_state(state)
        state_tensor = torch.FloatTensor(state_vec).unsqueeze(0).to(self.device)
        with torch.no_grad():
            q_values = self.q_network(state_tensor)
        return int(q_values.argmax(dim=1).item())

    def remember(self, state: int, action: int, reward: float,
                 next_state: int, done: bool) -> None:
        """Store a transition in the replay buffer."""
        self.memory.push(self.encode_state(state), action, reward,
                         self.encode_state(next_state), done)

    def learn(self) -> None:
        """Sample a mini-batch and perform one gradient descent step."""
        if len(self.memory) < self.batch_size:
            return

        states, actions, rewards, next_states, dones = self.memory.sample(self.batch_size)

        states_t = torch.FloatTensor(states).to(self.device)
        actions_t = torch.LongTensor(actions).to(self.device)
        rewards_t = torch.FloatTensor(rewards).to(self.device)
        next_states_t = torch.FloatTensor(next_states).to(self.device)
        dones_t = torch.FloatTensor(dones).to(self.device)

        # Current Q estimates from main network
        current_q = self.q_network(states_t).gather(1, actions_t.unsqueeze(1)).squeeze(1)

        # TD target from frozen target network
        with torch.no_grad():
            max_next_q = self.target_network(next_states_t).max(dim=1)[0]
            target_q = rewards_t + self.discount_factor * max_next_q * (1 - dones_t)

        loss = F.mse_loss(current_q, target_q)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        self.step_count += 1
        if self.step_count % self.target_update_freq == 0:
            self.target_network.load_state_dict(self.q_network.state_dict())

    def decay_epsilon(self) -> None:
        """Decay exploration rate after each episode."""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)


# main function
if __name__ == "__main__":

    # create environment wrapper
    env = GridWorldWrapper(size=4, mode='static')
    # Get state and action space size
    state_size = 16 # 4x4 grid
    action_size = 4 # 4 actions: up, down, left, right

    # Create DQN agent
    agent = DQNAgent(state_size, action_size,
                     learning_rate=0.001,
                     discount_factor=0.95,
                     epsilon=1.0,
                     epsilon_decay=0.995,
                     epsilon_min=0.01,
                     buffer_size=10000,
                     batch_size=32,
                     target_update_freq=100)
    
    print("\n" + "=" * 60)
    print("Test DQN Agent")
    print("=" * 60)

    # ------------------------------------------------------------
    # 1. Test agent create successfully or not
    # ------------------------------------------------------------
    print("\n[Step 1] Check agent basic parameters")
    print("state_size =", agent.state_size)
    print("action_size =", agent.action_size)
    print("learning_rate =", agent.learning_rate)
    print("discount_factor =", agent.discount_factor)
    print("epsilon =", agent.epsilon)
    print("batch_size =", agent.batch_size)
    print("target_update_freq =", agent.target_update_freq)

    # ------------------------------------------------------------
    # 2. Test intial state of the environment
    # ------------------------------------------------------------
    print("\n[Step 2] Get initial state of the environment")
    state = env.reset()
    print("Initial state index =", state)

    # one-hot encode
    state_vector = np.zeros(state_size)
    state_vector[state] = 1
    print("One-hot state =", state_vector)

    # ------------------------------------------------------------
    # 3. Test foward propagation of the q_network
    # ------------------------------------------------------------
    print("\n[Step 3] Test forward pass of the Q-network")
    state_tensor = torch.FloatTensor(state_vector).unsqueeze(0).to(agent.device) # Add batch dimension
    q_values = agent.q_network(state_tensor)

    print("q_values =")
    print(q_values)
    print("q_values shape =", q_values.shape)

    # ------------------------------------------------------------
    # 4. Get the Q values for each action
    # ------------------------------------------------------------
    print("\n[Step 4] Show Q values for each action")
    q_values_np = q_values.cpu().detach().numpy()[0]
    action_names = ['up', 'down', 'left', 'right']

    for i in range(action_size):
        print(f"Action{i} {action_names[i]}: Q = {q_values_np[i]:.4f}")

    best_action = np.argmax(q_values_np)
    print(f"\nCurrent biggest Q value is for action: {best_action} ({action_names[best_action]}))")

    # ------------------------------------------------------------
    # 5. Test target_network same as initial q_network or not
    # ------------------------------------------------------------
    print("\n[Step 5] Check if target network has same initial weights as Q-network")

    same = True
    for param_q, param_target in zip(agent.q_network.parameters(), agent.target_network.parameters()):
        if not torch.equal(param_q.data, param_target.data):
            same = False
            break
    
    print("Two weight networks have same initial weights or not:", same)

    # ------------------------------------------------------------
    # 6. Use target_network to do a forward pass
    # ------------------------------------------------------------
    print("\n[Step 6] Test forward pass of the target_network")
    target_q_values = agent.target_network(state_tensor)
    print("target_q_values =")
    print(target_q_values)

    # ------------------------------------------------------------
    # 7. Compare q_network and target_network outputs same or not
    # ------------------------------------------------------------
    print("\n[Step 7] Compare Q-network and target_network outputs")
    print("Ouputs are the same or not:", torch.allclose(q_values, target_q_values))

    print("\nDQNAgent tests complete!")





