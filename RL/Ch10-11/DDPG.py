import gymnasium as gym 
import math
import random 
import matplotlib
import matplotlib.pyplot as plt
from collections import namedtuple, deque
from itertools import count
import time
import numpy as np
import os

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

class Actor(nn.Module):
    """
    Selects an action given the current state.
    Input:  state, shape (batch_size, n_states)
            For MountainCarContinuous: n_states = 2
    Output: action, shape (batch_size, n_actions)
            For MountainCarContinuous: n_actions = 1
            Output range: [-action_bound, action_bound]
    """

    def __init__(self, n_states, n_actions, action_bound, hidden_dim=256):
        super(Actor, self).__init__()
        self.action_bound = action_bound

        # Network layers
        self.layer1 = nn.Linear(n_states, hidden_dim)
        self.layer2 = nn.Linear(hidden_dim, hidden_dim)
        self.layer3 = nn.Linear(hidden_dim, n_actions)

        # LayerNorm instead of BatchNorm for more stable small-batch training
        self.ln1 = nn.LayerNorm(hidden_dim)
        self.ln2 = nn.LayerNorm(hidden_dim)

    def forward(self, x):
        x = F.relu(self.ln1(self.layer1(x)))
        x = F.relu(self.ln2(self.layer2(x)))
        x = torch.tanh(self.layer3(x))
        return x * self.action_bound


class Critic(nn.Module):
    """
    Estimates the Q-value Q(s, a) for a given state-action pair.
    """

    def __init__(self, n_states, n_actions, hidden_dim=256):
        super(Critic, self).__init__()

        # Three hidden layers; state and action are concatenated as input
        self.layer1 = nn.Linear(n_states + n_actions, hidden_dim)
        self.layer2 = nn.Linear(hidden_dim, hidden_dim)
        self.layer3 = nn.Linear(hidden_dim, hidden_dim)
        self.output = nn.Linear(hidden_dim, 1)

        self.ln1 = nn.LayerNorm(hidden_dim)
        self.ln2 = nn.LayerNorm(hidden_dim)
        self.ln3 = nn.LayerNorm(hidden_dim)

    def forward(self, state, action):
        x = torch.cat([state, action], dim=1)
        x = F.relu(self.ln1(self.layer1(x)))
        x = F.relu(self.ln2(self.layer2(x)))
        x = F.relu(self.ln3(self.layer3(x)))
        return self.output(x)


class OUNoise:
    """
    Ornstein-Uhlenbeck noise process for continuous action exploration.
    Generates temporally correlated noise that produces smoother action
    sequences than independent Gaussian noise.
    """

    def __init__(self, n_actions, mu=0.0, theta=0.15, sigma=0.4, dt=0.01):
        self.n_actions = n_actions
        self.mu = mu
        self.theta = theta
        self.sigma = sigma
        self.dt = dt
        self.reset()

    def reset(self):
        self.x = np.zeros(self.n_actions)

    def sample(self):
        # x_{t+1} = x_t + θ(μ - x_t)Δt + σ√Δt * N(0,1)
        self.x = (self.x
                  + self.theta * (self.mu - self.x) * self.dt
                  + self.sigma * np.sqrt(self.dt) * np.random.randn(self.n_actions))
        return self.x


class ReplayBuffer:
    """
    Fixed-capacity circular buffer storing (s, a, r, s', done) transitions.
    Enables random sampling to break temporal correlations during training.
    """

    def __init__(self, capacity):
        self.buffer = deque([], maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        return (
            torch.FloatTensor(np.array(states)),
            torch.FloatTensor(np.array(actions)),
            torch.FloatTensor(np.array(rewards)).unsqueeze(1),
            torch.FloatTensor(np.array(next_states)),
            torch.FloatTensor(np.array(dones)).unsqueeze(1),
        )

    def __len__(self):
        return len(self.buffer)


class DDPGAgent:
    """
    DDPG agent encapsulating Actor/Critic networks, target networks,
    noise process, and update logic.
    """

    def __init__(self, n_states, n_actions, action_bound, device,
                 actor_lr=2e-4, critic_lr=1e-3, gamma=0.99, tau=0.002):
        self.device = device
        self.gamma = gamma
        self.tau = tau

        # Main networks
        self.actor  = Actor(n_states, n_actions, action_bound).to(device)
        self.critic = Critic(n_states, n_actions).to(device)

        # Target networks initialised to the same weights
        self.actor_target  = Actor(n_states, n_actions, action_bound).to(device)
        self.critic_target = Critic(n_states, n_actions).to(device)
        self.actor_target.load_state_dict(self.actor.state_dict())
        self.critic_target.load_state_dict(self.critic.state_dict())

        self.actor_optimizer  = optim.Adam(self.actor.parameters(),  lr=actor_lr)
        self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=critic_lr)

        self.noise = OUNoise(n_actions)

    def select_action(self, state, add_noise=True):
        state_t = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        self.actor.eval()
        with torch.no_grad():
            action = self.actor(state_t).cpu().numpy()[0]
        self.actor.train()
        if add_noise:
            action += self.noise.sample()
        return action

    def update(self, buffer, batch_size):
        states, actions, rewards, next_states, dones = [
            t.to(self.device) for t in buffer.sample(batch_size)
        ]

        # Critic update: minimise MSE against Bellman target
        with torch.no_grad():
            next_actions  = self.actor_target(next_states)
            target_q = rewards + self.gamma * (1 - dones) * self.critic_target(next_states, next_actions)

        critic_loss = nn.MSELoss()(self.critic(states, actions), target_q)
        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.critic.parameters(), 1.0)
        self.critic_optimizer.step()

        # Actor update: maximise expected Q-value (gradient ascent via negation)
        actor_loss = -self.critic(states, self.actor(states)).mean()
        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.actor.parameters(), 1.0)
        self.actor_optimizer.step()

        # Soft update both target networks: θ_target ← τθ + (1-τ)θ_target
        for param, target in zip(self.actor.parameters(),  self.actor_target.parameters()):
            target.data.copy_(self.tau * param.data + (1 - self.tau) * target.data)
        for param, target in zip(self.critic.parameters(), self.critic_target.parameters()):
            target.data.copy_(self.tau * param.data + (1 - self.tau) * target.data)


def plot_results(episode_rewards, episode_lengths, show_result=False):
    if not show_result and not SHOW_TRAINING_PROGRESS:
        return

    _, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    title = 'Final Rewards' if show_result else 'Training...'

    rewards_t = np.array(episode_rewards)
    lengths_t = np.array(episode_lengths)

    ax1.set_title(title)
    ax1.set_xlabel('Episode')
    ax1.set_ylabel('Reward')
    ax1.plot(rewards_t, 'b-', alpha=0.4, linewidth=1)
    ax1.axhline(y=90, color='g', linestyle='--', alpha=0.7, label='Target (90)')
    if len(rewards_t) >= 50:
        means = np.convolve(rewards_t, np.ones(50)/50, mode='valid')
        ax1.plot(range(49, len(rewards_t)), means, 'r-', linewidth=2, label='50-episode average')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.set_title('Final Episode Lengths' if show_result else 'Training...')
    ax2.set_xlabel('Episode')
    ax2.set_ylabel('Length')
    ax2.plot(lengths_t, 'b-', alpha=0.4, linewidth=1)
    if len(lengths_t) >= 50:
        means_l = np.convolve(lengths_t, np.ones(50)/50, mode='valid')
        ax2.plot(range(49, len(lengths_t)), means_l, 'r-', linewidth=2, label='50-episode average')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    if show_result:
        os.makedirs("results", exist_ok=True)
        plt.savefig("results/ddpg_results.png", dpi=150, bbox_inches="tight")

    if SHOW_TRAINING_PROGRESS:
        plt.pause(0.001)
    else:
        plt.close()


if __name__ == "__main__":

    env_temp = gym.make("MountainCarContinuous-v0")
    n_states    = env_temp.observation_space.shape[0]
    n_actions   = env_temp.action_space.shape[0]
    action_bound = float(env_temp.action_space.high[0])
    env_temp.close()

    print(f"Environment: MountainCarContinuous-v0")
    print(f"State space:  {n_states}")
    print(f"Action space: {n_actions}")
    print(f"Action bound: {action_bound}")

    device = torch.device(
        "cuda" if torch.cuda.is_available() else
        "mps"  if torch.backends.mps.is_available() else
        "cpu"
    )

    MODEL_SAVE_DIR  = "ddpg_models"
    ACTOR_PATH      = os.path.join(MODEL_SAVE_DIR, "actor_model.pth")
    CRITIC_PATH     = os.path.join(MODEL_SAVE_DIR, "critic_model.pth")
    TRAINING_PATH   = os.path.join(MODEL_SAVE_DIR, "training_info.pth")

    ###########################################################################
    # Mode Selection
    ###########################################################################
    print("=" * 60)
    print("DDPG Mountain Car - Mode Selection")
    print("=" * 60)
    print("1. Train new model")
    print("2. Demo with existing model")
    print("=" * 60)

    while True:
        try:
            mode = input("Please select mode (1 for Train, 2 for Demo): ").strip()
            if mode == '1':
                MODE = "TRAIN"
                print("Selected: Training mode")
                break
            elif mode == '2':
                MODE = "DEMO"
                print("Selected: Demo mode")
                break
            else:
                print("Invalid input. Please enter 1 or 2.")
        except KeyboardInterrupt:
            print("\nProgram interrupted.")
            exit()

    print("=" * 60)

    # ////////// DEMO //////////
    if MODE == "DEMO":
        print(f"\n{'=' * 50}")
        print("=== DEMO MODE ===")
        print("=" * 50)

        if not os.path.exists(ACTOR_PATH):
            print(f"Error: model not found at {ACTOR_PATH}")
            exit()

        agent = DDPGAgent(n_states, n_actions, action_bound, device)
        agent.actor.load_state_dict(torch.load(ACTOR_PATH, map_location=device))
        agent.actor.eval()

        env = gym.make("MountainCarContinuous-v0", render_mode="human")

        for i_episode in range(10):
            state, _ = env.reset()
            total_reward = 0
            for t in count():
                action = agent.select_action(state, add_noise=False)
                state, reward, terminated, truncated, _ = env.step(action)
                total_reward += reward
                if terminated or truncated:
                    print(f"Episode {i_episode + 1}: steps = {t + 1}, reward = {total_reward:.1f}")
                    break
                time.sleep(0.02)

        env.close()

    # ////////// TRAIN //////////
    elif MODE == "TRAIN":
        print(f"\n{'=' * 50}")
        print("=== TRAINING MODE (DDPG) ===")
        print("=" * 50)
        print("Starting DDPG training")

        SHOW_GAME_DURING_TRAINING = False
        SHOW_TRAINING_PROGRESS    = False

        ACTOR_LR       = 2e-4
        CRITIC_LR      = 1e-3
        GAMMA          = 0.99
        TAU            = 0.002
        BATCH_SIZE     = 64
        BUFFER_CAPACITY = 100000
        WARMUP_STEPS   = 500
        NUM_EPISODES   = 1500

        env = (gym.make("MountainCarContinuous-v0", render_mode="human")
               if SHOW_GAME_DURING_TRAINING
               else gym.make("MountainCarContinuous-v0"))

        agent  = DDPGAgent(n_states, n_actions, action_bound, device,
                           actor_lr=ACTOR_LR, critic_lr=CRITIC_LR,
                           gamma=GAMMA, tau=TAU)
        buffer = ReplayBuffer(BUFFER_CAPACITY)

        episode_rewards = []
        episode_lengths = []
        total_steps     = 0

        if SHOW_TRAINING_PROGRESS:
            plt.ion()

        for i_episode in range(NUM_EPISODES):
            state, _ = env.reset()
            agent.noise.reset()
            episode_reward = 0

            for t in count():
                # Warmup: random actions to fill the buffer before learning
                if total_steps < WARMUP_STEPS:
                    action = env.action_space.sample()
                else:
                    action = agent.select_action(state, add_noise=True)

                next_state, reward, terminated, truncated, _ = env.step(action)
                done = terminated or truncated
                total_steps += 1
                episode_reward += reward

                buffer.push(state, action, reward, next_state, float(done))
                state = next_state

                if len(buffer) >= WARMUP_STEPS:
                    agent.update(buffer, BATCH_SIZE)

                if done:
                    break

            episode_rewards.append(episode_reward)
            episode_lengths.append(t + 1)
            plot_results(episode_rewards, episode_lengths)

            if (i_episode + 1) % 50 == 0:
                recent = episode_rewards[-50:]
                avg = sum(recent) / len(recent)
                print(f"Episode {i_episode + 1}/{NUM_EPISODES} | last-50 avg reward = {avg:.1f}")

        os.makedirs(MODEL_SAVE_DIR, exist_ok=True)
        torch.save(agent.actor.state_dict(),  ACTOR_PATH)
        torch.save(agent.critic.state_dict(), CRITIC_PATH)
        torch.save({'episode_rewards': episode_rewards, 'episode_lengths': episode_lengths,
                    'total_steps': total_steps}, TRAINING_PATH)
        print(f"Models saved to {MODEL_SAVE_DIR}/")

        print("Complete")
        plot_results(episode_rewards, episode_lengths, show_result=True)
        if SHOW_TRAINING_PROGRESS:
            plt.ioff()
            plt.show()
        env.close()
