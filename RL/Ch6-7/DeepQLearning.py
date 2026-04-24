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

class DQN(nn.Module):
    """Deep Q-Network neural network model"""
    def __init__(self, state_size, action_size, hidden_size):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(state_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, action_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

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
                 target_update_freq: int = 100,
                 hidden_size: int = 64):
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
        self.q_network = DQN(state_size, action_size, hidden_size).to(self.device)
        self.target_network = DQN(state_size, action_size, hidden_size).to(self.device)
        self.target_network.load_state_dict(self.q_network.state_dict())
        self.target_network.eval()

        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)
        self.memory = ReplayBuffer(buffer_size)
        self.steps = 0

    def encode_state(self, state: int) -> np.ndarray:
        """Convert a state index to a one-hot vector."""
        vec = np.zeros(self.state_size, dtype=np.float32)
        vec[state] = 1.0
        return vec

    def _states_to_matrix(self, states) -> np.ndarray:
        """Convert a list of state indices to a matrix of one-hot vectors."""
        matrix = np.zeros((len(states), self.state_size), dtype=np.float32)
        for i, s in enumerate(states):
            matrix[i][s] = 1.0
        return matrix

    def select_action(self, state: int) -> int:
        """Epsilon-greedy action selection."""
        if random.random() < self.epsilon:
            return random.randrange(self.action_size)
        state_tensor = torch.FloatTensor(self.encode_state(state)).unsqueeze(0).to(self.device)
        with torch.no_grad():
            q_values = self.q_network(state_tensor)
        return int(q_values.argmax(dim=1).item())

    def remember(self, state: int, action: int, reward: float,
                 next_state: int, done: bool) -> None:
        """Store a transition in the replay buffer."""
        self.memory.push(state, action, reward, next_state, done)

    def learn(self) -> None:
        """Sample a mini-batch and perform one gradient descent step."""
        if len(self.memory) < self.batch_size:
            return

        # Smapling from buffer
        states, actions, rewards, next_states, dones = self.memory.sample(self.batch_size)

        # turn to tensors
        states = torch.FloatTensor(self._states_to_matrix(states)).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(self._states_to_matrix(next_states)).to(self.device)
        dones = torch.BoolTensor(dones).to(self.device)

        # Compute current Q values
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1))

        # Compute target Q values (detach() is to prvent backprop through target network,
        # which is the main point of DQN algorithm design)
        next_q_values = self.target_network(next_states).max(1)[0].detach()

        # Bellman equation: Q*(s, a) = R(s, a) + gamma * max Q*(s', a')
        # dones == True (~dones == false) no future reward if game ends,
        # no consideration of next_q_values, set to 0
        target_q_values = rewards + (self.discount_factor * next_q_values * ~dones)

        # Calculate loss by shorten the distance between current q_values prediction and real q_values,
        # (squeeze() is to turn redundant dimension in Tensor, which is the result of gather() function, back to original shape)
        loss = F.mse_loss(current_q_values.squeeze(), target_q_values)

        # Backpropagation and optimization step
        # self.optimizer.zero_grad() is to clear the gradients of all optimized tensors before backpropagation,
        # which is necessary in Pytorch taining
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Update step
        self.steps += 1

        # Update target network regularly (default every 100 steps)
        if self.steps % self.target_update_freq == 0:
            # self.q_network.state_dict() extracts all weights and biases from the main network
            # self.target_network.load_state_dict() reloads the weights into the target network
            self.target_network.load_state_dict(self.q_network.state_dict())

    def decay_epsilon(self) -> None:
        """Decay exploration rate after each episode."""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)


def train_dqn(num_episodes=1000, max_steps=200):
    """
    Train DQN agent
    """
    env = GridWorldWrapper(size=4, mode='static')
    agent = DQNAgent(state_size=16, action_size=4)

    scores = []
    epsilons = []

    for episode in range(num_episodes):
        state = env.reset()
        total_reward = 0

        for _ in range(max_steps):
            action = agent.select_action(state)
            next_state, reward, done = env.step(action)
            agent.remember(state, action, reward, next_state, done)
            agent.learn()
            state = next_state
            total_reward += reward
            if done:
                break

        agent.decay_epsilon()
        scores.append(total_reward)
        epsilons.append(agent.epsilon)

        if (episode + 1) % 100 == 0:
            avg = np.mean(scores[-100:])
            print(f"Episode {episode+1}/{num_episodes}, Avg Score: {avg:.1f}, Epsilon: {agent.epsilon:.3f}")

    return agent, scores, epsilons, env


def test_agent(agent, env, epsilons=5):
    temp_epsilon = agent.epsilon
    agent.epsilon = 0
    test_scores = []

    for _ in range(epsilons):
        state = env.reset()
        total_reward = 0
        steps = 0
        path = [state]

        for _ in range(200):
            action = agent.select_action(state)
            next_state, reward, done = env.step(action)

            state = next_state
            total_reward += reward
            steps += 1
            path.append(state)

            if done:
                break

        # recover original epsilon
        agent.epsilon = temp_epsilon

        test_scores.append(total_reward)
        print(f"Final State")
        env.render()
        print(f"Score = {total_reward}, Steps = {steps}")
        print(f"Path: {' -> '.join(map(str, path))}")

    print(f"\nAverage Test Score: {np.mean(test_scores):.2f}")
    return test_scores


def analyze_environment(env):
    print("\n" + "=" * 60)
    print("Environment Analysis")
    print("=" * 60)
    print(f"Grid size: {env.size}x{env.size}")
    print(f"State space: {env.size ** 2} states")
    print(f"Action space: {len(env.action_map)} actions {list(env.action_map.values())}")
    env.reset()
    env.render()


def visualize_results(scores, epsilons):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    ax1.plot(scores, alpha=0.6, color='blue')
    window = 100
    if len(scores) >= window:
        moving_avg = np.convolve(scores, np.ones(window) / window, mode='valid')
        ax1.plot(range(window - 1, len(scores)), moving_avg, color='red',
                 label=f'Moving Average ({window})')
        ax1.legend()
    ax1.set_title('DQN Training Scores')
    ax1.set_xlabel('Episode')
    ax1.set_ylabel('Score')

    ax2.plot(epsilons, color='blue')
    ax2.set_title('Epsilon Decay')
    ax2.set_xlabel('Episode')
    ax2.set_ylabel('Epsilon')

    plt.tight_layout()
    plt.savefig('dqn_results.png')
    plt.show()


def print_q_values(agent):
    print("\n" + "=" * 60)
    print("Q-Values for each state")
    print("=" * 60)
    action_names = ['up', 'down', 'left', 'right']
    for state in range(agent.state_size):
        state_tensor = torch.FloatTensor(agent.encode_state(state)).unsqueeze(0).to(agent.device)
        with torch.no_grad():
            q_vals = agent.q_network(state_tensor).cpu().numpy()[0]
        best = int(np.argmax(q_vals))
        print(f"State {state:2d}: {[f'{q:.2f}' for q in q_vals]} -> {action_names[best]}")


def print_policy(agent):
    print("\n" + "=" * 60)
    print("Policy (best action per state)")
    print("=" * 60)
    action_symbols = {0: '↑', 1: '↓', 2: '←', 3: '→'}
    size = int(agent.state_size ** 0.5)
    for row in range(size):
        line = ''
        for col in range(size):
            state = row * size + col
            state_tensor = torch.FloatTensor(agent.encode_state(state)).unsqueeze(0).to(agent.device)
            with torch.no_grad():
                q_vals = agent.q_network(state_tensor)
            action = int(q_vals.argmax().item())
            line += action_symbols[action] + ' '
        print(line)


def print_state_values(agent):
    print("\n" + "=" * 60)
    print("State Values (max Q-value per state)")
    print("=" * 60)
    size = int(agent.state_size ** 0.5)
    for row in range(size):
        line = ''
        for col in range(size):
            state = row * size + col
            state_tensor = torch.FloatTensor(agent.encode_state(state)).unsqueeze(0).to(agent.device)
            with torch.no_grad():
                q_vals = agent.q_network(state_tensor)
            value = float(q_vals.max().item())
            line += f'{value:6.2f} '
        print(line)


# main function
if __name__ == "__main__":

    print("=" * 60)
    print("Train DQN (Deep Q-Network) Gridworld")
    print("=" * 60)

    # Train DQN agent
    agent, scores, epsilons, env = train_dqn(num_episodes=1000)

    # Analyze environment
    analyze_environment(env)

    # Visualize results
    visualize_results(scores, epsilons)

    # print q_values and strategy
    print_q_values(agent)
    print_policy(agent)
    print_state_values(agent)

    # Test trained agent
    test_score = test_agent(agent, env, epsilons=5)
