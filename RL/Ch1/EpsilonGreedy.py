import numpy as np
import matplotlib.pyplot as plt
import random
from typing import List, Tuple

class MultiArmedBandit:
    ''' Multi-armed bandit environment '''

    def __init__(self, k: int = 10, true_rewards: List[float] = None):
        '''
        Initializes a multi-armed bandit 
        
        Args:
            k: Number of arms in the bandit
            true_rewards: List of true rewards for each arm. If None, rewards are randomly generated. 
        '''
        self.k = k
        
        if true_rewards is None:
            # Randomly generate expectation for each arm
            self.true_rewards = np.random.normal(0, 1, k)
        else:
            self.true_rewards = np.array(true_rewards)

        self.optimal_arm = np.argmax(self.true_rewards)
        self.optimal_reward = self.true_rewards[self.optimal_arm]
    

    def pull_arm(self, arm: int) -> float:
        '''
        Pull the specified arm and return the reward

        Args:
            arm: The index of the arm to pull
        
        Returns:
            The reward obtained from pulling the arm
        '''
        # The reward is drawn from a normal distribution with mean 
        # equal to the true_rewards[arm] and standard deviation of 1        # 
        reward = np.random.normal(self.true_rewards[arm], 1)
        return reward
    
class EpsilonGreedyAgent:
    ''' Epsilon-greedy strategy agent '''

    def __init__(self, k: int, epsilon: float = 0.1):
        '''
        Initializes an epsilon-greedy agent
        
        Args:
            k: Number of arms in the bandit
            epsilon: Probability of choosing a random arm (exploration)
        '''
        self.k = k
        self.epsilon = epsilon
        self.action_counts = np.zeros(k)  # Count of pulls for each arm
        self.q_estimates = np.zeros(k)  # Estimated value of each arm
        self.total_reward = 0
        self.total_steps = 0
    
    def select_action(self) -> int:
        '''
        Select an action using epsilon-greedy strategy
        
        Returns:
            The index of the selected arm
        '''
        if random.random() < self.epsilon:
            # Explore: choose a random arm
            return random.randint(0, self.k - 1)
        else:
            # Exploit: choose the arm with the highest estimated value
            return np.argmax(self.q_estimates)
        
    def update(self, action: int, reward: float):
        '''
        Update the estimated value 

        Args:
            action: The action that was selected
            reward: The reward received from pulling the arm
        '''
        self.action_counts[action] += 1
        self.total_steps += 1
        self.total_reward += reward

        # Use incremental update the formula
        n = self.action_counts[action]
        self.q_estimates[action] += (reward - self.q_estimates[action]) / n

def run_experiment(bandit: MultiArmedBandit, agent: EpsilonGreedyAgent, steps: int
                    ) -> Tuple[List[float], List[float], List[int]]:
    '''
    Run a single experiment with the given bandit and agent

    Args:
        bandit: The multi-armed bandit environment
        agent: The epsilon-greedy agent
        steps: Number of steps to run

    Returns:
        Tuple of (rewards_history, regret_history, actions_history)
    '''
    rewards_history = []
    regret_history = []
    actions_history = []
    cumulative_regret = 0   

    for step in range(steps):
        # Choose an action
        action = agent.select_action()
        actions_history.append(action)

        # Get the reward
        reward = bandit.pull_arm(action)

        # Update the agent
        agent.update(action, reward)
        
        # Record history
        avg_reward = agent.total_reward / agent.total_steps
        rewards_history.append(avg_reward)

        # Record regret (The difference between the optimal arm)
        regret = bandit.optimal_reward - bandit.true_rewards[action]
        cumulative_regret += regret
        regret_history.append(cumulative_regret)

    return rewards_history, regret_history, actions_history

def plot_single_experiment(bandit: MultiArmedBandit, agent: EpsilonGreedyAgent,
                           actions_history: List[int]):
    """
    Plot visualization for a single experiment.

    Args:
        bandit: The multi-armed bandit environment
        agent: The trained epsilon-greedy agent
        actions_history: List of actions taken during the experiment
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'Epsilon-Greedy Single Experiment (ε={agent.epsilon})', fontsize=14)
    arms = np.arange(bandit.k)

    # 1. Action Selection Frequency
    ax = axes[0, 0]
    ax.bar(arms, agent.action_counts, color='steelblue')
    ax.axvline(x=bandit.optimal_arm, color='red', linestyle='--', label='Optimal arm')
    ax.set_xlabel('Arm')
    ax.set_ylabel('Selection Count')
    ax.set_title('Action Selection Frequency')
    ax.set_xticks(arms)
    ax.legend()

    # 2. Value Estimation Accuracy
    ax = axes[0, 1]
    width = 0.35
    ax.bar(arms - width / 2, bandit.true_rewards, width, label='True value', color='coral')
    ax.bar(arms + width / 2, agent.q_estimates, width, label='Estimated value', color='steelblue')
    ax.set_xlabel('Arm')
    ax.set_ylabel('Value')
    ax.set_title('Value Estimation Accuracy')
    ax.set_xticks(arms)
    ax.legend()

    # 3. Action Sequence (recent 1000 steps)
    ax = axes[1, 0]
    recent = actions_history[-1000:]
    ax.scatter(range(len(recent)), recent, s=1, alpha=0.5, color='steelblue')
    ax.axhline(y=bandit.optimal_arm, color='red', linestyle='--', label='Optimal arm')
    ax.set_xlabel('Step (last 1000)')
    ax.set_ylabel('Selected Arm')
    ax.set_title('Action Sequence (Recent 1000 Steps)')
    ax.set_yticks(arms)
    ax.legend()

    # 4. Optimal Arm Selection Rate over time
    ax = axes[1, 1]
    optimal_counts = np.cumsum(np.array(actions_history) == bandit.optimal_arm)
    steps_arr = np.arange(1, len(actions_history) + 1)
    optimal_rate = optimal_counts / steps_arr
    ax.plot(steps_arr, optimal_rate, color='steelblue')
    ax.set_xlabel('Step')
    ax.set_ylabel('Optimal Arm Selection Rate')
    ax.set_title('Optimal Arm Selection Rate')

    plt.tight_layout()
    plt.savefig('RL/Ch1/results/single_experiment.png', dpi=150)
    plt.show()


def main():
    # Set random seed for reproducibility
    # np.random.seed(42)
    # random.seed(42)

    # Create a multi-armed bandit with 10 arms
    bandit = MultiArmedBandit(k=10)

    print("ArmBandit Setup:")
    print(f"Number of arms: {bandit.k}")
    print(f"Each arm's true reward expectations: {bandit.true_rewards}")
    print(f"Optimal arm: {bandit.optimal_arm} (Expected reward: {bandit.optimal_reward:.3f})")
    print()

    # Single Experiment Demonstration
    print("=== Single Experiment Demonstration (ε=0.1) ===")
    agent = EpsilonGreedyAgent(k=10, epsilon=0.1)
    rewards, regrets, actions = run_experiment(bandit, agent, steps=2000)

    print(f"Total reward after Experiment ended: {agent.q_estimates}")
    print(f"The Chosen times for each arm: {agent.action_counts}")
    print(f"Final average reward: {rewards[-1]:.3f}")
    print(f"Cumulative regret: {regrets[-1]:.3f}")
    print()

    # Visualization
    plot_single_experiment(bandit, agent, actions)

if __name__ == "__main__":
    main()