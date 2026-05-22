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
from torch.distributions import Categorical

class ActorCritic(nn.Module):
    """
    Shared-trunk actor-critic network for discrete-action PPO.
    Input:  state, shape (batch_size, n_states)
            For Acrobot-v1: n_states = 6
    Output: actor logits, shape (batch_size, n_actions) -> Categorical policy
            For Acrobot-v1: n_actions = 3
            critic value, shape (batch_size,) -> state value V(s)

    The trunk (Linear 6->64->64 with Tanh) extracts shared features, then two
    heads branch off: the actor head produces action logits and the critic head
    produces a scalar value. Weights use orthogonal initialisation; the heads
    follow the gains specified in the slide (actor gain=0.01 -> near-uniform
    initial policy, critic gain=1.0).
    """

    def __init__(self, n_states, n_actions, hidden_dim=64):
        super(ActorCritic, self).__init__()

        # Shared feature trunk
        self.shared = nn.Sequential(
            nn.Linear(n_states, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
        )

        # Separate heads for policy logits and state value
        self.actor_head  = nn.Linear(hidden_dim, n_actions)
        self.critic_head = nn.Linear(hidden_dim, 1)

        self._init_weights()

    def _init_weights(self):
        # Orthogonal init: trunk uses gain=sqrt(2), heads use the slide's gains
        for layer in self.shared:
            if isinstance(layer, nn.Linear):
                nn.init.orthogonal_(layer.weight, gain=np.sqrt(2))
                nn.init.constant_(layer.bias, 0.0)
        nn.init.orthogonal_(self.actor_head.weight,  gain=0.01)
        nn.init.constant_(self.actor_head.bias, 0.0)
        nn.init.orthogonal_(self.critic_head.weight, gain=1.0)
        nn.init.constant_(self.critic_head.bias, 0.0)

    def forward(self, x):
        features = self.shared(x)
        logits = self.actor_head(features)
        value  = self.critic_head(features)
        return logits, value

    def get_action(self, state_t):
        # Rollout-time: sample an action from the current stochastic policy
        logits, value = self.forward(state_t)
        dist = Categorical(logits=logits)
        action = dist.sample()
        return action, dist.log_prob(action), value.squeeze(-1)

    def evaluate_actions(self, states, actions):
        # Update-time: re-score the stored actions under the current policy
        logits, values = self.forward(states)
        dist = Categorical(logits=logits)
        log_probs = dist.log_prob(actions)
        entropy   = dist.entropy()
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
    PPO agent (actor-critic style, Algorithm 1 in the slides).
    Encapsulates the shared actor-critic network, its optimizer, GAE advantage
    estimation, and the clipped-surrogate update performed over K epochs of
    minibatches. The same rollout is reused for every epoch, then discarded.
    """

    def __init__(self, n_states, n_actions, device,
                 lr=3e-4, gamma=0.99, gae_lambda=0.95, clip_eps=0.2,
                 value_coef=0.5, entropy_coef=0.01,
                 n_epochs=10, minibatch_size=64, max_grad_norm=0.5):
        self.device = device
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_eps = clip_eps
        self.value_coef = value_coef
        self.entropy_coef = entropy_coef
        self.n_epochs = n_epochs
        self.minibatch_size = minibatch_size
        self.max_grad_norm = max_grad_norm

        self.net = ActorCritic(n_states, n_actions).to(device)
        self.optimizer = optim.Adam(self.net.parameters(), lr=lr)

    def select_action(self, state):
        # Stochastic action for rollout collection; returns plain scalars
        state_t = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            action, log_prob, value = self.net.get_action(state_t)
        return action.item(), log_prob.item(), value.item()

    def predict(self, state):
        # Deterministic action (argmax logits) for evaluation and demo
        state_t = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            logits, _ = self.net(state_t)
            action = torch.argmax(logits, dim=1)
        return action.item()

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
        actions       = torch.LongTensor(np.array(buffer.actions)).to(self.device)
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


def evaluate_policy(agent, env, n_episodes=10):
    # Run the greedy (deterministic) policy to gauge real performance
    rewards = []
    for _ in range(n_episodes):
        state, _ = env.reset()
        total_reward = 0
        for t in count():
            action = agent.predict(state)
            state, reward, terminated, truncated, _ = env.step(action)
            total_reward += reward
            if terminated or truncated:
                break
        rewards.append(total_reward)
    return float(np.mean(rewards))


def plot_results(episode_rewards, episode_lengths, eval_timesteps, eval_rewards, show_result=False):
    if not show_result and not SHOW_TRAINING_PROGRESS:
        return

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('PPO Acrobot Training Results (PyTorch)' if show_result else 'Training...')

    rewards_t = np.array(episode_rewards)
    lengths_t = np.array(episode_lengths)

    # Panel 1: per-episode reward
    ax1.set_title('Episode Rewards')
    ax1.set_xlabel('Episode')
    ax1.set_ylabel('Reward')
    ax1.plot(rewards_t, 'b-', alpha=0.4, linewidth=1)
    ax1.axhline(y=-100, color='g', linestyle='--', alpha=0.7, label='Success threshold')
    if len(rewards_t) >= 50:
        means = np.convolve(rewards_t, np.ones(50)/50, mode='valid')
        ax1.plot(range(49, len(rewards_t)), means, 'r-', linewidth=2, label='50-episode average')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Panel 2: per-episode length
    ax2.set_title('Episode Lengths')
    ax2.set_xlabel('Episode')
    ax2.set_ylabel('Steps')
    ax2.plot(lengths_t, 'g-', alpha=0.4, linewidth=1)
    ax2.axhline(y=500, color='orange', linestyle='--', alpha=0.7, label='Max steps')
    if len(lengths_t) >= 50:
        means_l = np.convolve(lengths_t, np.ones(50)/50, mode='valid')
        ax2.plot(range(49, len(lengths_t)), means_l, 'r-', linewidth=2, label='50-episode average')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Panel 3: deterministic-policy evaluation over training
    ax3.set_title('Evaluation Performance')
    ax3.set_xlabel('Timesteps')
    ax3.set_ylabel('Mean Reward')
    if len(eval_timesteps) > 0:
        ax3.plot(eval_timesteps, eval_rewards, 'r-o', linewidth=1)
    ax3.axhline(y=-100, color='g', linestyle='--', alpha=0.7, label='Success threshold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # Panel 4: rolling success rate (reward > -100) over a 50-episode window
    ax4.set_title('Success Rate (50-episode window)')
    ax4.set_xlabel('Episode')
    ax4.set_ylabel('Success Rate (%)')
    if len(rewards_t) >= 50:
        success = (rewards_t > -100).astype(np.float32)
        rate = np.convolve(success, np.ones(50)/50, mode='valid') * 100
        ax4.plot(range(49, len(rewards_t)), rate, color='purple', linewidth=1.5)
    ax4.axhline(y=80, color='g', linestyle='--', alpha=0.7, label='Target (80%)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()

    if show_result:
        os.makedirs("results", exist_ok=True)
        plt.savefig("results/ppo_results.png", dpi=150, bbox_inches="tight")

    if SHOW_TRAINING_PROGRESS:
        plt.pause(0.001)
    else:
        plt.close()


if __name__ == "__main__":

    env_temp = gym.make("Acrobot-v1")
    n_states  = env_temp.observation_space.shape[0]
    n_actions = env_temp.action_space.n
    env_temp.close()

    print(f"Environment: Acrobot-v1")
    print(f"State space:  {n_states}")
    print(f"Action space: {n_actions}")

    device = torch.device(
        "cuda" if torch.cuda.is_available() else
        "mps"  if torch.backends.mps.is_available() else
        "cpu"
    )

    MODEL_SAVE_DIR = "ppo_models"
    POLICY_PATH    = os.path.join(MODEL_SAVE_DIR, "ppo_model.pth")
    TRAINING_PATH  = os.path.join(MODEL_SAVE_DIR, "training_info.pth")

    ###########################################################################
    # Mode Selection
    ###########################################################################
    print("=" * 60)
    print("PPO Acrobot - Mode Selection")
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

        agent = PPOAgent(n_states, n_actions, device)
        agent.net.load_state_dict(torch.load(POLICY_PATH, map_location=device))
        agent.net.eval()

        env = gym.make("Acrobot-v1", render_mode="human")

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
        print("=== TRAINING MODE (PPO) ===")
        print("=" * 50)
        print("Starting PPO training")

        SHOW_GAME_DURING_TRAINING = False
        SHOW_TRAINING_PROGRESS    = False

        LR             = 3e-4
        GAMMA          = 0.99
        GAE_LAMBDA     = 0.95
        CLIP_EPS       = 0.2
        VALUE_COEF     = 0.5
        ENTROPY_COEF   = 0.01
        N_EPOCHS       = 10
        MINIBATCH_SIZE = 64
        ROLLOUT_STEPS  = 2048
        MAX_GRAD_NORM  = 0.5
        NUM_EPISODES   = 1500
        EVAL_FREQ      = 20000
        EVAL_EPISODES  = 10

        env = (gym.make("Acrobot-v1", render_mode="human")
               if SHOW_GAME_DURING_TRAINING
               else gym.make("Acrobot-v1"))
        eval_env = gym.make("Acrobot-v1")

        agent = PPOAgent(n_states, n_actions, device,
                         lr=LR, gamma=GAMMA, gae_lambda=GAE_LAMBDA,
                         clip_eps=CLIP_EPS, value_coef=VALUE_COEF,
                         entropy_coef=ENTROPY_COEF, n_epochs=N_EPOCHS,
                         minibatch_size=MINIBATCH_SIZE, max_grad_norm=MAX_GRAD_NORM)
        buffer = RolloutBuffer()

        episode_rewards = []
        episode_lengths = []
        eval_timesteps  = []
        eval_rewards    = []
        total_steps     = 0
        next_eval       = EVAL_FREQ

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
                next_state, reward, terminated, truncated, _ = env.step(action)
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

                # Periodic deterministic-policy evaluation
                if total_steps >= next_eval:
                    mean_eval = evaluate_policy(agent, eval_env, EVAL_EPISODES)
                    eval_timesteps.append(total_steps)
                    eval_rewards.append(mean_eval)
                    next_eval += EVAL_FREQ

                if len(episode_rewards) >= NUM_EPISODES:
                    break

            # Bootstrap the value of the state following the rollout, then update.
            # If the rollout ended on a terminal step, this value is masked by done.
            with torch.no_grad():
                last_state_t = torch.FloatTensor(state).unsqueeze(0).to(device)
                _, last_value_t = agent.net(last_state_t)
                last_value = last_value_t.item()

            agent.update(buffer, last_value)
            plot_results(episode_rewards, episode_lengths, eval_timesteps, eval_rewards)

        os.makedirs(MODEL_SAVE_DIR, exist_ok=True)
        torch.save(agent.net.state_dict(), POLICY_PATH)
        torch.save({'episode_rewards': episode_rewards, 'episode_lengths': episode_lengths,
                    'eval_timesteps': eval_timesteps, 'eval_rewards': eval_rewards,
                    'total_steps': total_steps}, TRAINING_PATH)
        print(f"Models saved to {MODEL_SAVE_DIR}/")

        print("Complete")
        plot_results(episode_rewards, episode_lengths, eval_timesteps, eval_rewards, show_result=True)
        if SHOW_TRAINING_PROGRESS:
            plt.ioff()
            plt.show()
        env.close()
        eval_env.close()
