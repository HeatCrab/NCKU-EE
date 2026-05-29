import importlib.util
import os
import time
from collections import deque
from itertools import count

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import torch

from stable_baselines3 import SAC
from stable_baselines3.common.callbacks import BaseCallback, CallbackList, EvalCallback
from stable_baselines3.common.monitor import Monitor

# The environment lives in "Mobile Robot.py" (space in the filename), so it
# cannot be imported with a normal import statement; load it by file path.
_env_path = os.path.join(os.path.dirname(__file__), "Mobile Robot.py")
_spec = importlib.util.spec_from_file_location("mobile_robot", _env_path)
mobile_robot = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mobile_robot)
CircleTrackingEnv = mobile_robot.CircleTrackingEnv


class EpisodeLogCallback(BaseCallback):
    """
    Prints a last-N-episode average reward every log_every episodes, matching
    the console log format of the hand-written SAC script so the two runs can
    be compared side by side. Episode statistics come from the Monitor wrapper,
    which injects an "episode" entry into info when an episode ends.
    """

    def __init__(self, log_every=50, total_timesteps=0, verbose=0):
        super().__init__(verbose)
        self.log_every = log_every
        self.total_timesteps = total_timesteps
        self.ep_rewards = deque(maxlen=log_every)
        self.n_episodes = 0

    def _on_step(self):
        for info in self.locals.get("infos", []):
            ep = info.get("episode")
            if ep is not None:
                self.ep_rewards.append(ep["r"])
                self.n_episodes += 1
                if self.n_episodes % self.log_every == 0:
                    avg = sum(self.ep_rewards) / len(self.ep_rewards)
                    print(f"Episode {self.n_episodes} | step {self.num_timesteps}/{self.total_timesteps} "
                          f"| last-{self.log_every} avg reward = {avg:.1f}")
        return True


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

    fig.suptitle(f'SB3 Training Statistics | Episodes: {len(rewards_t)} | Timesteps: {total_timesteps}',
                 fontweight='bold')
    plt.tight_layout()

    if show_result:
        os.makedirs("results", exist_ok=True)
        plt.savefig("results/sb3_results.png", dpi=150, bbox_inches="tight")

    if SHOW_TRAINING_PROGRESS:
        plt.pause(0.001)
    else:
        plt.close()


if __name__ == "__main__":

    env_temp = CircleTrackingEnv()
    print(f"Environment: CircleTrackingEnv")
    print(f"State space:  {env_temp.observation_space.shape[0]}")
    print(f"Action space: {env_temp.action_space.shape[0]}")
    print(f"Action low:   {env_temp.action_space.low}")
    print(f"Action high:  {env_temp.action_space.high}")
    env_temp.close()

    device = "cuda" if torch.cuda.is_available() else "cpu"

    MODEL_SAVE_DIR = "sb3_models"
    MODEL_PATH     = os.path.join(MODEL_SAVE_DIR, "sac_sb3")

    ###########################################################################
    # Mode Selection
    ###########################################################################
    print("=" * 60)
    print("SB3 SAC Mobile Robot Line Tracking - Mode Selection")
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

        if not os.path.exists(MODEL_PATH + ".zip"):
            print(f"Error: model not found at {MODEL_PATH}.zip")
            exit()

        model = SAC.load(MODEL_PATH, device=device)
        env = CircleTrackingEnv(render_mode="human")

        for i_episode in range(10):
            obs, _ = env.reset()
            total_reward = 0
            for t in count():
                action, _ = model.predict(obs, deterministic=True)
                obs, reward, terminated, truncated, _ = env.step(action)
                total_reward += reward
                if terminated or truncated:
                    print(f"Episode {i_episode + 1}: steps = {t + 1}, reward = {total_reward:.1f}")
                    break
                time.sleep(0.02)

        env.close()

    # ////////// TRAIN //////////
    elif MODE == "TRAIN":
        print(f"\n{'=' * 50}")
        print("=== TRAINING MODE (SB3 SAC) ===")
        print("=" * 50)
        print("Starting SB3 SAC training")

        SHOW_TRAINING_PROGRESS = False

        LR              = 5e-4
        GAMMA           = 0.99
        TAU             = 0.005
        ENT_COEF        = 0.2
        BATCH_SIZE      = 256
        BUFFER_CAPACITY = 200000
        WARMUP_STEPS    = 1000
        TOTAL_TIMESTEPS = 300000
        EVAL_FREQ       = 5000
        N_EVAL_EPISODES = 5

        # Monitor records per-episode reward and length for the plot.
        env      = Monitor(CircleTrackingEnv())
        eval_env = Monitor(CircleTrackingEnv())

        # SB3's built-in SAC is the engine; net_arch and ent_coef are pinned to
        # the slide values so the run matches the hand-written implementation.
        model = SAC(
            "MlpPolicy",
            env,
            learning_rate=LR,
            buffer_size=BUFFER_CAPACITY,
            batch_size=BATCH_SIZE,
            tau=TAU,
            gamma=GAMMA,
            ent_coef=ENT_COEF,
            learning_starts=WARMUP_STEPS,
            policy_kwargs=dict(net_arch=[256, 256]),
            device=device,
            verbose=0,
        )

        eval_callback = EvalCallback(
            eval_env,
            best_model_save_path=MODEL_SAVE_DIR,
            log_path=MODEL_SAVE_DIR,
            eval_freq=EVAL_FREQ,
            n_eval_episodes=N_EVAL_EPISODES,
            deterministic=True,
            render=False,
            verbose=0,
        )
        log_callback = EpisodeLogCallback(log_every=50, total_timesteps=TOTAL_TIMESTEPS)

        model.learn(total_timesteps=TOTAL_TIMESTEPS,
                    callback=CallbackList([eval_callback, log_callback]))

        # Episode statistics from the Monitor wrapper.
        episode_rewards = env.get_episode_rewards()
        episode_lengths = env.get_episode_lengths()

        # Evaluation statistics collected by the EvalCallback.
        eval_timesteps = list(eval_callback.evaluations_timesteps)
        eval_rewards   = [float(np.mean(r)) for r in eval_callback.evaluations_results]

        os.makedirs(MODEL_SAVE_DIR, exist_ok=True)
        model.save(MODEL_PATH)
        print(f"Model saved to {MODEL_PATH}.zip")

        print("Complete")
        plot_results(episode_rewards, episode_lengths, eval_timesteps, eval_rewards,
                     TOTAL_TIMESTEPS, show_result=True)
        if SHOW_TRAINING_PROGRESS:
            plt.ioff()
            plt.show()
        env.close()
        eval_env.close()
