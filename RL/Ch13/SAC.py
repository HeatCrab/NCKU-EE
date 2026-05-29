import importlib.util
import os
import random
import time
from collections import deque
from itertools import count

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.distributions import Normal

# The environment lives in "Mobile Robot.py" (space in the filename), so it
# cannot be imported with a normal import statement; load it by file path.
_env_path = os.path.join(os.path.dirname(__file__), "Mobile Robot.py")
_spec = importlib.util.spec_from_file_location("mobile_robot", _env_path)
mobile_robot = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mobile_robot)
CircleTrackingEnv = mobile_robot.CircleTrackingEnv

# Numerical floor that keeps the Jacobian-correction log() away from log(0).
LOG_STD_MIN = -20
LOG_STD_MAX = 2
EPSILON = 1e-6


class Actor(nn.Module):
    """
    Squashed-Gaussian policy for SAC.

    The shared trunk maps the state to a hidden representation, then two
    separate heads output the mean and the log standard deviation of a
    Gaussian over the pre-squash variable x. An action is produced by
    sampling x with the reparameterization trick, squashing it through
    tanh, and rescaling it into the environment's action range.

    Input:  state, shape (batch_size, n_states)
    Output (sample): action  shape (batch_size, n_actions), range [low, high]
                     log_prob shape (batch_size, 1), Jacobian-corrected
    """

    def __init__(self, n_states, n_actions, action_low, action_high, hidden_dim=256):
        super(Actor, self).__init__()

        # Shared trunk: two hidden layers (per Ch13 slide).
        self.layer1 = nn.Linear(n_states, hidden_dim)
        self.layer2 = nn.Linear(hidden_dim, hidden_dim)

        # Two output heads: Gaussian mean and log std over the pre-tanh value.
        self.mean_head    = nn.Linear(hidden_dim, n_actions)
        self.log_std_head = nn.Linear(hidden_dim, n_actions)

        # a = tanh(x) * scale + bias maps tanh's [-1, 1] onto [low, high].
        action_low  = torch.as_tensor(action_low,  dtype=torch.float32)
        action_high = torch.as_tensor(action_high, dtype=torch.float32)
        self.register_buffer("action_scale", (action_high - action_low) / 2.0)
        self.register_buffer("action_bias",  (action_high + action_low) / 2.0)

    def forward(self, state):
        x = F.relu(self.layer1(state))
        x = F.relu(self.layer2(x))
        mean = self.mean_head(x)
        # Clamp log std into a sane range so std = exp(log_std) cannot blow up
        # or collapse to zero during training.
        log_std = self.log_std_head(x).clamp(LOG_STD_MIN, LOG_STD_MAX)
        return mean, log_std

    def sample(self, state):
        mean, log_std = self.forward(state)
        std = log_std.exp()

        # Reparameterization trick: x = mean + std * eps, eps ~ N(0, 1).
        # rsample() keeps the sample differentiable wrt mean and std.
        normal = Normal(mean, std)
        x = normal.rsample()

        # Squash into [-1, 1] then rescale into the environment's action range.
        y = torch.tanh(x)
        action = y * self.action_scale + self.action_bias

        # Jacobian correction: tanh + scaling changes the probability density,
        # so subtract log|da/dx| = log(scale * (1 - tanh^2(x))). The EPSILON
        # keeps the log finite when tanh saturates toward +-1.
        log_prob = normal.log_prob(x)
        log_prob -= torch.log(self.action_scale * (1 - y.pow(2)) + EPSILON)
        # Joint log-prob of a multi-dim action = sum of per-dim log-probs.
        log_prob = log_prob.sum(dim=1, keepdim=True)

        # Deterministic action (no noise) for evaluation / demo.
        mean_action = torch.tanh(mean) * self.action_scale + self.action_bias

        return action, log_prob, mean_action


class Critic(nn.Module):
    """
    Twin Q-network for SAC.

    Holds two independent Q-functions (Q1, Q2) inside one module. Each takes
    the concatenated state-action pair and estimates a scalar Q-value. Using
    two critics and taking their minimum in the target reduces the
    overestimation bias of a single Q-network.

    Input:  state  shape (batch_size, n_states)
            action shape (batch_size, n_actions)
    Output: q1, q2 each shape (batch_size, 1)
    """

    def __init__(self, n_states, n_actions, hidden_dim=256):
        super(Critic, self).__init__()

        # Q1: two hidden layers (per Ch13 slide), state and action concatenated.
        self.q1_layer1 = nn.Linear(n_states + n_actions, hidden_dim)
        self.q1_layer2 = nn.Linear(hidden_dim, hidden_dim)
        self.q1_output = nn.Linear(hidden_dim, 1)

        # Q2: identical architecture, independent weights.
        self.q2_layer1 = nn.Linear(n_states + n_actions, hidden_dim)
        self.q2_layer2 = nn.Linear(hidden_dim, hidden_dim)
        self.q2_output = nn.Linear(hidden_dim, 1)

    def forward(self, state, action):
        x = torch.cat([state, action], dim=1)

        q1 = F.relu(self.q1_layer1(x))
        q1 = F.relu(self.q1_layer2(q1))
        q1 = self.q1_output(q1)

        q2 = F.relu(self.q2_layer1(x))
        q2 = F.relu(self.q2_layer2(q2))
        q2 = self.q2_output(q2)

        return q1, q2


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


class SACAgent:
    """
    Soft Actor-Critic agent: one squashed-Gaussian actor plus twin critics
    with their target networks. SAC differs from TD3 in three ways: the
    policy is stochastic (entropy is the exploration mechanism, so no OU
    noise), both the target value and the actor loss carry an entropy bonus
    -alpha * log pi, and there is no target actor (the next action is sampled
    fresh from the current policy).
    """

    def __init__(self, n_states, n_actions, action_low, action_high, device,
                 lr=5e-4, gamma=0.99, tau=0.005, alpha=0.2):
        self.device = device
        self.gamma = gamma
        self.tau = tau
        self.alpha = alpha

        # Actor + twin critics (Q1, Q2 live inside one Critic module).
        self.actor  = Actor(n_states, n_actions, action_low, action_high).to(device)
        self.critic = Critic(n_states, n_actions).to(device)

        # Only the critic has a target network; SAC has no target actor.
        self.critic_target = Critic(n_states, n_actions).to(device)
        self.critic_target.load_state_dict(self.critic.state_dict())

        self.actor_optimizer  = optim.Adam(self.actor.parameters(),  lr=lr)
        self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=lr)

    def select_action(self, state, evaluate=False):
        state_t = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            action, _, mean_action = self.actor.sample(state_t)
        # Evaluation uses the deterministic mean action (no sampling noise).
        chosen = mean_action if evaluate else action
        return chosen.cpu().numpy()[0]

    def update(self, buffer, batch_size):
        states, actions, rewards, next_states, dones = [
            t.to(self.device) for t in buffer.sample(batch_size)
        ]

        # ----- Critic update -----
        with torch.no_grad():
            # Next action is sampled from the CURRENT policy (no target actor),
            # and its log-prob feeds the entropy bonus in the soft target.
            next_actions, next_log_probs, _ = self.actor.sample(next_states)
            target_q1, target_q2 = self.critic_target(next_states, next_actions)
            target_q = torch.min(target_q1, target_q2) - self.alpha * next_log_probs
            target_q = rewards + self.gamma * (1 - dones) * target_q

        current_q1, current_q2 = self.critic(states, actions)
        critic_loss = F.mse_loss(current_q1, target_q) + F.mse_loss(current_q2, target_q)

        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        self.critic_optimizer.step()

        # ----- Actor update -----
        # Resample actions for the current states so the gradient flows through
        # the reparameterized policy; maximize Q while staying high-entropy.
        new_actions, log_probs, _ = self.actor.sample(states)
        q1, q2 = self.critic(states, new_actions)
        min_q = torch.min(q1, q2)
        actor_loss = (self.alpha * log_probs - min_q).mean()

        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()

        # ----- Soft update of the critic target only -----
        for param, target in zip(self.critic.parameters(), self.critic_target.parameters()):
            target.data.copy_(self.tau * param.data + (1 - self.tau) * target.data)


def evaluate_policy(agent, env, n_episodes=5):
    """Run the deterministic policy for n_episodes and return the mean reward."""
    total = 0.0
    for _ in range(n_episodes):
        state, _ = env.reset()
        for _ in count():
            action = agent.select_action(state, evaluate=True)
            state, reward, terminated, truncated, _ = env.step(action)
            total += reward
            if terminated or truncated:
                break
    return total / n_episodes


def plot_results(episode_rewards, episode_lengths, eval_timesteps, eval_rewards,
                 total_timesteps, show_result=False):
    if not show_result and not SHOW_TRAINING_PROGRESS:
        return

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

    rewards_t = np.array(episode_rewards)
    lengths_t = np.array(episode_lengths)

    # Episode Rewards
    ax1.set_title('Episode Rewards')
    ax1.set_xlabel('Episode')
    ax1.set_ylabel('Reward')
    ax1.plot(rewards_t, 'b-', alpha=0.4, linewidth=1)
    if len(rewards_t) >= 50:
        means = np.convolve(rewards_t, np.ones(50)/50, mode='valid')
        ax1.plot(range(49, len(rewards_t)), means, 'r-', linewidth=2, label='50-ep avg')
        ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Episode Lengths
    ax2.set_title('Episode Lengths')
    ax2.set_xlabel('Episode')
    ax2.set_ylabel('Steps')
    ax2.plot(lengths_t, 'g-', alpha=0.4, linewidth=1)
    if len(lengths_t) >= 50:
        means_l = np.convolve(lengths_t, np.ones(50)/50, mode='valid')
        ax2.plot(range(49, len(lengths_t)), means_l, 'r-', linewidth=2, label='50-ep avg')
        ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Evaluation Performance
    ax3.set_title('Evaluation Performance')
    ax3.set_xlabel('Timesteps')
    ax3.set_ylabel('Mean Reward')
    ax3.plot(eval_timesteps, eval_rewards, 'ro-', markersize=4)
    ax3.grid(True, alpha=0.3)

    # Recent Rewards Distribution
    ax4.set_title('Recent Rewards Distribution')
    ax4.set_xlabel('Reward')
    ax4.set_ylabel('Frequency')
    recent = rewards_t[-100:] if len(rewards_t) >= 100 else rewards_t
    if len(recent) > 0:
        ax4.hist(recent, bins=20, color='purple', alpha=0.7)
        mean_r = float(recent.mean())
        ax4.axvline(mean_r, color='red', linestyle='--', label=f'Mean: {mean_r:.1f}')
        ax4.legend()
    ax4.grid(True, alpha=0.3)

    fig.suptitle(f'Training Statistics | Episodes: {len(rewards_t)} | Timesteps: {total_timesteps}',
                 fontweight='bold')
    plt.tight_layout()

    if show_result:
        os.makedirs("results", exist_ok=True)
        plt.savefig("results/sac_results.png", dpi=150, bbox_inches="tight")

    if SHOW_TRAINING_PROGRESS:
        plt.pause(0.001)
    else:
        plt.close()


if __name__ == "__main__":

    env_temp = CircleTrackingEnv()
    n_states     = env_temp.observation_space.shape[0]
    n_actions    = env_temp.action_space.shape[0]
    action_low   = env_temp.action_space.low
    action_high  = env_temp.action_space.high
    env_temp.close()

    print(f"Environment: CircleTrackingEnv")
    print(f"State space:  {n_states}")
    print(f"Action space: {n_actions}")
    print(f"Action low:   {action_low}")
    print(f"Action high:  {action_high}")

    device = torch.device(
        "cuda" if torch.cuda.is_available() else
        "mps"  if torch.backends.mps.is_available() else
        "cpu"
    )

    MODEL_SAVE_DIR = "sac_models"
    ACTOR_PATH     = os.path.join(MODEL_SAVE_DIR, "actor_model.pth")
    CRITIC_PATH    = os.path.join(MODEL_SAVE_DIR, "critic_model.pth")
    TRAINING_PATH  = os.path.join(MODEL_SAVE_DIR, "training_info.pth")

    ###########################################################################
    # Mode Selection
    ###########################################################################
    print("=" * 60)
    print("SAC Mobile Robot Line Tracking - Mode Selection")
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

        agent = SACAgent(n_states, n_actions, action_low, action_high, device)
        agent.actor.load_state_dict(torch.load(ACTOR_PATH, map_location=device))
        agent.actor.eval()

        env = CircleTrackingEnv(render_mode="human")

        for i_episode in range(10):
            state, _ = env.reset()
            total_reward = 0
            for t in count():
                action = agent.select_action(state, evaluate=True)
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
        print("=== TRAINING MODE (SAC) ===")
        print("=" * 50)
        print("Starting SAC training")

        SHOW_GAME_DURING_TRAINING = False
        SHOW_TRAINING_PROGRESS    = False

        LR              = 5e-4
        GAMMA           = 0.99
        TAU             = 0.005
        ALPHA           = 0.2
        BATCH_SIZE      = 256
        BUFFER_CAPACITY = 200000
        WARMUP_STEPS    = 1000
        TOTAL_TIMESTEPS = 300000
        EVAL_FREQ       = 5000
        N_EVAL_EPISODES = 5

        env      = CircleTrackingEnv(render_mode="human" if SHOW_GAME_DURING_TRAINING else None)
        eval_env = CircleTrackingEnv()

        agent  = SACAgent(n_states, n_actions, action_low, action_high, device,
                          lr=LR, gamma=GAMMA, tau=TAU, alpha=ALPHA)
        buffer = ReplayBuffer(BUFFER_CAPACITY)

        episode_rewards = []
        episode_lengths = []
        eval_timesteps  = []
        eval_rewards    = []
        total_steps     = 0
        i_episode       = 0

        if SHOW_TRAINING_PROGRESS:
            plt.ion()

        while total_steps < TOTAL_TIMESTEPS:
            state, _ = env.reset()
            episode_reward = 0

            for t in count():
                # Warmup: random actions to fill the buffer before learning.
                if total_steps < WARMUP_STEPS:
                    action = env.action_space.sample()
                else:
                    action = agent.select_action(state)

                next_state, reward, terminated, truncated, _ = env.step(action)
                # Only a true terminal (robot drifted too far) zeroes the future
                # value. Hitting the 200-step limit is a time-limit truncation,
                # not a real ending, so it must still bootstrap from next_state.
                done = terminated
                total_steps += 1
                episode_reward += reward

                buffer.push(state, action, reward, next_state, float(done))
                state = next_state

                if len(buffer) >= BATCH_SIZE and total_steps >= WARMUP_STEPS:
                    agent.update(buffer, BATCH_SIZE)

                if total_steps % EVAL_FREQ == 0:
                    mean_eval = evaluate_policy(agent, eval_env, N_EVAL_EPISODES)
                    eval_timesteps.append(total_steps)
                    eval_rewards.append(mean_eval)

                if terminated or truncated:
                    break

            episode_rewards.append(episode_reward)
            episode_lengths.append(t + 1)
            i_episode += 1
            plot_results(episode_rewards, episode_lengths, eval_timesteps, eval_rewards, total_steps)

            if i_episode % 50 == 0:
                recent = episode_rewards[-50:]
                avg = sum(recent) / len(recent)
                print(f"Episode {i_episode} | step {total_steps}/{TOTAL_TIMESTEPS} "
                      f"| last-50 avg reward = {avg:.1f}")

        os.makedirs(MODEL_SAVE_DIR, exist_ok=True)
        torch.save(agent.actor.state_dict(),  ACTOR_PATH)
        torch.save(agent.critic.state_dict(), CRITIC_PATH)
        torch.save({'episode_rewards': episode_rewards, 'episode_lengths': episode_lengths,
                    'eval_timesteps': eval_timesteps, 'eval_rewards': eval_rewards,
                    'total_steps': total_steps}, TRAINING_PATH)
        print(f"Models saved to {MODEL_SAVE_DIR}/")

        print("Complete")
        plot_results(episode_rewards, episode_lengths, eval_timesteps, eval_rewards,
                     total_steps, show_result=True)
        if SHOW_TRAINING_PROGRESS:
            plt.ioff()
            plt.show()
        env.close()
        eval_env.close()
