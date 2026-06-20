# train.py  (IMPROVED VERSION)

import os
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import (
    CheckpointCallback,
    EvalCallback,
    BaseCallback,
)
from rl_model.abr_env import ABREnv


class ABRProgressCallback(BaseCallback):
    """
    Prints a training summary every print_freq timesteps.
    Tracks whether the agent is exploring all 3 actions
    (a key indicator of the risk-averse collapse problem).
    """

    def __init__(self, print_freq: int = 10_000, verbose: int = 0):
        super().__init__(verbose)
        self.print_freq      = print_freq
        self.episode_rewards = []
        self.action_counts   = {0: 0, 1: 0, 2: 0}

    def _on_step(self) -> bool:

        # Track action distribution
        actions = self.locals.get("actions", [])
        for a in np.array(actions).flatten():
            self.action_counts[int(a)] += 1

        # Track episode rewards
        for info in self.locals.get("infos", []):
            if "episode" in info:
                self.episode_rewards.append(info["episode"]["r"])

        if self.num_timesteps % self.print_freq == 0:

            # Action distribution percentage
            total_actions = sum(self.action_counts.values())
            if total_actions > 0:
                pct = {
                    k: v / total_actions * 100
                    for k, v in self.action_counts.items()
                }
                action_str = (
                    f"300Kbps:{pct[0]:.1f}% | "
                    f"800Kbps:{pct[1]:.1f}% | "
                    f"1500Kbps:{pct[2]:.1f}%"
                )
            else:
                action_str = "no actions yet"

            if self.episode_rewards:
                recent = self.episode_rewards[-50:]
                print(
                    f"\n[Step {self.num_timesteps:>7,}] "
                    f"MeanReward={np.mean(recent):+.2f} | "
                    f"Actions: {action_str}"
                )

                # Warn if agent is collapsing to single action
                if pct[0] > 80:
                    print(
                        "  ⚠️  WARNING: Agent choosing 300Kbps "
                        f"{pct[0]:.0f}% of time "
                        "— risk-averse collapse detected. "
                        "Consider increasing ent_coef."
                    )
                elif pct[2] > 60:
                    print(
                        "  ⚠️  WARNING: Agent choosing 1500Kbps "
                        f"{pct[2]:.0f}% of time "
                        "— may be too aggressive."
                    )
                else:
                    print("  ✓ Action distribution looks healthy.")

                # Reset action counts for next window
                self.action_counts = {0: 0, 1: 0, 2: 0}

        return True


def make_env():
    env = ABREnv()
    return Monitor(env)


def main():

    print("=" * 55)
    print("  ABR RL TRAINING — IMPROVED VERSION")
    print("=" * 55)

    print("\nChecking environment...")
    check_env(ABREnv())
    print("Environment check passed.\n")

    os.makedirs("checkpoints/best", exist_ok=True)
    os.makedirs("logs/tensorboard", exist_ok=True)
    os.makedirs("logs/eval",        exist_ok=True)

    N_ENVS = 4
    env      = make_vec_env(make_env, n_envs=N_ENVS)
    eval_env = make_vec_env(make_env, n_envs=1)

    checkpoint_cb = CheckpointCallback(
        save_freq   = max(25_000 // N_ENVS, 1),
        save_path   = "checkpoints/",
        name_prefix = "ppo_abr_improved",
        verbose     = 1,
    )

    eval_cb = EvalCallback(
        eval_env,
        best_model_save_path = "checkpoints/best/",
        log_path             = "logs/eval/",
        eval_freq            = max(15_000 // N_ENVS, 1),
        n_eval_episodes      = 20,
        deterministic        = True,
        verbose              = 1,
    )

    progress_cb = ABRProgressCallback(print_freq=10_000)

    model = PPO(
        policy          = "MlpPolicy",
        env             = env,
        verbose         = 1,

        # ── Learning rate ────────────────────────────────────────
        learning_rate   = 3e-4,

        # ── Rollout ──────────────────────────────────────────────
        n_steps         = 2048,

        # ── Batch and epochs ─────────────────────────────────────
        # Smaller batch + more epochs = more gradient updates
        # per collected experience
        batch_size      = 64,
        n_epochs        = 15,

        # ── Discounting ──────────────────────────────────────────
        gamma           = 0.99,
        gae_lambda      = 0.95,

        # ── PPO clipping ─────────────────────────────────────────
        clip_range      = 0.2,
        max_grad_norm   = 0.5,

        # ── ENTROPY (KEY CHANGE) ──────────────────────────────────
        # Increased from 0.01 to 0.05 to force the agent
        # to keep exploring all 3 actions rather than
        # collapsing to always choosing 300 Kbps.
        ent_coef        = 0.05,

        # ── Value function ────────────────────────────────────────
        vf_coef         = 0.5,

        # ── Network (wider for the 16-dim state) ─────────────────
        policy_kwargs   = dict(net_arch=[128, 128]),

        tensorboard_log = "logs/tensorboard/",
    )

    print("\nKey hyperparameters:")
    print(f"  ent_coef      : 0.05  (was 0.01 — more exploration)")
    print(f"  REBUFFER_COEF : 2.5   (was 4.0  — less conservative)")
    print(f"  QUALITY_SCALE : 2.5   (NEW     — rewards quality more)")
    print(f"  REWARD_CLIP   : 50.0  (was 20.0 — wider reward range)")
    print(f"  batch_size    : 64    (was 128  — more gradient steps)")
    print(f"  n_epochs      : 15    (was 10   — more learning)")
    print(f"  N_ENVS        : {N_ENVS}")
    print(f"  Total steps   : 500,000\n")

    model.learn(
        total_timesteps = 500_000,
        progress_bar    = True,
        callback        = [checkpoint_cb, eval_cb, progress_cb],
    )

    model.save("ppo_abr_model_improved")
    print("\nTraining complete.")
    print("Saved: ppo_abr_model_improved.zip")
    print("Best : checkpoints/best/best_model.zip")


if __name__ == "__main__":
    main()


























"""
import os
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.monitor import Monitor

from rl_model.abr_env import ABREnv


def make_env():
    env = ABREnv()
    env = Monitor(env)   # Wrap to log episode reward/length correctly
    return env


def main():
    # ---- Sanity check the environment first ----
    check_env_instance = ABREnv()
    check_env(check_env_instance)
    print("Environment check passed.\n")

    # ---- Vectorized envs speed up PPO data collection ----
    n_envs = 4
    env = make_vec_env(make_env, n_envs=n_envs)

    # Separate eval environment (not used for training data)
    eval_env = make_vec_env(make_env, n_envs=1)

    os.makedirs("checkpoints", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    checkpoint_callback = CheckpointCallback(
        save_freq=20_000,
        save_path="checkpoints/",
        name_prefix="ppo_abr",
    )

    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path="checkpoints/best_model",
        log_path="logs/eval",
        eval_freq=10_000,
        n_eval_episodes=5,
        deterministic=True,
    )

    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.03,          # encourages exploration; re-enabled
        vf_coef=0.5,
        max_grad_norm=0.5,      # CRITICAL: clips gradient norm,
                                 # prevents the loss explosions you saw
        tensorboard_log="logs/tensorboard",
        policy_kwargs=dict(net_arch=[64, 64]),
    )

    model.learn(
        total_timesteps=500_000,
        progress_bar=True,
        callback=[checkpoint_callback, eval_callback],
    )

    model.save("ppo_abr_model_final")
    print("Training complete. Model saved as ppo_abr_model_final.zip")


if __name__ == "__main__":
    main()
"""





































"""
from stable_baselines3 import PPO
from rl_model.abr_env import ABREnv
from stable_baselines3.common.env_checker import check_env




env = ABREnv()
check_env(env)


model = PPO(

    ## creates a neural network
    "MlpPolicy",
    #

    env,

    verbose=1,

    ## how fast PPO updates
    learning_rate=0.0003,

    n_steps=2048,

    batch_size=64,

    ## future reward importance
    gamma=0.99,


    #ent_coef=0.01

)


model.learn(

    ## number of interactions with the env
    total_timesteps=500000,
    progress_bar=True

)


model.save(

    "ppo_abr_model"
)

print("Training Complete")
"""