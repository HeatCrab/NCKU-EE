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
from torch.distributions import Normal

class ActorCritic(nn.Module):
    """
    Shared-trunk actor-critic network for continuous-action PPO.
    Input:  state, shape (batch_size, n_states)
            For MountainCarContinuous: n_states = 2
    Output: action mean mu(s), shape (batch_size, n_actions)
            For MountainCarContinuous: n_actions = 1, squashed to [-bound, bound]
            state value V(s), shape (batch_size,)

    The actor head produces only the Gaussian mean (tanh * action_bound). The
    standard deviation is state-independent: a single global learnable log_std
    parameter (init -0.5) shared across all states, so the policy is
    N(mu(s), exp(log_std)^2). This is simpler and more stable than letting the
    network output a per-state std. The trunk follows the slide diagram:
    Linear -> LayerNorm -> ReLU, twice.
    """

    def __init__(self, n_states, n_actions, action_bound, hidden_dim=64,
                 log_std_init=0.0, sigma_floor=0.5):
        super(ActorCritic, self).__init__()
        self.action_bound = action_bound
        self.sigma_floor = sigma_floor

        # Shared feature trunk (LayerNorm + ReLU, matching the slide)
        self.shared = nn.Sequential(
            nn.Linear(n_states, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
        )

        # Actor head outputs the Gaussian mean; critic head outputs V(s)
        self.actor_head  = nn.Linear(hidden_dim, n_actions)
        self.critic_head = nn.Linear(hidden_dim, 1)

        # State-independent std: one global learnable log_std. Init high
        # (sigma=1.0) so early exploration is strong enough to reach the goal;
        # the std is floored in _distribution so the action-cost pressure cannot
        # collapse it to a do-nothing policy (the failure mode we diagnosed).
        self.log_std = nn.Parameter(torch.ones(n_actions) * log_std_init)

    def forward(self, x):
        features = self.shared(x)
        mean  = torch.tanh(self.actor_head(features)) * self.action_bound
        value = self.critic_head(features)
        return mean, value

    def _distribution(self, mean):
        std = torch.exp(self.log_std).clamp(min=self.sigma_floor)
        return Normal(mean, std)

    def get_action(self, state_t):
        # Rollout-time: sample from the Gaussian policy. The raw (unclipped)
        # sample and its log-prob are returned so the importance ratio stays
        # consistent later; the caller clips before stepping the environment.
        mean, value = self.forward(state_t)
        dist = self._distribution(mean)
        action = dist.sample()
        log_prob = dist.log_prob(action).sum(-1)
        return action, log_prob, value.squeeze(-1)

    def evaluate_actions(self, states, actions):
        # Update-time: re-score the stored actions under the current policy.
        # Sum log-prob / entropy over the action dimensions (1D here).
        mean, values = self.forward(states)
        dist = self._distribution(mean)
        log_probs = dist.log_prob(actions).sum(-1)
        entropy   = dist.entropy().sum(-1)
        return log_probs, entropy, values.squeeze(-1)


class RolloutBuffer:
    """
    On-policy storage for a single rollout of fixed length.
    Unlike the off-policy ReplayBuffer used in DDPG/TD3, this buffer is cleared
    after every update: PPO only trains on data collected by the current policy.
    Stores (state, action, log_prob, reward, value, done) per timestep; the
    advantages and returns are computed by the agent at update time via GAE.
    """

    def __init__(self):
        self.clear()

    def clear(self):
        self.states    = []
        self.actions   = []
        self.log_probs = []
        self.rewards   = []
        self.values    = []
        self.dones     = []

    def push(self, state, action, log_prob, reward, value, done):
        self.states.append(state)
        self.actions.append(action)
        self.log_probs.append(log_prob)
        self.rewards.append(reward)
        self.values.append(value)
        self.dones.append(done)

    def __len__(self):
        return len(self.states)


class PPOAgent:
    """
    PPO agent (actor-critic style, Algorithm 1 in the slides), continuous version.
    Same clipped-surrogate update as the discrete case; only the policy
    distribution changes (Gaussian instead of Categorical). Encapsulates the
    network, optimizer, GAE advantage estimation, and the K-epoch minibatch
    update that reuses each rollout before discarding it.
    """

    def __init__(self, n_states, n_actions, action_bound, device,
                 lr=3e-4, gamma=0.99, gae_lambda=0.95, clip_eps=0.2,
                 value_coef=0.5, entropy_coef=0.01,
                 n_epochs=10, minibatch_size=64, max_grad_norm=0.5,
                 log_std_init=0.0, sigma_floor=0.5):
        self.device = device
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_eps = clip_eps
        self.value_coef = value_coef
        self.entropy_coef = entropy_coef
        self.n_epochs = n_epochs
        self.minibatch_size = minibatch_size
        self.max_grad_norm = max_grad_norm

        self.net = ActorCritic(n_states, n_actions, action_bound,
                               log_std_init=log_std_init, sigma_floor=sigma_floor).to(device)
        self.optimizer = optim.Adam(self.net.parameters(), lr=lr)

    def select_action(self, state):
        # Stochastic action for rollout collection; returns plain numpy/scalars
        state_t = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            action, log_prob, value = self.net.get_action(state_t)
        return action.cpu().numpy()[0], log_prob.item(), value.item()

    def predict(self, state):
        # Deterministic action (the Gaussian mean) for evaluation and demo
        state_t = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            mean, _ = self.net(state_t)
        return mean.cpu().numpy()[0]

    def compute_gae(self, rewards, values, dones, last_value):
        # Backward recursion: delta_t = r_t + gamma V(s_{t+1})(1-done) - V(s_t)
        #                     A_t     = delta_t + gamma lambda (1-done) A_{t+1}
        T = len(rewards)
        advantages = np.zeros(T, dtype=np.float32)
        last_gae = 0.0
        for t in reversed(range(T)):
            next_value = last_value if t == T - 1 else values[t + 1]
            next_non_terminal = 1.0 - dones[t]
            delta = rewards[t] + self.gamma * next_value * next_non_terminal - values[t]
            last_gae = delta + self.gamma * self.gae_lambda * next_non_terminal * last_gae
            advantages[t] = last_gae
        # R_t = A_t + V(s_t): the value-function regression target
        returns = advantages + np.array(values, dtype=np.float32)
        return advantages, returns

    def update(self, buffer, last_value):
        # 1) Turn the rollout into GAE advantages and value targets
        advantages, returns = self.compute_gae(
            buffer.rewards, buffer.values, buffer.dones, last_value)

        states        = torch.FloatTensor(np.array(buffer.states)).to(self.device)
        actions       = torch.FloatTensor(np.array(buffer.actions)).to(self.device)
        old_log_probs = torch.FloatTensor(np.array(buffer.log_probs)).to(self.device)
        advantages_t  = torch.FloatTensor(advantages).to(self.device)
        returns_t     = torch.FloatTensor(returns).to(self.device)

        # Advantage normalization: A_hat = (A - mu) / (sigma + eps)
        advantages_t = (advantages_t - advantages_t.mean()) / (advantages_t.std() + 1e-8)

        n = len(buffer)
        indices = np.arange(n)

        # 2) K epochs of minibatch SGD on the same collected rollout
        for _ in range(self.n_epochs):
            np.random.shuffle(indices)
            for start in range(0, n, self.minibatch_size):
                mb = indices[start:start + self.minibatch_size]

                new_log_probs, entropy, values = self.net.evaluate_actions(
                    states[mb], actions[mb])

                # Importance sampling ratio: rho = exp(log pi - log pi_old)
                ratio = torch.exp(new_log_probs - old_log_probs[mb])

                # Clipped surrogate objective (maximise -> negate to a loss)
                surr1 = ratio * advantages_t[mb]
                surr2 = torch.clamp(ratio, 1 - self.clip_eps, 1 + self.clip_eps) * advantages_t[mb]
                policy_loss = -torch.min(surr1, surr2).mean()

                # Value function loss: L_VF = E[(R_t - V(s_t))^2]
                value_loss = F.mse_loss(values, returns_t[mb])

                # Entropy bonus encourages exploration
                entropy_loss = entropy.mean()

                # Final objective: L = -L_CLIP + c1 L_VF - c2 L_ENT
                loss = policy_loss + self.value_coef * value_loss - self.entropy_coef * entropy_loss

                self.optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(self.net.parameters(), self.max_grad_norm)
                self.optimizer.step()


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
        plt.savefig("results/ppo_continuous_results.png", dpi=150, bbox_inches="tight")

    if SHOW_TRAINING_PROGRESS:
        plt.pause(0.001)
    else:
        plt.close()


if __name__ == "__main__":

    env_temp = gym.make("MountainCarContinuous-v0")
    n_states     = env_temp.observation_space.shape[0]
    n_actions    = env_temp.action_space.shape[0]
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

    MODEL_SAVE_DIR = "ppo_continuous_models"
    POLICY_PATH    = os.path.join(MODEL_SAVE_DIR, "ppo_model.pth")
    TRAINING_PATH  = os.path.join(MODEL_SAVE_DIR, "training_info.pth")

    ###########################################################################
    # Mode Selection
    ###########################################################################
    print("=" * 60)
    print("PPO Mountain Car (Continuous) - Mode Selection")
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

        if not os.path.exists(POLICY_PATH):
            print(f"Error: model not found at {POLICY_PATH}")
            exit()

        agent = PPOAgent(n_states, n_actions, action_bound, device)
        agent.net.load_state_dict(torch.load(POLICY_PATH, map_location=device))
        agent.net.eval()

        env = gym.make("MountainCarContinuous-v0", render_mode="human")

        for i_episode in range(10):
            state, _ = env.reset()
            total_reward = 0
            for t in count():
                action = agent.predict(state)
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
        print("=== TRAINING MODE (PPO Continuous) ===")
        print("=" * 50)
        print("Starting PPO training")

        SHOW_GAME_DURING_TRAINING = False
        SHOW_TRAINING_PROGRESS    = False

        LR             = 3e-4
        GAMMA          = 0.99
        GAE_LAMBDA     = 0.95
        CLIP_EPS       = 0.2
        VALUE_COEF     = 0.5
        ENTROPY_COEF   = 0.0     # off: the sigma floor handles exploration; a
                                 # positive coef inflates sigma without bound
                                 # once the task is solved
        N_EPOCHS       = 10
        MINIBATCH_SIZE = 64
        ROLLOUT_STEPS  = 2048
        MAX_GRAD_NORM  = 0.5
        NUM_EPISODES   = 2000
        LOG_STD_INIT   = 0.0     # initial sigma = exp(0.0) = 1.0 (strong early exploration)
        SIGMA_FLOOR    = 0.5     # sigma can refine down to here but never collapse

        env = (gym.make("MountainCarContinuous-v0", render_mode="human")
               if SHOW_GAME_DURING_TRAINING
               else gym.make("MountainCarContinuous-v0"))

        agent = PPOAgent(n_states, n_actions, action_bound, device,
                         lr=LR, gamma=GAMMA, gae_lambda=GAE_LAMBDA,
                         clip_eps=CLIP_EPS, value_coef=VALUE_COEF,
                         entropy_coef=ENTROPY_COEF, n_epochs=N_EPOCHS,
                         minibatch_size=MINIBATCH_SIZE, max_grad_norm=MAX_GRAD_NORM,
                         log_std_init=LOG_STD_INIT, sigma_floor=SIGMA_FLOOR)
        buffer = RolloutBuffer()

        episode_rewards = []
        episode_lengths = []
        total_steps     = 0

        if SHOW_TRAINING_PROGRESS:
            plt.ion()

        state, _ = env.reset()
        episode_reward = 0
        episode_len    = 0

        # On-policy training: repeatedly collect a fixed-length rollout, then
        # run K epochs of clipped-surrogate updates on it (PDF Algorithm 1).
        while len(episode_rewards) < NUM_EPISODES:
            buffer.clear()

            for _ in range(ROLLOUT_STEPS):
                action, log_prob, value = agent.select_action(state)
                # Clip the sampled action to the valid range for the environment;
                # the unclipped action stays in the buffer for a consistent ratio.
                clipped_action = np.clip(action, -action_bound, action_bound)
                next_state, reward, terminated, truncated, _ = env.step(clipped_action)
                done = terminated or truncated

                buffer.push(state, action, log_prob, reward, value, float(done))
                state = next_state
                episode_reward += reward
                episode_len    += 1
                total_steps    += 1

                if done:
                    episode_rewards.append(episode_reward)
                    episode_lengths.append(episode_len)

                    if len(episode_rewards) % 50 == 0:
                        recent = episode_rewards[-50:]
                        avg = sum(recent) / len(recent)
                        print(f"Episode {len(episode_rewards)}/{NUM_EPISODES} | last-50 avg reward = {avg:.1f}")

                    state, _ = env.reset()
                    episode_reward = 0
                    episode_len    = 0

                if len(episode_rewards) >= NUM_EPISODES:
                    break

            # Bootstrap the value of the state following the rollout, then update.
            # If the rollout ended on a terminal step, this value is masked by done.
            with torch.no_grad():
                last_state_t = torch.FloatTensor(state).unsqueeze(0).to(device)
                _, last_value_t = agent.net(last_state_t)
                last_value = last_value_t.item()

            agent.update(buffer, last_value)
            plot_results(episode_rewards, episode_lengths)

        os.makedirs(MODEL_SAVE_DIR, exist_ok=True)
        torch.save(agent.net.state_dict(), POLICY_PATH)
        torch.save({'episode_rewards': episode_rewards, 'episode_lengths': episode_lengths,
                    'total_steps': total_steps}, TRAINING_PATH)
        print(f"Models saved to {MODEL_SAVE_DIR}/")

        print("Complete")
        plot_results(episode_rewards, episode_lengths, show_result=True)
        if SHOW_TRAINING_PROGRESS:
            plt.ioff()
            plt.show()
        env.close()
