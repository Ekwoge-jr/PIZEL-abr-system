# rl_model/abr_env.py  (IMPROVED VERSION)

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from collections import deque
from backend.services.trace_loader import TraceLoader


class ABREnv(gym.Env):
    """
    Pensieve-style ABR Environment — Improved Version.

    Key changes from previous version:
    1. Rebalanced reward coefficients to prevent
       risk-averse policy collapse (agent always choosing
       minimum bitrate to avoid rebuffer penalty).
    2. Wider reward clip range to allow good decisions
       to produce meaningfully positive rewards.
    3. Quality reward scaled up relative to penalties.
    4. Added explicit quality-of-experience bonus for
       high-quality delivery without rebuffering.
    """

    # ------------------------------------------------------------------
    # Constants
    # ------------------------------------------------------------------

    VIDEO_CHUNK_LEN_S   = 4.0
    BUFFER_MAX_S        = 60.0
    BUFFER_INIT_MIN_S   = 5.0
    BUFFER_INIT_MAX_S   = 20.0
    HISTORY_LEN         = 5
    MAX_CHUNKS          = 48

    BITRATES_BPS = [300_000, 800_000, 1_500_000]
    N_BITRATES   = len(BITRATES_BPS)

    MAX_THROUGHPUT_BPS  = 8_000_000.0
    MAX_DOWNLOAD_TIME_S = VIDEO_CHUNK_LEN_S * 4.0
    MIN_THROUGHPUT_BPS  = 50_000.0

    # ── Reward coefficients (KEY CHANGE) ─────────────────────────────
    # The previous version had REBUFFER_COEF=4.0 which was
    # too high relative to quality_reward, causing the agent
    # to always pick 300 Kbps (safest choice, least rebuffering).
    # These new values encourage quality-seeking behaviour.
    QUALITY_SCALE       = 2.5    # Multiplier on quality reward
    REBUFFER_COEF       = 3.0    # Reduced from 4.0 then to 2.5
    SMOOTH_COEF         = 0.4    # Reduced from 1.0 then to 0.5
    OVERSHOOT_COEF      = 0.3    # Reduced from 0.5
    REWARD_CLIP         = 30.0   # Widened from 20.0 then 50.0

    OBS_DIM = HISTORY_LEN + HISTORY_LEN + 1 + 1 + 1 + N_BITRATES  # = 16

    def __init__(self, trace_folder: str = "cooked_traces"):
        super().__init__()

        # Dynamically load the correct split
        self.loader = TraceLoader(trace_folder=trace_folder)

        self.observation_space = spaces.Box(
            low=np.zeros(self.OBS_DIM,  dtype=np.float32),
            high=np.ones(self.OBS_DIM,  dtype=np.float32),
            dtype=np.float32,
        )
        self.action_space = spaces.Discrete(self.N_BITRATES)

        self.current_trace         = None
        self.trace_index           = 0
        self.step_count            = 0
        self.buffer_s              = 0.0
        self.last_action           = 1
        self.chunks_sent           = 0
        self.throughput_history    = deque(
            [0.0] * self.HISTORY_LEN, maxlen=self.HISTORY_LEN
        )
        self.download_time_history = deque(
            [0.0] * self.HISTORY_LEN, maxlen=self.HISTORY_LEN
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_throughput_bps(self, index: int) -> float:
        raw = self.current_trace[
            min(index, len(self.current_trace) - 1)
        ][1]
        bps = float(raw) * 1_000_000.0
        return float(
            np.clip(bps, self.MIN_THROUGHPUT_BPS, self.MAX_THROUGHPUT_BPS * 2)
        )

    def _build_observation(self) -> np.ndarray:

        th_norm = [
            float(np.clip(t / self.MAX_THROUGHPUT_BPS, 0.0, 1.0))
            for t in self.throughput_history
        ]
        dl_norm = [
            float(np.clip(d / self.MAX_DOWNLOAD_TIME_S, 0.0, 1.0))
            for d in self.download_time_history
        ]
        buf_norm       = float(
            np.clip(self.buffer_s / self.BUFFER_MAX_S, 0.0, 1.0)
        )
        remaining_norm = float(
            np.clip(
                (self.MAX_CHUNKS - self.chunks_sent) / self.MAX_CHUNKS,
                0.0, 1.0
            )
        )
        last_br_norm   = float(
            np.clip(
                self.BITRATES_BPS[self.last_action] / self.BITRATES_BPS[-1],
                0.0, 1.0
            )
        )
        one_hot = np.zeros(self.N_BITRATES, dtype=np.float32)
        one_hot[self.last_action] = 1.0

        return np.array(
            th_norm + dl_norm +
            [buf_norm, remaining_norm, last_br_norm] +
            list(one_hot),
            dtype=np.float32,
        )

    # ------------------------------------------------------------------
    # Gym API
    # ------------------------------------------------------------------

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.current_trace = self.loader.get_random_trace()
        self.trace_index   = 0
        self.step_count    = 0
        self.chunks_sent   = 0
        self.last_action   = 1

        self.buffer_s = float(
            np.random.uniform(self.BUFFER_INIT_MIN_S, self.BUFFER_INIT_MAX_S)
        )

        first_tp = self._get_throughput_bps(0)
        self.throughput_history = deque(
            [first_tp] * self.HISTORY_LEN, maxlen=self.HISTORY_LEN
        )
        approx_dl = (
            self.BITRATES_BPS[1] * self.VIDEO_CHUNK_LEN_S
        ) / first_tp
        self.download_time_history = deque(
            [approx_dl] * self.HISTORY_LEN, maxlen=self.HISTORY_LEN
        )

        return self._build_observation(), {}

    def step(self, action: int):

        self.step_count  += 1
        self.chunks_sent += 1

        selected_bps     = self.BITRATES_BPS[int(action)]
        current_bps      = self.BITRATES_BPS[self.last_action]

        # Advance trace
        self.trace_index = min(
            self.trace_index + 1,
            len(self.current_trace) - 1
        )
        new_tp_bps = self._get_throughput_bps(self.trace_index)

        # Download simulation
        segment_bits  = selected_bps * self.VIDEO_CHUNK_LEN_S
        download_time = float(
            np.clip(segment_bits / new_tp_bps, 0.0, self.VIDEO_CHUNK_LEN_S * 4.0)
        )

        # Buffer update
        self.buffer_s = float(
            np.clip(
                self.buffer_s + self.VIDEO_CHUNK_LEN_S - download_time,
                0.0, self.BUFFER_MAX_S
            )
        )

        # Update histories
        self.throughput_history.append(new_tp_bps)
        self.download_time_history.append(download_time)

        # ── Reward ─────────────────────────────────────────────────

        # 1. Quality reward (scaled up to compete with penalties)
        quality_reward = (
            #np.log(selected_bps / self.BITRATES_BPS[0] + 1.0)
            #* self.QUALITY_SCALE

            #selected_bps / 300000
            (selected_bps / self.BITRATES_BPS[0]) * 0.6

        )

        # 2. Rebuffering penalty
        rebuffer_time    = max(0.0, download_time - self.VIDEO_CHUNK_LEN_S)
        rebuffer_penalty = rebuffer_time * self.REBUFFER_COEF

        # 3. Smoothness penalty
        smooth_penalty = (
            abs(selected_bps - current_bps) / 1_000_000.0
        ) * self.SMOOTH_COEF

        # 4. Overshoot penalty
        overshoot_penalty = 0.0
        if selected_bps > new_tp_bps:
            overshoot_penalty = (
                (selected_bps - new_tp_bps) / 1_000_000.0
            ) * self.OVERSHOOT_COEF

        # 5. Buffer health bonus (NEW)
        # Rewards the agent for maintaining a healthy buffer level.
        # This encourages proactive quality management rather than
        # purely reactive rebuffering avoidance.
        buffer_bonus = 0.0
        if self.buffer_s > 10.0 and rebuffer_time == 0.0:
            buffer_bonus = 0.5    # was 0.3, now 0.5 

        raw_reward = (
            quality_reward
            - rebuffer_penalty
            - smooth_penalty
            - overshoot_penalty
            + buffer_bonus
        )

        reward = float(
            np.clip(raw_reward, -self.REWARD_CLIP, self.REWARD_CLIP)
        )

        self.last_action = int(action)

        terminated = (
            self.trace_index >= len(self.current_trace) - 1
            or self.chunks_sent >= self.MAX_CHUNKS
        )
        truncated = self.step_count >= 500

        info = {
            "throughput_mbps"   : new_tp_bps / 1e6,
            "buffer_s"          : self.buffer_s,
            "download_time_s"   : download_time,
            "rebuffer_time_s"   : rebuffer_time,
            "selected_kbps"     : selected_bps / 1000,
            "quality_reward"    : quality_reward,
            "rebuffer_penalty"  : rebuffer_penalty,
            "smooth_penalty"    : smooth_penalty,
            "buffer_bonus"      : buffer_bonus,
        }

        return self._build_observation(), reward, terminated, truncated, info