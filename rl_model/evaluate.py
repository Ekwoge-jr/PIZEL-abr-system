import numpy as np
from stable_baselines3 import PPO

from rl_model.abr_env import ABREnv


def evaluate(model_path, episodes=50):

    env = ABREnv(trace_folder="cooked_test_traces")

    model = PPO.load(model_path, env=env)

    rewards = []

    #action_counts = [0, 0, 0]
    action_counts = [0] * env.action_space.n

    for episode in range(episodes):

        obs, _ = env.reset()

        done = False
        total_reward = 0


        while not done:

            action, _ = model.predict(
                obs,
                deterministic=True
            )

            action_counts[action] += 1

            obs, reward, terminated, truncated, info = env.step(action)

            done = terminated or truncated

            total_reward += reward

        rewards.append(total_reward)

        print(
            f"Episode {episode + 1}: "
            f"Reward = {total_reward:.2f}"
        )

    rewards = np.array(rewards)

    print("\n========== RESULTS ==========")

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


    print("\nAction Distribution")

    print(
        f"300kbps : {action_counts[0]}"
    )

    print(
        f"800kbps : {action_counts[1]}"
    )

    print(
        f"1500kbps : {action_counts[2]}"
    )

    return rewards


if __name__ == "__main__":

    evaluate(
        "checkpoints/best/best_model",
        episodes=50
    )