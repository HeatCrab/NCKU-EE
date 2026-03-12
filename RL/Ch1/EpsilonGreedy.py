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

        reward = np.random.normal(self.true_rewards[arm], 1)
        return reward
    
class EpsilonGreedyAgent:
    ''' Epsilon-greedy agent for multi-armed bandit '''

    def __init__(self, k: int, epsilon: float = 0.1):
        '''
        Initializes an epsilon-greedy agent
        
        Args:
            k: Number of arms in the bandit
            epsilon: Probability of choosing a random arm (exploration)
        '''
        self.k = k
        self.epsilon = epsilon
        self.counts = np.zeros(k)  # Count of pulls for each arm
        self.values = np.zeros(k)  # Estimated value of each arm
        self.total_reward = 0
        self.total_steps = 0

def main():
    # Set random seed for reproducibility
    np.random.seed(42)
    random.seed(42)

    # Create a multi-armed bandit with 10 arms
    bandit = MultiArmedBandit(k=10)

    print("ArmBandit Setup:")
    print(f"Number of arms: {bandit.k}")
    print(f"Each arm's true reward expectations: {bandit.true_rewards}")
    print(f"Optimal arm: {bandit.optimal_arm} (Expected reward: {bandit.optimal_reward:.3f})")
    print()

    # Create an epsilon-greedy agent
    agent = EpsilonGreedyAgent(k=10, epsilon=0.1)
    print(agent.k)
    print(agent.epsilon)

if __name__ == "__main__":
    main()