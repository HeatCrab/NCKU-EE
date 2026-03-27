import os
import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import random
from collections import deque
from Gridworld import Gridworld

class SARSAAgent:
    def __init__(self, state_size, action_size, learning_rate=0.01, discount_factor=0.95, epsilon=1.0, epsilon_decay=0.995, epsilon_min=0.01):
        """
        SARSA (State-Action-Reward-State-Action) agent.

        On-policy TD control that updates Q-values using the actual
        next action chosen by the current policy.

        Parameters:
        - state_size: The size of the state space
        - action_size: The size of the action space
        - learning_rate: Learning rate (alpha)
        - discount_factor: Discount factor (gamma)
        - epsilon: Exploration rate
        - epsilon_decay: Decay rate for epsilon
        - epsilon_min: Minimum value for epsilon
        """       
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min

        # Initialize Q-table
        self.q_table = np.zeros((state_size, action_size))
    
    def get_action(self, state):
        """ 
        Select an action using epsilon-greedy policy.
        """
        if random.uniform(0, 1) < self.epsilon:
            # Explore: select a random action
            return random.randrange(self.action_size)
        else:
            # Exploit: select the action with max Q-value
            return np.argmax(self.q_table[state])
        
    def update_q_table(self, state, action, reward, next_state, next_action, done):
        """
        Update the Q-table using SARSA update rule.
        Q(s, a) = Q(s, a) + alpha * (reward + gamma * Q(s', a') - Q(s, a))
        """
        current_q = self.q_table[state, action]

        if done:
            # If it is terminal state, the Q value of the next state is 0
            target_q = reward
        else:
            # Use the actual next action's Q-value, not the max
            target_q = reward + self.discount_factor * self.q_table[next_state, next_action]

        # Update Q-value
        self.q_table[state, action] = current_q + self.learning_rate * (target_q - self.q_table[state, action])

    def decay_epsilon(self):
        """
        Decay the exploration rate
        """
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

class GridWorldWrapper:
    """
    Gridworld environment wrapper to interface with SARSA agent.
    """

    def __init__(self, size=4, mode='static'):
        self.game = Gridworld(size=size, mode=mode)
        self.size = size
        self.action_map = {0: 'u', 1: 'd', 2: 'l', 3: 'r'}  # 0 = up, 1 = down, 2 = left, 3 = right
    
    def reset(self):
        """ Reset the environment and return the initial state. """
        self.game = Gridworld(size=self.size, mode='static')
        return self.get_state()
    
    def get_state(self):
        """ Get the agent's current position and turn out to the state representation. """
        pos = self.game.board.components['Player'].pos
        return pos[0] * self.size + pos[1]
    
    def step(self, action):
        """ Take an action in the environment and return the new state, reward, and done flag. """
        # Take the action
        self.game.makeMove(self.action_map[action])

        # Get the reward
        reward = self.game.reward()
        
        # Get the new state
        new_state = self.get_state()

        # Check if the episode is done
        done = (reward == 10 or reward == -10) # Reach the goal or hit the trap

        return new_state, reward, done
    
    def render(self):
        """ Render the current state of the environment. """
        print(self.game.display())

def train_sarsa(episodes, max_steps=200):

    # Initialize the environment(mode='static' object, trap and wall positions are fixed per episode)
    env = GridWorldWrapper(size=4, mode='static')

    # Get the state size and action size
    state_size = 16 # 4x4 grid
    action_size = 4 # up, down, left, right four actions

    # Create the Agent
    agent = SARSAAgent(state_size, action_size)

    scores = []
    epsilons = []

    print("Starting training SARSA agent...")
    print("Initial environment:")
    env.render()

    for episode in range(episodes):
        state = env.reset()
        action = agent.get_action(state) # SARSA: select the first action
        total_reward = 0
        steps = 0

        for step in range(max_steps):
            # Take the action
            next_state, reward, done = env.step(action)

            if done:
                # Terminal state, no next action
                agent.update_q_table(state, action, reward, next_state, None, done)
            else:
                # SARSA: select the next action
                next_action = agent.get_action(next_state)
                # Use next action to update Q-table
                agent.update_q_table(state, action, reward, next_state, next_action, done)
                # Update action
                action = next_action
            
            state = next_state
            total_reward += reward
            steps += 1

            if done:
                break

        # Decay exploration rate
        agent.decay_epsilon()

        # Record results
        scores.append(total_reward)
        epsilons.append(agent.epsilon)

        if (episode + 1) % 100 == 0:
            avg_score = np.mean(scores[-100:])
            print(f'Episode: {episode + 1}, Average Score: {avg_score:.2f}, Epsilon: {agent.epsilon:.4f}')

    # Final training metrics
    final_avg_score = np.mean(scores[-100:])
    print(f'\nTraining complete!')
    print(f'Average score of last 100 episodes: {final_avg_score:.2f}')
    print(f'Final epsilon: {agent.epsilon:.4f}')

    # Convergence assessment
    if final_avg_score > 0:
        print('Agent has converged: achieving positive average reward.')
    else:
        print('Agent has not fully converged. Consider more training episodes.')

    return agent, scores, epsilons, env


def  analyze_environment(env):
    """ 
    Analyze the environment Setup
    """

    print("Analyzing the environment:")
    print("-" * 30)
    player_pos = env.game.board.components['Player'].pos
    goal_pos = env.game.board.components['Goal'].pos
    pit_pos = env.game.board.components['Pit'].pos
    wall_pos = env.game.board.components['Wall'].pos

    print(f"Player Position: {player_pos} (State: {player_pos[0] * 4 + player_pos[1]})")
    print(f"Goal Position: {goal_pos} (State: {goal_pos[0] * 4 + goal_pos[1]})")
    print(f"Trap Position: {pit_pos} (State: {pit_pos[0] * 4 + pit_pos[1]})")
    print(f"Wall Position: {wall_pos} (State: {wall_pos[0] * 4 + wall_pos[1]})")
    print()

def visualize_results(scores, epsilons):
    """ 
    Visualize the training results
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Plot scores convergence
    ax1.plot(scores)
    ax1.set_title('Training Scores')
    ax1.set_xlabel('Episode')
    ax1.set_ylabel('Score')
    ax1.grid(True)

    # Caculate moving average
    window_size = 100
    if len(scores) >= window_size:
        moving_avg = np.convolve(scores, np.ones(window_size)/window_size, mode='valid')
        ax1.plot(range(window_size - 1, len(scores)), moving_avg, label='Moving Average (100 episodes)', color='orange')
        ax1.legend()

    # Plot epsilon decay curve
    ax2.plot(epsilons)
    ax2.set_title('Epsilon Decay')
    ax2.set_xlabel('Episode')
    ax2.set_ylabel('Epsilon')
    ax2.grid(True)

    plt.tight_layout()
    os.makedirs('results', exist_ok=True)
    plt.savefig('results/training_results.png')
    plt.close()


def test_agent(agent, env, num_episodes=10, max_steps=200):
    """
    Test the trained agent with pure exploitation (epsilon=0).

    Args:
        agent: Trained SARSAAgent
        env: GridWorldWrapper environment
        num_episodes: Number of test episodes
        max_steps: Maximum steps per episode

    Returns:
        List of test scores
    """
    test_scores = []

    print("\n" + "=" * 50)
    print("Testing trained agent (epsilon = 0)")
    print("=" * 50)

    for episode in range(num_episodes):
        state = env.reset()
        total_score = 0
        path = [state]

        for step in range(max_steps):
            # Pure exploitation: always pick the best action
            action = np.argmax(agent.q_table[state])
            next_state, reward, done = env.step(action)

            path.append(next_state)
            total_score += reward
            state = next_state

            if done:
                break

        test_scores.append(total_score)
        result = "Goal!" if reward == 10 else "Pit!" if reward == -10 else "Timeout"
        print(f'Test Episode {episode + 1}: Score = {total_score:.1f}, '
              f'Steps = {len(path) - 1}, Result = {result}, Path = {path}')

    avg_test_score = np.mean(test_scores)
    print(f'\nAverage test score: {avg_test_score:.2f}')
    return test_scores


def demonstrate_learned_policy(agent, env):
    """
    Demonstrate the learned policy with step-by-step walkthrough.

    Args:
        agent: Trained SARSAAgent
        env: GridWorldWrapper environment
    """
    action_names = {0: 'Up', 1: 'Down', 2: 'Left', 3: 'Right'}

    print("\n" + "=" * 50)
    print("Demonstrating learned policy")
    print("=" * 50)

    state = env.reset()
    env.render()

    for step in range(200):
        action = np.argmax(agent.q_table[state])
        q_values = agent.q_table[state]
        print(f'Step {step + 1}: State {state}, '
              f'Q-values = {np.round(q_values, 2)}, '
              f'Action = {action_names[action]}')

        next_state, reward, done = env.step(action)
        env.render()
        print(f'Reward: {reward}')

        state = next_state
        if done:
            result = "reached the Goal!" if reward == 10 else "fell into the Pit!"
            print(f'\nAgent {result}')
            break


def visualize_policy(agent, env):
    """
    Visualize the learned policy with directional arrows and state values.

    Args:
        agent: Trained SARSAAgent
        env: GridWorldWrapper environment
    """
    size = env.size
    action_arrows = {0: '\u2191', 1: '\u2193', 2: '\u2190', 3: '\u2192'}  # ↑ ↓ ← →

    # Get special positions
    goal_pos = env.game.board.components['Goal'].pos
    pit_pos = env.game.board.components['Pit'].pos
    wall_pos = env.game.board.components['Wall'].pos

    goal_state = goal_pos[0] * size + goal_pos[1]
    pit_state = pit_pos[0] * size + pit_pos[1]
    wall_state = wall_pos[0] * size + wall_pos[1]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Policy visualization with arrows
    ax1.set_title('Learned Policy (SARSA)')
    ax1.set_xlim(-0.5, size - 0.5)
    ax1.set_ylim(-0.5, size - 0.5)
    ax1.set_xticks(range(size))
    ax1.set_yticks(range(size))
    ax1.grid(True)
    ax1.invert_yaxis()

    for s in range(size * size):
        row, col = s // size, s % size
        if s == goal_state:
            ax1.text(col, row, '+', ha='center', va='center', fontsize=20, color='green', fontweight='bold')
        elif s == pit_state:
            ax1.text(col, row, '-', ha='center', va='center', fontsize=20, color='red', fontweight='bold')
        elif s == wall_state:
            ax1.add_patch(plt.Rectangle((col - 0.5, row - 0.5), 1, 1, color='gray', alpha=0.5))
            ax1.text(col, row, 'W', ha='center', va='center', fontsize=14, color='white', fontweight='bold')
        else:
            best_action = np.argmax(agent.q_table[s])
            ax1.text(col, row, action_arrows[best_action], ha='center', va='center', fontsize=20)

    # State values (max Q-value per state)
    ax2.set_title('State Values (max Q)')
    state_values = np.max(agent.q_table, axis=1).reshape(size, size)
    im = ax2.imshow(state_values, cmap='RdYlGn', interpolation='nearest')
    plt.colorbar(im, ax=ax2)

    for row in range(size):
        for col in range(size):
            s = row * size + col
            if s == wall_state:
                ax2.text(col, row, 'W', ha='center', va='center', fontsize=12, fontweight='bold')
            else:
                ax2.text(col, row, f'{state_values[row, col]:.1f}',
                         ha='center', va='center', fontsize=10)

    plt.tight_layout()
    os.makedirs('results', exist_ok=True)
    plt.savefig('results/policy_visualization.png')
    plt.close()
    print("Policy visualization saved to results/policy_visualization.png")


# Main
if __name__ == "__main__":

    # Train agent
    agent, scores, epsilons, env = train_sarsa(episodes=1000)

    # Visualize training results
    visualize_results(scores, epsilons)

    # Analyze environment
    analyze_environment(env)

    # Visualize learned policy
    visualize_policy(agent, env)

    # Test the trained agent
    test_agent(agent, env)

    # Demonstrate the learned policy step by step
    demonstrate_learned_policy(agent, env)