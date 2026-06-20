# evaluate.py
"""
Compares PPO agent against heuristic baselines using
the updated 16-dimensional observation environment.
"""

import numpy as np
from stable_baselines3 import PPO
from rl_model.abr_env import ABREnv


# ------------------------------------------------------------------
# Heuristic policies
# ------------------------------------------------------------------

def fixed_policy(bitrate_index: int):
    """Always pick the same bitrate level."""
    def policy(obs, env):
        return bitrate_index
    return policy


def throughput_policy(obs, env):
    """
    Pick the highest bitrate that fits in the estimated throughput.
    Uses the most recent normalised throughput from the observation.
    """
    # obs[4] = most recent throughput (last element of 5-history window)
    throughput_bps = float(obs[4]) * env.MAX_THROUGHPUT_BPS

    chosen = 0
    for i, bps in enumerate(env.BITRATES_BPS):
        # Use 90% of available throughput as safety margin
        if bps < throughput_bps * 0.9:
            chosen = i

    return chosen


def buffer_based_policy(obs, env):
    """
    Simple buffer-based policy:
    - Buffer very low  (<5s)  → lowest  quality
    - Buffer medium    (5-20s)→ mid     quality
    - Buffer high      (>20s) → highest quality
    """
    # obs[10] = buffer level (normalised by BUFFER_MAX_S = 60s)
    buffer_s = float(obs[10]) * env.BUFFER_MAX_S

    if buffer_s < 5.0:
        return 0
    elif buffer_s < 20.0:
        return 1
    else:
        return 2


# ------------------------------------------------------------------
# Evaluation runner
# ------------------------------------------------------------------

def evaluate_policy(
    policy_fn,
    env: ABREnv,
    n_episodes: int = 100,
    ppo_model=None,
    deterministic: bool = True,
) -> dict:
    """
    Runs n_episodes and returns reward statistics.

    For PPO, pass the loaded model as ppo_model.
    For heuristic policies, pass a callable as policy_fn.
    """

    all_rewards       = []
    all_rebuffers     = []
    all_quality_avgs  = []
    all_switches      = []

    for ep in range(n_episodes):
        obs, _ = env.reset()
        done   = False
        total_reward    = 0.0
        total_rebuffer  = 0.0
        total_quality   = 0.0
        total_switches  = 0
        last_action     = 1
        steps           = 0

        while not done:
            if ppo_model is not None:
                action, _ = ppo_model.predict(obs, deterministic=deterministic)
                action = int(action)
            else:
                action = policy_fn(obs, env)

            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated

            total_reward   += reward
            total_rebuffer += info["rebuffer_time_s"]
            total_quality  += info["selected_kbps"]
            if action != last_action:
                total_switches += 1
            last_action = action
            steps      += 1

        all_rewards.append(total_reward)
        all_rebuffers.append(total_rebuffer)
        all_quality_avgs.append(total_quality / max(steps, 1))
        all_switches.append(total_switches)

    return {
        "mean_reward"     : float(np.mean(all_rewards)),
        "std_reward"      : float(np.std(all_rewards)),
        "best_reward"     : float(np.max(all_rewards)),
        "worst_reward"    : float(np.min(all_rewards)),
        "mean_rebuffer_s" : float(np.mean(all_rebuffers)),
        "mean_quality_kbps": float(np.mean(all_quality_avgs)),
        "mean_switches"   : float(np.mean(all_switches)),
    }


def print_result(name: str, result: dict):
    print(f"\n{'='*50}")
    print(f"  {name}")
    print(f"{'='*50}")
    print(f"  Mean Reward       : {result['mean_reward']:+.2f}")
    print(f"  Std  Reward       : {result['std_reward']:.2f}")
    print(f"  Best Reward       : {result['best_reward']:+.2f}")
    print(f"  Worst Reward      : {result['worst_reward']:+.2f}")
    print(f"  Mean Rebuffer (s) : {result['mean_rebuffer_s']:.3f}")
    print(f"  Mean Quality(Kbps): {result['mean_quality_kbps']:.0f}")
    print(f"  Mean Switches     : {result['mean_switches']:.1f}")


def main():
    N_EPISODES = 100

    env = ABREnv(trace_folder="cooked_test_traces")

    print(f"\nEvaluating over {N_EPISODES} episodes each...\n")

    # Heuristics
    policies = {
        "Fixed 300 Kbps"  : fixed_policy(0),
        "Fixed 800 Kbps"  : fixed_policy(1),
        "Fixed 1500 Kbps" : fixed_policy(2),
        "Throughput-Based": throughput_policy,
        "Buffer-Based"    : buffer_based_policy,
    }

    results = {}
    for name, fn in policies.items():
        results[name] = evaluate_policy(fn, env, n_episodes=N_EPISODES)
        print_result(name, results[name])

    # PPO model
    try:
        ppo_model = PPO.load("checkpoints/best/best_model")
        print("\nLoaded best model from checkpoints/best/best_model.zip")
    except FileNotFoundError:
        try:
            ppo_model = PPO.load("ppo_abr_model_final")
            print("\nLoaded final model from ppo_abr_model_final.zip")
        except FileNotFoundError:
            print("\nNo trained model found. Skipping PPO evaluation.")
            ppo_model = None

    if ppo_model is not None:
        results["PPO (RL Agent)"] = evaluate_policy(
            None, env,
            n_episodes  = N_EPISODES,
            ppo_model   = ppo_model,
            deterministic = True,
        )
        print_result("PPO (RL Agent)", results["PPO (RL Agent)"])

    # ---- Summary table ----
    print(f"\n{'='*60}")
    print(f"{'FINAL COMPARISON':^60}")
    print(f"{'='*60}")
    print(f"{'Policy':<20} {'Mean Reward':>12} {'Rebuffer(s)':>12} {'Qual(Kbps)':>12} {'Switches':>10}")
    print(f"{'-'*60}")
    for name, r in results.items():
        print(
            f"{name:<20} "
            f"{r['mean_reward']:>+12.2f} "
            f"{r['mean_rebuffer_s']:>12.3f} "
            f"{r['mean_quality_kbps']:>12.0f} "
            f"{r['mean_switches']:>10.1f}"
        )
    print(f"{'='*60}")


if __name__ == "__main__":
    main()































"""
import numpy as np
from stable_baselines3 import PPO

from rl_model.abr_env import ABREnv


EPISODES = 50


def evaluate_policy(policy_name, action_fn):

    env = ABREnv()

    rewards = []

    for episode in range(EPISODES):

        obs, _ = env.reset()

        done = False
        total_reward = 0

        while not done:

            action = action_fn(obs)

            obs, reward, terminated, truncated, info = env.step(action)

            done = terminated or truncated

            total_reward += reward

        rewards.append(total_reward)

    rewards = np.array(rewards)

    print(f"\n===== {policy_name} =====")

    print(
        f"Mean Reward: {rewards.mean():.2f}"
    )

    print(
        f"Std Reward: {rewards.std():.2f}"
    )

    print(
        f"Best Reward: {rewards.max():.2f}"
    )

    print(
        f"Worst Reward: {rewards.min():.2f}"
    )

    return rewards.mean()


def evaluate_ppo():

    env = ABREnv()

    model = PPO.load(
        "checkpoints/best_model/best_model"
    )

    rewards = []

    for episode in range(EPISODES):

        obs, _ = env.reset()

        done = False
        total_reward = 0

        while not done:

            action, _ = model.predict(
                obs,
                deterministic=True
            )

            obs, reward, terminated, truncated, info = env.step(action)

            done = terminated or truncated

            total_reward += reward

        rewards.append(total_reward)

    rewards = np.array(rewards)

    print("\n===== PPO =====")

    print(
        f"Mean Reward: {rewards.mean():.2f}"
    )

    print(
        f"Std Reward: {rewards.std():.2f}"
    )

    print(
        f"Best Reward: {rewards.max():.2f}"
    )

    print(
        f"Worst Reward: {rewards.min():.2f}"
    )

    return rewards.mean()


# ---------------------------------------------------
# Baselines
# ---------------------------------------------------

def fixed_300(obs):
    return 0


def fixed_800(obs):
    return 1


def fixed_1500(obs):
    return 2


def throughput_based(obs):

    throughput_bps = obs[0] * 5_000_000

    if throughput_bps < 600_000:
        return 0

    elif throughput_bps < 1_200_000:
        return 1

    else:
        return 2


if __name__ == "__main__":

    results = {}

    results["Fixed300"] = evaluate_policy(
        "Fixed 300 kbps",
        fixed_300
    )

    results["Fixed800"] = evaluate_policy(
        "Fixed 800 kbps",
        fixed_800
    )

    results["Fixed1500"] = evaluate_policy(
        "Fixed 1500 kbps",
        fixed_1500
    )

    results["Throughput"] = evaluate_policy(
        "Throughput-Based",
        throughput_based
    )

    results["PPO"] = evaluate_ppo()

    print("\n==============================")
    print("FINAL COMPARISON")
    print("==============================")

    for name, score in results.items():

        print(
            f"{name:15s}: {score:.2f}"
        )
"""