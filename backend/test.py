
#from services.ffmpeg_pipeline import generate_dash_stream
#from services.roi_analyzer import ROIAnalyzer
#import cv2

"""
from stable_baselines3 import PPO

model = PPO.load("checkpoints/best/best_model.zip")

print(model.policy)
"""



# robust_evaluation.py
"""
Run multiple evaluation passes with different random seeds
to confirm Run 3's rebuffer/switch advantage is consistent
and not a lucky draw of episodes.
"""
"""
import numpy as np
from stable_baselines3 import PPO
from rl_model.abr_env import ABREnv
from rl_model.evaluate_baselines import evaluate_policy, throughput_policy

N_SEEDS    = 5
N_EPISODES = 100

ppo_model = PPO.load("checkpoints/best/best_model")
env       = ABREnv(trace_folder="cooked_test_traces")

records = {"ppo": [], "throughput": []}

for seed in range(N_SEEDS):
    np.random.seed(seed)

    ppo_result = evaluate_policy(
        None, env, n_episodes=N_EPISODES,
        ppo_model=ppo_model, deterministic=True
    )
    tp_result = evaluate_policy(
        throughput_policy, env, n_episodes=N_EPISODES
    )

    records["ppo"].append(ppo_result)
    records["throughput"].append(tp_result)

    print(f"\nSeed {seed}:")
    print(f"  PPO        : reward={ppo_result['mean_reward']:+.2f} | "
          f"rebuffer={ppo_result['mean_rebuffer_s']:.2f}s | "
          f"quality={ppo_result['mean_quality_kbps']:.0f}Kbps | "
          f"switches={ppo_result['mean_switches']:.1f}")
    print(f"  Throughput : reward={tp_result['mean_reward']:+.2f} | "
          f"rebuffer={tp_result['mean_rebuffer_s']:.2f}s | "
          f"quality={tp_result['mean_quality_kbps']:.0f}Kbps | "
          f"switches={tp_result['mean_switches']:.1f}")

# Aggregate across seeds
def agg(records, key, metric):
    return [r[metric] for r in records[key]]

print(f"\n{'='*60}")
print("AGGREGATED ACROSS 5 SEEDS (mean ± std of per-seed means)")
print(f"{'='*60}")

for metric, label in [
    ("mean_reward",      "Reward"),
    ("mean_rebuffer_s",  "Rebuffer (s)"),
    ("mean_quality_kbps","Quality (Kbps)"),
    ("mean_switches",    "Switches"),
]:
    ppo_vals = agg(records, "ppo", metric)
    tp_vals  = agg(records, "throughput", metric)
    print(
        f"{label:<16} | "
        f"PPO: {np.mean(ppo_vals):>8.2f} ± {np.std(ppo_vals):.2f} | "
        f"Throughput: {np.mean(tp_vals):>8.2f} ± {np.std(tp_vals):.2f}"
    )

print(f"{'='*60}")
"""











""" 
from stable_baselines3 import PPO

from rl_model.abr_env import ABREnv


env = ABREnv()

model = PPO.load(
    "ppo_abr_model"
)

obs, _ = env.reset()

for _ in range(20):

    action, _ = model.predict(
        obs,
        deterministic=True
    )

    obs, reward, done, trunc, _ = env.step(action)

    print(
        f"Action={action}, Reward={reward}"
    )

    if done or trunc:
        break
"""







"""
from services.trace_loader import TraceLoader

loader = TraceLoader()

print(
    "Number of traces:",
    len(loader.traces)
)

trace = loader.get_random_trace()

print(
    "Trace length:",
    len(trace)
)

print(
    trace[:5]
)
"""












""" 
# to test the roi complexity evaluation
regions = [

    {
        "name": "roi_1",
        "x": 0.267,
        "y": 0.11859485274511027,
        "w": 0.08,
        "h": 0.0975177304964539
    }

]


analyzer = ROIAnalyzer(
    regions
)

cap = cv2.VideoCapture(
    "media/test_video.mp4"
)


while True:

    ret, frame = cap.read()

    if not ret:
        break

    results = analyzer.analyze(
        frame
    )

    print(results)

cap.release()
"""





""" 
from app import app

# to test video segmentation
if __name__ == "__main__":
    with app.app_context():
        generate_dash_stream()
"""


        


"""
from services.roi_detector import detect_rois

rois = detect_rois("./media/test_video.mp4")

print(rois)
"""