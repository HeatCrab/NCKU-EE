import math
import random
import matplotlib
import matplotlib.pyplot as plt
from collections import namedtuple, deque
from itertools import count
import time
import numpy as np
import os

import gymnasium as gym

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

# DQN model
class DQN(nn.Module):
    def __init__(self, state_size, action_size):
        super(DQN, self).__init__()
        self.layer1 = nn.Linear(state_size, 128)
        self.layer2 = nn.Linear(128, 128)
        self.layer3 = nn.Linear(128, action_size)

    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        return self.layer3(x)
    
class ReplayMemory(object):
    def __init__(self, capacity):
        self.memory = deque([], maxlen=capacity)

    def push(self, *args):
        """ Save a transition """
        self.memory.append(Transition(*args))
    
    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)


def select_action(state):
    """ Epsilon-greedy action selection """
    global steps_done
    sample = random.random()
    eps_threshold = EPS_END + (EPS_START - EPS_END) * \
        math.exp(-1. * steps_done / EPS_DECAY)
    steps_done += 1
    if sample > eps_threshold:
        with torch.no_grad():
            # policy_net(state).max(1) returns the max value and its index for each row.
            # .indices.view(1, 1) extracts the action index and reshapes it to [1, 1].
            return policy_net(state).max(1).indices.view(1, 1)
    else:
        return torch.tensor([[env.action_space.sample()]], device=device, dtype=torch.long)


def optimize_model():
    """ Perform one step of optimization on the policy network """
    if len(memory) < BATCH_SIZE:
        return

    transitions = memory.sample(BATCH_SIZE)
    # Convert a batch-array of Transitions into a Transition of batch-arrays.
    batch = Transition(*zip(*transitions))

    # Compute a mask of non-final states to distinguish which next_state is not None.
    non_final_mask = torch.tensor(
        tuple(map(lambda s: s is not None, batch.next_state)),
        device=device, dtype=torch.bool
    )
    non_final_next_states = torch.cat([s for s in batch.next_state if s is not None])

    state_batch = torch.cat(batch.state)
    action_batch = torch.cat(batch.action)
    reward_batch = torch.cat(batch.reward)

    # Q(s_t, a) - Q-value from policy_net for the action taken at the current state.
    state_action_values = policy_net(state_batch).gather(1, action_batch)

    # Double DQN: policy_net selects the best action, target_net evaluates its value.
    # y = r + γ * Q_target(s', argmax_a' Q_policy(s', a'))
    next_state_values = torch.zeros(BATCH_SIZE, device=device)
    with torch.no_grad():
        best_actions = policy_net(non_final_next_states).max(1).indices.unsqueeze(1)
        next_state_values[non_final_mask] = target_net(non_final_next_states).gather(1, best_actions).squeeze(1)
    # Bellman target: r + γ * V(s_{t+1})
    expected_state_action_values = (next_state_values * Discount_Factor) + reward_batch

    # Huber loss (SmoothL1Loss)
    criterion = nn.SmoothL1Loss()
    loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))

    # Optimize policy network
    optimizer.zero_grad()
    loss.backward()
    # In-place gradient clipping to prevent exploding gradients.
    torch.nn.utils.clip_grad_value_(policy_net.parameters(), 100)
    optimizer.step()


def plot_durations(show_result=False):
    """ Plot training progress """
    if not SHOW_TRAINING_PROGRESS:
        return

    plt.figure(1)
    plt.clf()

    durations_t = torch.tensor(episode_durations, dtype=torch.float)

    if show_result:
        plt.title('Final Durations')
    else:
        plt.title('Training...')

    plt.xlabel('Episode')
    plt.ylabel('Duration')
    plt.plot(durations_t.numpy(), 'b-', alpha=0.7, linewidth=1)

    # Take 100 episode averages and plot them too
    if len(durations_t) >= 100:
        means = durations_t.unfold(0, 100, 1).mean(1).view(-1)
        means = torch.cat((torch.zeros(99), means))
        plt.plot(means.numpy(), 'r-', linewidth=2, label='100-episode average')
        plt.legend()

    # Add Objective line
    plt.axhline(y=500, color='g', linestyle='--', alpha=0.7, label='Target (500)')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.pause(0.001)  # pause a bit so that plots are updated

# main function
if __name__ == "__main__":

    # ////////////////////////// move up to here ///////////////////////////
    Transition = namedtuple('Transition', ('state', 'action', 'next_state', 'reward'))

    # Get environment info
    env_temp = gym.make("CartPole-v1")
    n_actions = env_temp.action_space.n
    state, info = env_temp.reset()
    n_observations = len(state)
    env_temp.close()

    print(f"Environment: CartPole-v1")
    print(f"State space: {n_observations}")
    print(f"Action space: {n_actions}")

    # if GPU is to be used
    device = torch.device(
        "cuda" if torch.cuda.is_available() else
        "mps" if torch.backends.mps.is_available() else
        "cpu"    
    )

    # Initialize network
    policy_net = DQN(n_observations, n_actions).to(device)
    target_net = DQN(n_observations, n_actions).to(device)

    # model preservation path
    MODEL_SAVE_DIR = "ddqn_models"
    POLICY_MODEL_PATH = os.path.join(MODEL_SAVE_DIR, "policy_model.pth")
    TARGET_MODEL_PATH = os.path.join(MODEL_SAVE_DIR, "target_model.pth")
    TRAINING_INFO_PATH = os.path.join(MODEL_SAVE_DIR, "training_info.pth")
    # ////////////////////////// move up to here ///////////////////////////

    ###########################################################################
    # Mode Selection
    ###########################################################################
    print("=" * 60)
    print("DDQN CartPole - Mode Selection")
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

        # Load trained networks
        if not os.path.exists(POLICY_MODEL_PATH):
            print(f"Error: model not found at {POLICY_MODEL_PATH}")
            exit()

        policy_net.load_state_dict(torch.load(POLICY_MODEL_PATH, map_location=device))
        target_net.load_state_dict(torch.load(TARGET_MODEL_PATH, map_location=device))
        policy_net.eval()
        target_net.eval()

        # Demo always runs with rendering enabled.
        env = gym.make("CartPole-v1", render_mode="human")

        num_demo_episodes = 10
        for i_episode in range(num_demo_episodes):
            state, info = env.reset()
            state = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
            total_reward = 0

            for t in count():
                # Demo uses a pure greedy policy (no exploration).
                with torch.no_grad():
                    action = policy_net(state).max(1).indices.view(1, 1)

                observation, reward, terminated, truncated, _ = env.step(action.item())
                total_reward += reward
                done = terminated or truncated

                if done:
                    print(f"Episode {i_episode + 1}: duration = {t + 1}, total reward = {total_reward}")
                    break

                state = torch.tensor(observation, dtype=torch.float32, device=device).unsqueeze(0)
                time.sleep(0.02)

        env.close()

    # ////////// TRAIN //////////
    elif MODE == "TRAIN":


        print(f"\n{'=' * 50}")
        print("=== TRAINING MODE (Double DQN) ===")
        print("=" * 50)
        print("Starting Double DQN training")
    
        # Training Configurations
        SHOW_GAME_DURING_TRAINING = False   # Whether to render the game during training
        SHOW_TRAINING_PROGRESS = False      # Whether to show the training progress chart

        # Rendering parameters (used only when SHOW_GAME_* is True)
        RENDER_EVERY = 10       # Render the game every N episodes (during training)
        RENDER_DELAY = 0.02     # Delay between rendered frames (seconds)

        # Traning Parameters
        BATCH_SIZE = 128
        Discount_Factor = 0.99
        EPS_START = 0.9
        EPS_END = 0.01
        EPS_DECAY = 2500
        TAU = 0.005
        LR = 3e-4
    
        steps_done = 0
    
        # Create different environments based on rendering config.
        if SHOW_GAME_DURING_TRAINING:
            env = gym.make("CartPole-v1", render_mode="human")
        else:
            env = gym.make("CartPole-v1")

        # Initialize target network
        target_net.load_state_dict(policy_net.state_dict())
    
        # Optimizer and memory
        # amsgrad=True enables the AMSGrad variant, which mitigates non-convergence issues of Adam in some cases.
        optimizer = optim.AdamW(policy_net.parameters(), lr=LR, amsgrad=True)
        memory = ReplayMemory(10000)
    
        episode_durations = []

        ###########################################################################
        # Main training loop
        ###########################################################################
        if torch.cuda.is_available() or torch.backends.mps.is_available():
            num_episodes = 1200
        else:
            num_episodes = 50

        if SHOW_TRAINING_PROGRESS:
            plt.ion()

        for i_episode in range(num_episodes):
            # Initialize environment and get its state
            state, info = env.reset()
            state = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)

            for t in count():
                action = select_action(state)
                observation, reward, terminated, truncated, _ = env.step(action.item())
                reward = torch.tensor([reward], device=device)
                done = terminated or truncated

                if terminated:
                    next_state = None
                else:
                    next_state = torch.tensor(observation, dtype=torch.float32, device=device).unsqueeze(0)

                # Store transition in replay memory
                memory.push(state, action, next_state, reward)

                # Move to next state
                state = next_state

                # Perform one step of optimization on the policy network
                optimize_model()

                # Soft update of target network's weights:
                # θ′ ← τ θ + (1 − τ) θ′
                target_net_state_dict = target_net.state_dict()
                policy_net_state_dict = policy_net.state_dict()
                for key in policy_net_state_dict:
                    target_net_state_dict[key] = (
                        policy_net_state_dict[key] * TAU
                        + target_net_state_dict[key] * (1 - TAU)
                    )
                target_net.load_state_dict(target_net_state_dict)

                if done:
                    episode_durations.append(t + 1)
                    plot_durations()
                    break

            # Periodic progress log
            if (i_episode + 1) % 50 == 0:
                recent = episode_durations[-50:]
                avg = sum(recent) / len(recent)
                print(f"Episode {i_episode + 1}/{num_episodes} | last-50 avg duration = {avg:.1f}")

        # Save trained models and training info
        os.makedirs(MODEL_SAVE_DIR, exist_ok=True)
        torch.save(policy_net.state_dict(), POLICY_MODEL_PATH)
        torch.save(target_net.state_dict(), TARGET_MODEL_PATH)
        torch.save(
            {'episode_durations': episode_durations, 'steps_done': steps_done},
            TRAINING_INFO_PATH,
        )
        print(f"Models saved to {MODEL_SAVE_DIR}/")

        print('Complete')
        plot_durations(show_result=True)
        if SHOW_TRAINING_PROGRESS:
            plt.ioff()
            plt.show()
        env.close()



















