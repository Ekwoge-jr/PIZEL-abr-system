"""
# merge_onnx.py

import onnx

model = onnx.load(
    "ppo_abr.onnx",
    load_external_data=True
)

onnx.save_model(
    model,
    "ppo_abr_single.onnx",
    save_as_external_data=False
)

print("done")
"""


import torch
import torch.nn as nn
from stable_baselines3 import PPO


model = PPO.load(
    "checkpoints/best/best_model.zip"
)


class PPOWrapper(nn.Module):

    def __init__(self, policy):
        super().__init__()
        self.policy = policy

    def forward(self, x):

        latent_pi, _ = self.policy.mlp_extractor(x)

        logits = self.policy.action_net(latent_pi)

        return logits


wrapper = PPOWrapper(model.policy)

# Switch to eval mode before export (important!)
wrapper.eval()

dummy = torch.randn(1,16)

torch.onnx.export(
    wrapper,
    dummy,
    "ppo_abr.onnx",
    input_names=["state"],
    output_names=["logits"],
    export_params=True,
    keep_initializers_as_inputs=False,
    opset_version=18
)

print("Done")